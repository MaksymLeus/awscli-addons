import click
from os import environ
from awscli_addons.utils.aws_config import AWSConfig

DEFAULT_ASSUME_PROFILE_NAME = "assume_role"

def assume(role_arn: str, session_name: str = "AWSCLI-Session", profile_name: str = None):
    from boto3 import Session
    from botocore.exceptions import ClientError

    # 1. Initialize AWSConfig objects
    # source_cfg: Where we get the identity to assume the role
    # target_cfg: Where we save the temporary role keys
    source_cfg = AWSConfig(profile_name)
    target_cfg = AWSConfig(DEFAULT_ASSUME_PROFILE_NAME)

    try:
        click.echo(f"🔄 Assuming role {click.style(role_arn, fg='yellow')}...")
        
        # 2. Create the boto3 session using the resolved source profile
        session = Session(profile_name=source_cfg.profile)
        sts = session.client("sts")

        # 3. Call AWS STS
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        
        creds = response["Credentials"]

        # 4. Save credentials using our Class
        target_cfg.update_credentials(
            access_key=creds["AccessKeyId"],
            secret_key=creds["SecretAccessKey"],
            token=creds["SessionToken"]
        )

        source_region = source_cfg._conf.get(source_cfg.conf_section, "region", fallback=None)
        if source_region:
            target_cfg.update_config(region=source_region)

        # 5. Commit to disk
        target_cfg.save()

        click.secho(f"\n✅ Successfully assumed role!", fg="green", bold=True)
        click.echo(f"Account: {role_arn.split(':')[4]}")
        click.echo(f"To use:  export AWS_PROFILE={DEFAULT_ASSUME_PROFILE_NAME}")

    except ClientError as e:
        click.secho(f"❌ AWS Error: {e}", fg="red")
    except Exception as e:
        click.secho(f"❌ Error: {str(e)}", fg="red")