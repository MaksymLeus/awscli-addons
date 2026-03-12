import boto3
import click
from botocore.exceptions import ProfileNotFound, NoCredentialsError
from awscli_addons.utils.aws_config import AWSConfig

def show(profile, export=False, reveal=False):
    try:
        # Initialize your class (handles AWS_PROFILE env var logic internally)
        aws = AWSConfig(profile)
        
        # Use the resolved profile from the class
        active_profile = aws.profile
        
        session = boto3.Session(profile_name=active_profile)
        credentials = session.get_credentials()

        if not credentials:
            click.secho(f"❌ No credentials found for profile '{active_profile}'.", fg="red")
            return

        # Frozen credentials ensure we get the actual keys from SSO/Vault/Env
        current_creds = credentials.get_frozen_credentials()
        
        access_key = current_creds.access_key
        secret_key = current_creds.secret_key
        token = current_creds.token
        region = session.region_name

        if export:
            # shell-friendly output
            click.echo(f"export AWS_ACCESS_KEY_ID={access_key}")
            click.echo(f"export AWS_SECRET_ACCESS_KEY={secret_key}")
            if token:
                click.echo(f"export AWS_SESSION_TOKEN={token}")
            if region:
                click.echo(f"export AWS_DEFAULT_REGION={region}")
        else:
            # Human-friendly output
            click.secho(f"🔑 AWS Context: {active_profile}", fg="cyan", bold=True)
            
            # Optional: Add Account ID/Identity check using STS
            try:
                sts = session.client("sts")
                identity = sts.get_caller_identity()
                click.echo(f"Account:           {identity['Account']}")
                click.echo(f"ARN:               {identity['Arn']}")
            except:
                click.echo("Account:           [Unable to verify identity]")

            click.echo(f"Region:            {region or 'Not Set'}")
            click.echo(f"Access Key ID:     {access_key}")
            
            if reveal:
                click.echo(f"Secret Access Key: {secret_key}")
            else:
                masked_secret = f"{secret_key[:4]}...{secret_key[-4:]}"
                click.echo(f"Secret Access Key: {masked_secret} (use --reveal to unmask)")

            if token:
                status = click.style("Temporary Session Active", fg="green")
                click.echo(f"Session Token:     [{status}]")
            
    except ProfileNotFound:
        click.secho(f"❌ Profile '{profile}' not found in your AWS config.", fg="red")
    except NoCredentialsError:
        click.secho("❌ Unable to locate credentials. Try running 'aws-addons configure'.", fg="red")
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg="red")