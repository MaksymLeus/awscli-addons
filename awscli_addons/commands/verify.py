import click
from os import environ
from shutil import which
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

from awscli_addons.utils.aws_config import AWSConfig

def check_aws_cli():
    """Checks if the actual aws-cli binary is installed."""
    if which("aws") is None:
        click.secho("⚠️  AWS CLI binary not found in PATH. Some features may not work.", fg="yellow")
    else:
        click.secho("✅ AWS CLI binary found in PATH", fg="green")

def check_aws_setup():
    """Initializes the .aws directory structure using the class logic."""
    # We create a dummy instance just to trigger directory creation/check
    aws = AWSConfig("default")
    aws.save() # This ensures folders and files exist with correct permissions
    click.secho(f"✅ AWS config directory verified: {aws.aws_dir}", fg="green")

def run_verify(skip_interactive: bool = False):
    click.secho("=== 🔍 Verifying AWS Environment ===", bold=True, fg="cyan")
    
    # 1. System Checks
    check_aws_cli()
    check_aws_setup()

    # 2. Profile Selection
    default_p = environ.get("AWS_PROFILE", "default")
    if not skip_interactive:
        profile_name = click.prompt("Profile to verify", default=default_p)
    else:
        profile_name = default_p

    # Load the Profile using our Class
    aws = AWSConfig(profile_name)
    is_valid = False

    # 3. Validation Logic
    if aws.exists():
        click.echo(f"ℹ️  Profile '{profile_name}' found in credentials file.")
        # Check if keys are actually present in the parser
        ak = aws._creds.get(profile_name, 'aws_access_key_id', fallback=None)
        sk = aws._creds.get(profile_name, 'aws_secret_access_key', fallback=None)
        st = aws._creds.get(profile_name, 'aws_session_token', fallback=None)
        
        if ak and sk:
            click.echo("🔗 Testing connectivity...")
            is_valid = aws.verify_credentials_live(ak, sk, st)
    else:
        # Fallback to Environment Variables
        click.echo(f"ℹ️  Profile '{profile_name}' not in file. Checking Environment Variables...")
        env_ak = environ.get("AWS_ACCESS_KEY_ID")
        env_sk = environ.get("AWS_SECRET_ACCESS_KEY")
        env_st = environ.get("AWS_SESSION_TOKEN")

        if env_ak and env_sk:
            is_valid = aws.verify_credentials_live(env_ak, env_sk, env_st)

    # 4. Interactive Fix
    if not is_valid and not skip_interactive:
        if click.confirm(f"\nWould you like to configure credentials for '{profile_name}' now?"):
            new_ak = click.prompt("AWS Access Key ID", value_proc=aws.validate_access_key)
            new_sk = click.prompt("AWS Secret Access Key", hide_input=True)

            if aws.verify_credentials_live(new_ak, new_sk):
                aws.update_credentials(access_key=new_ak, secret_key=new_sk)
                aws.save()
            else:
                click.secho("❌ Aborting save due to invalid credentials.", fg="red")

    click.secho("\n=== ✨ Verification Complete ===", bold=True, fg="cyan")