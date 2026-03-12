from pathlib import Path
import configparser

def Credentials_save(creds: dict, profile_name: str, output: bool = True):
    path = Path.home() / ".aws" / "credentials"
    config = Config_read(path)

    if profile_name not in config.sections():
        config.add_section(profile_name)

    if creds:
      config[profile_name]["aws_access_key_id"] = creds["AccessKeyId"]
      config[profile_name]["aws_secret_access_key"] = creds["SecretAccessKey"]
      if "SessionToken" in creds:
        config[profile_name]["aws_session_token"] = creds["SessionToken"]

    with open(path, "w") as f:
        config.write(f)
    
    if output:
        print(f"✅ Saved credentials to profile '{profile_name}'")
        print(f"\nUse: export AWS_PROFILE={profile_name}\n \nto use these credentials in your shell session")



def Config_read(path: Path):
    config = configparser.ConfigParser()
    config.read(path)
    return config


def Config_profile_exists(path: str, profile_name: str):
    _path = Path.home() / path
    config = Config_read(_path)
    return profile_name in config.sections()



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

    return {
        "aws_dir": aws_dir,
        "credentials_file": credentials_file,
        "config_file": config_file
    }