import sys, os
import shutil
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

from awscli_addons.custom import Credentials_save, Config_read



def check_aws_cli():
    if shutil.which("aws") is None:
        print("⚠️ AWS CLI not found in PATH. Some fallback features may not work.")
    else:
        print("✅ AWS CLI found in PATH")

def check_aws_config_dirs():
    aws_dir = Path.home() / ".aws"
    aws_dir.mkdir(exist_ok=True)
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    if not credentials_file.exists():
        credentials_file.touch()
        print(f"✅ Created empty AWS credentials file at {credentials_file}")
    else:
        print(f"✅ AWS credentials file exists: {credentials_file}")
    if not config_file.exists():
        config_file.touch()
        print(f"✅ Created empty AWS config file at {config_file}")
    else:
        print(f"✅ AWS config file exists: {config_file}")

def verify_profile(profile="default"):
    """
    Check profiles in ~/.aws/credentials
    Returns a dict with profile -> True/False if credentials exist
    """
    print(f"ℹ️ Current AWS profile: '{profile}'")
    
    choice = input(f"Would you like to change the active profile? [y/N]: ").strip().lower()
    if choice == "y":
        profile = input("Enter the profile name you want to use: ").strip()
        print(f"ℹ️ Active profile set to: '{profile}'")

    credentials_file = Path.home() / ".aws" / "credentials"
    config = Config_read(credentials_file)

    profile_status = {}

    if profile not in config.sections():
        print(f"⚠️ Profile '{profile}' not found in AWS credentials")
        print(f"ℹ️ Adding empty profile '{profile}' to credentials file for future use")
        # Add empty profile to credentials file to avoid error from boto3 when checking connectivity later, will be overwritten with real creds if user choose to set them
        Credentials_save(creds=None, profile_name=profile, output=False)
        profile_status[profile] = False
    else:
      # Check if keys are actually set
      keys_missing = any(not config[profile].get(k) for k in ["aws_access_key_id", "aws_secret_access_key"])
      if keys_missing:
          print(f"⚠️ Profile '{profile}' exists but credentials are not set")
          profile_status[profile] = False
      else:
          print(f"✅ Profile '{profile}' exists with credentials set")
          profile_status[profile] = True
    
    # Check environment variables ONLY if credentials in file are missing 
    if not profile_status[profile]:
        print("ℹ️ Checking environment variables for this profile...")

        # Check environment variables
        aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        aws_session_token = os.environ.get("AWS_SESSION_TOKEN")

        
        missing_env = []
        if not aws_access_key:
            missing_env.append("AWS_ACCESS_KEY_ID")
        if not aws_secret_key:
            missing_env.append("AWS_SECRET_ACCESS_KEY")
        # session token is optional if long-term credentials, but warn
        if not aws_session_token:
            print("ℹ️ AWS_SESSION_TOKEN not set (long-term credentials)")

        if missing_env:
            print(f"⚠️ Environment variables missing for active profile: {', '.join(missing_env)}")

        else:
            print("✅ All required environment variables for active profile are set")
            profile_status[profile] = True

    return profile_status

def verify_credentials(key, secret):
    # Create a temporary session with the provided keys
    session = boto3.Session(
        aws_access_key_id=key,
        aws_secret_access_key=secret
    )
    
    # Use the STS (Security Token Service) client to verify identity
    sts = session.client('sts')
    
    try:
        # This call always succeeds if credentials are valid, regardless of permissions
        identity = sts.get_caller_identity()
        print(f"✅ Success! Authenticated as: {identity['Arn']}")
        return True
    except ClientError as e:
        # Catch common authentication errors
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidClientTokenId':
            print("❌ Error: Invalid Access Key ID.")
        elif error_code == 'SignatureDoesNotMatch':
            print("❌ Error: Invalid Secret Access Key (Signature mismatch).")
        else:
            print(f"❌ Error: {e}")
        return False

def interactive_configuration(profile_status):
    """
    Ask user to add profile interactively
    """
    for profile, ok in profile_status.items():
        if not ok:
            choice = input(f"Would you like to set credentials for profile '{profile}'? [y/N]: ").strip().lower()

            if choice == "y":
              user_input = input("Enter AWS Access Key ID: ").strip()
              user_secret = input("Enter AWS Secret Access Key: ").strip()
              if not user_input or not user_secret:
                  print("❌ Access Key ID and Secret Access Key cannot be empty. Skipping.")
                  exit(1)
              if not verify_credentials(user_input, user_secret):
                  print("❌ Invalid credentials. Please try again.")
                  exit(1)

              try:
                  creds = {
                      "AccessKeyId": user_input,
                      "SecretAccessKey": user_secret,
                  }
                  Credentials_save(creds=creds, profile_name=profile)
              except Exception as e:
                  print(f"❌ Failed to run save credentials for profile '{profile}': {e}")
            else:
              print(f"Skipping setting credentials for profile '{profile}'")


def check_aws_connectivity():
    # check creds file and with this list check connectivity for each profile, if creds missing skip

    try:
        session = boto3.Session(profile_name=profile)
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print(f"✅ AWS connectivity OK for profile '{profile}'")
        print(f"    Account: {identity['Account']}, ARN: {identity['Arn']}")
    except ClientError as e:
        print(f"❌ AWS connectivity failed for profile '{profile}': {e}")
    except Exception as e:
        print(f"❌ Unexpected error checking AWS connectivity: {e}")

def run_verify(skip_interactive: bool = False):
    print("=== Verifying environment ===")
    check_aws_cli()
    check_aws_config_dirs()

    # Check profiles and capture their status
    profile_status = verify_profile(os.environ.get("AWS_PROFILE", "default"))

    if skip_interactive:
        print("⚠️ Some profiles are missing or incomplete. Run with --fix to interactively fix them.")
    else:
        interactive_configuration(profile_status)

    # Check connectivity for each profile in the credentials file
    # check_aws_connectivity()

    print("=== Verification complete ===")
