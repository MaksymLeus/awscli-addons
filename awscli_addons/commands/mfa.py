from os import environ
import click
from awscli_addons.utils.aws_config import AWSConfig

DEFAULT_MFA_PROFILE_PREFIX = "mfa"
DEFAULT_SESSION_DURATION = 43200  # 12 hours
def validate_mfa_token(ctx, param, value):
    """
    Reusable Click callback to validate 6-digit MFA tokens.
    """
    if value:
        # Remove any spaces or dashes users might accidentally include
        clean_value = value.replace(" ", "").replace("-", "")
        if not clean_value.isdigit() or len(clean_value) != 6:
            raise click.BadParameter("MFA code must be exactly 6 digits (e.g., 123456).")
        return clean_value
    return value

    
def create_mfa_session(profile_name: str = None, mfa_token: str = None, duration: int = DEFAULT_SESSION_DURATION):
    from boto3 import Session
    from botocore.exceptions import ClientError, ProfileNotFound

    # 1. Initialize AWSConfig for the source profile
    # This automatically handles the AWS_PROFILE environment variable if profile_name is None
    source_cfg = AWSConfig(profile_name)
    
    # 2. Define and initialize the target MFA profile
    target_profile_name = f"{DEFAULT_MFA_PROFILE_PREFIX}_{source_cfg.profile}"
    target_cfg = AWSConfig(target_profile_name)

    try:
        session = Session(profile_name=source_cfg.profile)
        iam = session.client("iam")
        sts = session.client("sts")

        # Bonus: Check if we are already using an MFA profile
        if source_cfg.profile.startswith(DEFAULT_MFA_PROFILE_PREFIX):
            click.secho(f"⚠️  Note: You are already using an MFA profile ({source_cfg.profile}).", fg="yellow")

        # Get MFA Serial
        user_data = iam.get_user()["User"]
        mfa_devices = iam.list_mfa_devices(UserName=user_data["UserName"])["MFADevices"]
        
        if not mfa_devices:
            click.secho("❌ No MFA devices found for this user.", fg="red")
            return

        mfa_serial = mfa_devices[0]["SerialNumber"]

        # Prompt for token if not provided
        # if not mfa_token:
        #     mfa_token = click.prompt("Enter MFA Code", type=str)

        if not mfa_token:
            mfa_token = click.prompt(
                click.style("Enter 6-digit MFA Code", fg="yellow"),
                type=str,
                value_proc=validate_mfa_token  # This prevents the ParamValidationError
            )
        # 3. Get Session Token
        creds = sts.get_session_token(
            SerialNumber=mfa_serial,
            TokenCode=mfa_token,
            DurationSeconds=duration
        )["Credentials"]

        # 4. Save using our Class
        target_cfg.update_credentials(
            access_key=creds["AccessKeyId"],
            secret_key=creds["SecretAccessKey"],
            token=creds["SessionToken"]
        )
        
        # 💡 Sync the region from source to target
        source_region = source_cfg._conf.get(source_cfg.conf_section, "region", fallback=None)
        target_cfg.update_config(region=source_region)
        
        target_cfg.save()

        click.secho(f"\n🚀 MFA Session Active!", fg="green", bold=True)
        click.echo(f"Profile: {click.style(target_profile_name, bold=True)}")
        click.echo(f"Expires: {creds['Expiration'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
        click.echo(f"\nTo use: {click.style(f'export AWS_PROFILE={target_profile_name}', fg='cyan')}")

    except ClientError as e:
        click.secho(f"❌ AWS Error: {e}", fg="red")