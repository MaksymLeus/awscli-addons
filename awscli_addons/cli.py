#!/usr/bin/env python3
import click
from awscli_addons import mfa, assume_role, whoami, myip, verify

@click.group()
def cli():
    """AWS CLI Addons - Enhance your AWS CLI experience with additional commands for MFA, role assumption, identity verification, and more."""
    pass

@cli.command("verify")
@click.option("-si","--skip-interactive", default=False, help="Skip interactive prompts so you don't need input anything")
def verify_command(skip_interactive):
    """Verify environment, AWS config, and connectivity"""
    verify.run_verify(skip_interactive)

@cli.command("mfa")
@click.option("--profile", default=None, help="Base AWS profile")
@click.option("--mfa-code", prompt=True, hide_input=True, help="6-digit MFA token")
def mfa_command(profile, mfa_code):
    """Generate temporary AWS credentials using MFA"""
    mfa.create_session(profile, mfa_code)


@cli.command("assume-role")
@click.option("--role-arn", prompt=True, help="IAM Role ARN to assume")
@click.option("--session-name", default="AWSCLI-Session", help="Role session name")
@click.option("--profile", default=None, help="Base AWS profile")
def assume_role_command(role_arn, session_name, profile):
    """Assume an AWS IAM role"""
    assume_role.assume(role_arn, session_name, profile)


@cli.command("whoami")
@click.option("--profile", default=None, help="AWS profile to query")
def whoami_command(profile):
    """Show AWS identity (sts get-caller-identity)"""
    whoami.show(profile)


@cli.command("myip")
def myip_command():
    """Show your public IP"""
    myip.show()


if __name__ == "__main__":
    cli()
