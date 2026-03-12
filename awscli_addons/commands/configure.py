import os
import configparser
import click

from awscli_addons.utils.aws_config import AWSConfig

def run_configure(profile_name: str = None):
    # Initialize the class (handles AWS_PROFILE env var logic internally)
    aws = AWSConfig(profile_name)
    
    if not aws.exists():
        click.secho(f"✨ Creating new profile: {aws.profile}", fg="green")
    else:
        click.secho(f"🔧 Updating profile: {aws.profile}", fg="cyan", bold=True)

    # Use the class's internal parsers
    creds = aws._creds
    conf = aws._conf
    
    # Use the helper property from your class for the config section naming
    conf_sect = aws.conf_section 

    # Helper to get existing value for the prompt
    def get_old(parser, section, key, hide=False):
        if parser.has_option(section, key):
            val = parser.get(section, key)
            if hide and val:
                return f" [{'' '*' * 8 }] "
            return f" [{val}] "
        return " "

    # 1. Credentials (using the profile name directly)
    access_key = click.prompt(
        f"AWS Access Key ID{get_old(creds, aws.profile, 'aws_access_key_id')}", 
        default=creds.get(aws.profile, 'aws_access_key_id', fallback=""), 
        show_default=False,
        value_proc=aws.validate_access_key
    )
    
    secret_key = click.prompt(
        f"AWS Secret Access Key{get_old(creds, aws.profile, 'aws_secret_access_key', hide=True)}", 
        default=creds.get(aws.profile, 'aws_secret_access_key', fallback=""), 
        show_default=False, 
        hide_input=True
    )
    # 2. Config (using the special conf_sect: e.g., 'profile dev')
    region = click.prompt(
        f"Default region name{get_old(conf, conf_sect, 'region')}", 
        default=conf.get(conf_sect, 'region', fallback="us-east-1"), 
        show_default=False,
        value_proc=aws.validate_region
    )
    
    output = click.prompt(
        f"Default output format{get_old(conf, conf_sect, 'output')}", 
        default=conf.get(conf_sect, 'output', fallback="json"), 
        type=click.Choice(['json', 'text', 'table', 'yaml']), 
        show_default=False
    )

    # 3. Update & Save via the Class methods
    aws.update_credentials(access_key=access_key, secret_key=secret_key)
    aws.update_config(region=region, output=output)
    aws.save()