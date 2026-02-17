import boto3
from botocore.exceptions import ClientError

from awscli_addons.custom import Credentials_save

DEFAULT_ASSUME_PROFILE_NAME = "assume_role"


def assume(role_arn: str, session_name: str = "AWSCLI-Session", profile_name: str = None):
    session = boto3.Session(profile_name=profile_name)
    sts = session.client("sts")
    try:
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        creds = response["Credentials"]
        Credentials_save(creds, DEFAULT_ASSUME_PROFILE_NAME)
    except ClientError as e:
        print(f"❌ AWS Error: {e}")
