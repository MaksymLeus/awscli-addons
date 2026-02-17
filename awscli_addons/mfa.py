import boto3
from botocore.exceptions import ClientError

from awscli_addons.custom import Credentials_save

DEFAULT_MFA_PROFILE_PREFIX = "mfa"
DEFAULT_SESSION_DURATION = 43200  # 12 hours



def create_session(profile_name: str = "default", mfa_token: str = None, duration: int = DEFAULT_SESSION_DURATION):
    session = boto3.Session(profile_name=profile_name)
    iam = session.client("iam")
    sts = session.client("sts")

    try:
        username = iam.get_user()["User"]["UserName"]
        mfa_devices = iam.list_mfa_devices(UserName=username)["MFADevices"]
        if not mfa_devices:
            raise Exception("No MFA devices found for this user")
        mfa_serial = mfa_devices[0]["SerialNumber"]

        creds = sts.get_session_token(
            SerialNumber=mfa_serial,
            TokenCode=mfa_token,
            DurationSeconds=duration
        )["Credentials"]

        Credentials_save(creds, f"{DEFAULT_MFA_PROFILE_PREFIX}_{profile_name}")
    except ClientError as e:
        print(f"❌ AWS Error: {e}")
