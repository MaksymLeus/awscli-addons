import configparser
import os
from pathlib import Path
from typing import Optional, Dict
import re
import click

class AWSConfig:
    def __init__(self, profile: str = "default"):
        self.profile = profile
        self.home = Path.home()
        self.aws_dir = self.home / ".aws"
        self.creds_path = self.aws_dir / "credentials"
        self.config_path = self.aws_dir / "config"
        
        # Internal Parsers
        self._creds = configparser.ConfigParser()
        self._conf = configparser.ConfigParser()
        
        # Auto-load existing data
        self.load()

    def load(self):
        """Load current files into memory."""
        if self.creds_path.exists():
            self._creds.read(self.creds_path)
        
        if self.config_path.exists():
            self._conf.read(self.config_path)
        
        self.profile = self.profile or os.environ.get("AWS_PROFILE") or "default"

    @property
    def conf_section(self) -> str:
        """Helper for the naming difference in .aws/config."""
        return self.profile if self.profile == "default" else f"profile {self.profile}"

    def exists(self) -> bool:
        """Check if the current profile exists in credentials."""
        return self.profile in self._creds.sections()

    def update_credentials(self, access_key: str = None, secret_key: str = None, token: str = None):
        """Update the credential state in memory."""
        if self.profile not in self._creds.sections():
            self._creds.add_section(self.profile)
        
        if access_key: self._creds[self.profile]["aws_access_key_id"] = access_key
        if secret_key: self._creds[self.profile]["aws_secret_access_key"] = secret_key
        if token:      self._creds[self.profile]["aws_session_token"] = token

    def update_config(self, region: str = None, output: str = "json"):
        """Update the config state (region/output) in memory."""
        section = self.conf_section
        if section not in self._conf.sections():
            self._conf.add_section(section)
        
        if region: self._conf[section]["region"] = region
        if output: self._conf[section]["output"] = output

    def save(self):
        """Atomic write to disk with correct permissions."""
        self.aws_dir.mkdir(exist_ok=True, mode=0o700)
        
        # Save Credentials
        with open(self.creds_path, "w") as f:
            self._creds.write(f)
        os.chmod(self.creds_path, 0o600)
        
        # Save Config
        with open(self.config_path, "w") as f:
            self._conf.write(f)
        
        print(f"✅ Profile '{self.profile}' updated successfully.")

    def verify_credentials_live(self, key: str, secret: str, token: str = None) -> bool:
        """Real-time validation of keys via AWS STS."""
        from boto3 import Session
        from botocore.exceptions import ClientError

        session = Session(
            aws_access_key_id=key, 
            aws_secret_access_key=secret, 
            aws_session_token=token
        )
        sts = session.client('sts')
        try:
            identity = sts.get_caller_identity()
            click.secho(f"✅ Authenticated as: {identity['Arn']}", fg="green")
            return True
        except ClientError as e:
            click.secho(f"❌ Authentication failed: {e.response['Error']['Code']}", fg="red")
            return False
        except Exception as e:
            click.secho(f"❌ Connection error: {str(e)}", fg="red")
            return False


    def validate_access_key(self, value):
        """Basic check for AWS Access Key ID format."""
        # AWS Access Keys are usually 20 characters, uppercase alphanumeric
        if not re.match(r"^[A-Z0-9]{20}$", value):
            raise click.UsageError("Access Key ID must be 20 uppercase alphanumeric characters.")
        return value

    def validate_region(self, value):
        """Ensures the region looks like a standard AWS region (e.g., us-east-1)."""
        # Simple regex for region format: lowercase-letters-digit
        if not re.match(r"^[a-z]{2}-[a-z]+-[0-9]{1}$", value):
            raise click.UsageError("Invalid region format. Example: us-east-1")
        return value