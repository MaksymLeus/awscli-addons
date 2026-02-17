import boto3
from botocore.exceptions import ClientError

def show(profile_name: str = None):
    session = boto3.Session(profile_name=profile_name)
    sts = session.client("sts")
    try:
        identity = sts.get_caller_identity()
        print("AWS Identity:")
        print(f"  Account: {identity['Account']}")
        print(f"  UserId: {identity['UserId']}")
        print(f"  ARN: {identity['Arn']}")
    except ClientError as e:
        print(f"❌ AWS Error: {e}")
