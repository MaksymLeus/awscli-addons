#!/usr/bin/env python3
import click

# Define the custom help flags
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

__version__ = "882ae35"

class AliasedGroup(click.Group):
    # This is the dictionary of your shortcuts
    MAP = {
        'sc': 'show-creds',
        'conf': 'configure',
        'ver':  'verify',
        'ar': 'assume-role',
        'wi': 'whoami',
        'up': 'upgrade'
    }

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        if cmd_name in self.MAP:
            return click.Group.get_command(self, ctx, self.MAP[cmd_name])
        return None

    def format_commands(self, ctx, formatter):
        """Automatically add (alias: xx) to the help list"""
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None or cmd.hidden:
                continue
            
            # Find if this command has an alias
            aliases = [k for k, v in self.MAP.items() if v == subcommand]
            alias_str = f" (alias: {', '.join(aliases)})" if aliases else ""
            
            commands.append((subcommand + alias_str, cmd.get_short_help_str()))

        if commands:
            with formatter.section("Commands"):
                formatter.write_dl(commands)

@click.group(context_settings=CONTEXT_SETTINGS, cls=AliasedGroup)
@click.version_option(__version__, '--version', '-v', 
    prog_name="awscli-addons",
    message="%(version)s"
)

def cli():
    """AWS CLI Addons - Enhance your AWS CLI experience."""
    pass

@cli.command("verify")
@click.option("-si","--skip-interactive", default=False, help="Skip interactive prompts so you don't need input anything")
def verify_command(skip_interactive):
    """Verify environment, AWS config, and connectivity"""
    from awscli_addons.commands.verify import run_verify
    run_verify(skip_interactive)

from awscli_addons.commands.mfa import validate_mfa_token
@cli.command("mfa")
@click.option("-p", "--profile", default=None, help="Base AWS profile")
@click.option(
    "-mc", 
    "--mfa-code", 
    prompt="Enter MFA code", 
    hide_input=False, 
    help="6-digit MFA token",
    callback=validate_mfa_token  # This is the magic line
)
def mfa_command(profile, mfa_code):
    """Generate temporary AWS credentials using MFA"""
    from awscli_addons.commands.mfa import create_mfa_session
    create_mfa_session(profile, mfa_code)

@cli.command("show-creds", short_help="Show AWS credentials [alias: sc]")
@click.option("-p", "--profile", default=None, help="AWS profile to query")
@click.option("-ex", "--export", is_flag=True, help="Output as shell export commands")
@click.option("-r", "--reveal", is_flag=True, help="Reveal the full Secret Access Key in the terminal output")
def show_creds_command(profile, export, reveal):
    """Show AWS credentials for the current profile"""
    from awscli_addons.commands.show_creds import show
    show(profile, export, reveal)

@cli.command("configure")
@click.option("-p", "--profile", default=None, help="AWS profile to configure")
def configure_command(profile):
    """Interactively configure AWS credentials and settings. Alias: conf"""
    from awscli_addons.commands.configure import run_configure
    run_configure(profile)

@cli.command("assume-role")
@click.option("--role-arn", prompt=True, help="IAM Role ARN to assume")
@click.option("--session-name", default="AWSCLI-Session", help="Role session name")
@click.option("--profile", default=None, help="Base AWS profile")
def assume_role_command(role_arn, session_name, profile):
    """Assume an AWS IAM role"""
    from awscli_addons.commands.assume_role import assume
    assume(role_arn, session_name, profile)


@cli.command("whoami")
@click.option("-p", "--profile", default=None, help="AWS profile to query")
def whoami_command(profile):
    """Show AWS identity (sts get-caller-identity)"""
    from awscli_addons.commands.whoami import show_identity
    show_identity(profile)

@cli.command("myip")
def myip_command():
    """Show your public IP"""
    from awscli_addons.commands.myip import show
    show()

@cli.command("upgrade")
@click.option("-f", "--force", is_flag=True, help="Force upgrade even if versions match")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
def upgrade_command(force, yes):
    """Upgrade the app to the latest version [alias: up]"""
    # 1. Check for manual confirmation
    if not yes:
        if not click.confirm("🚀 This will check for updates and replace the current app. Continue?"):
            click.secho("Upgrade aborted.", fg="yellow")
            return

    # 2. Proceed with the logic
    from awscli_addons.commands.upgrade import run_upgrade
    run_upgrade(force=force)

@cli.group()
def ecr():
    """Generate AWS ECR commands for terminal use."""
    pass

@ecr.command(name="login")
@click.option("-p", "--profile", help="AWS profile name")
def ecr_login_command(profile):
    """Generate Docker login command for ECR Private."""
    from awscli_addons.commands.ecr import generate_login
    generate_login(profile)

@ecr.command(name="login-public")
@click.option("-p", "--profile", help="AWS profile name")
def ecr_login_public_command(profile):
    """Generate Docker login command for ECR Public."""
    from awscli_addons.commands.ecr import generate_login_public
    generate_login_public(profile)

@ecr.command(name="login-helm")
@click.option("-p", "--profile", help="AWS profile name")
def ecr_login_helm_command(profile):
    """Generate Helm login command for ECR."""
    from awscli_addons.commands.ecr import generate_login_helm
    generate_login_helm(profile)

@ecr.command(name="repo-list")
@click.option("-p", "--profile", help="AWS profile name")
def ecr_generate_repository_list(profile):
    """Generate ECR repository list  command for ECR."""
    from awscli_addons.commands.ecr import generate_list
    generate_list(profile)

@ecr.command(name="purge")
@click.argument("repo_name")
@click.option("-p", "--profile", help="AWS profile")
def ecr_purge_repository(repo_name, profile):
    """Generate a command to delete all UNTAGGED images (saves money)."""
    from awscli_addons.commands.ecr import generate_purge
    generate_purge(repo_name, profile)


if __name__ == "__main__":
    cli()
