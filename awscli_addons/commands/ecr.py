import click
from awscli_addons.utils.aws_config import AWSConfig

def get_ecr_context(profile_name):
    """Helper to resolve metadata using AWSConfig and STS."""
    aws = AWSConfig(profile_name)
    from boto3 import Session
    
    # We need a live session just to grab the Account ID
    session = Session(profile_name=aws.profile)
    sts = session.client("sts")
    
    account_id = sts.get_caller_identity()["Account"]
    region = aws._conf.get(aws.conf_section, "region", fallback="us-east-1")
    
    return aws.profile, account_id, region

def generate_login(profile):
    """Generate Docker login command for ECR Private."""
    p_name, acc_id, region = get_ecr_context(profile)
    registry = f"{acc_id}.dkr.ecr.{region}.amazonaws.com"
    
    cmd = (
        f"aws ecr get-login-password --region {region} --profile {p_name} | "
        f"docker login --username AWS --password-stdin {registry}"
    )
    
    click.secho(f"# ECR Private Login for {p_name}:", fg="cyan", bold=True)
    click.echo(cmd)

def generate_login_public(profile):
    """Generate Docker login command for ECR Public."""
    p_name, _, _ = get_ecr_context(profile)
    
    # ECR Public authentication must use us-east-1
    cmd = (
        f"aws ecr-public get-login-password --region us-east-1 --profile {p_name} | "
        f"docker login --username AWS --password-stdin public.ecr.aws"
    )
    
    click.secho("# ECR Public Login (Global):", fg="cyan", bold=True)
    click.echo(cmd)

def generate_login_helm(profile):
    """Generate Helm login command for ECR."""
    p_name, acc_id, region = get_ecr_context(profile)
    registry = f"{acc_id}.dkr.ecr.{region}.amazonaws.com"
    
    cmd = (
        f"aws ecr get-login-password --region {region} --profile {p_name} | "
        f"helm registry login --username AWS --password-stdin {registry}"
    )
    
    click.secho(f"# Helm ECR Login for {p_name}:", fg="magenta", bold=True)
    click.echo(cmd)

def generate_list(profile):
    """Generate ECR repository list command."""
    p_name, _, region = get_ecr_context(profile)
    
    cmd = (
        f"aws ecr describe-repositories --profile {p_name} --region {region} "
        f"--query 'repositories[].repositoryUri' --output table"
    )
    
    click.secho(f"# List Repositories in {region}:", fg="cyan", bold=True)
    click.echo(cmd)

def generate_purge(repo_name, profile):
    """Generate a command to delete all UNTAGGED images (saves money)."""
    p_name, _, region = get_ecr_context(profile)
    
    cmd = (
        f"aws ecr batch-delete-image --profile {p_name} --region {region} "
        f"--repository-name {repo_name} --image-ids \"$(aws ecr list-images "
        f"--profile {p_name} --region {region} --repository-name {repo_name} "
        f"--filter 'tagStatus=UNTAGGED' --query 'imageIds[*]' --output json)\""
    )
    
    click.secho(f"# 🧹 Purge untagged images in {repo_name}:", fg="yellow", bold=True)
    click.echo(cmd)