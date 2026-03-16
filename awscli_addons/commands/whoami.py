import click
from botocore.exceptions import ClientError, ProfileNotFound
from awscli_addons.utils.aws_config import AWSConfig

def show_identity(profile_name: str = None):
    """Fetches and displays the current AWS identity (WhoAmI)."""
    from boto3 import Session

    # 1. Resolve profile through our central class
    try:
        aws = AWSConfig(profile_name)
    except Exception as e:
        click.secho(f"❌ Initialization Error: {e}", fg="red")
        return

    try:
        # 2. Initialize session with the resolved profile
        session = Session(profile_name=aws.profile)
        sts = session.client("sts")

        click.echo(f"🔍 Checking identity for profile: {click.style(aws.profile, fg='cyan', bold=True)}")
        
        # 3. Call STS
        identity = sts.get_caller_identity()
        
        # 4. Pretty print results
        click.secho("\n✨ AWS Identity Found:", fg="green", bold=True)
        click.echo(f"  {click.style('Account:', bold=True):<12} {identity['Account']}")
        click.echo(f"  {click.style('UserId:', bold=True):<12} {identity['UserId']}")
        click.echo(f"  {click.style('ARN:', bold=True):<12} {identity['Arn']}")

        # Bonus: If it's an assumed role, let the user know
        if ":assumed-role/" in identity['Arn']:
            click.secho("\n💡 Note: You are currently using temporary credentials (Assumed Role).", fg="yellow", italic=True)

    except ProfileNotFound:
        click.secho(f"❌ Error: The profile '{aws.profile}' was not found in your config files.", fg="red")
    except ClientError as e:
        click.secho(f"❌ AWS Error: {e}", fg="red")
    except Exception as e:
        click.secho(f"❌ Unexpected Error: {str(e)}", fg="red")