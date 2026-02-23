# awscli-addons
```ini
awscli-addons/
│
├─ awscli_addons/
│   ├─ __init__.py
│   ├─ mfa.py
│   ├─ assume_role.py
│   ├─ whoami.py
│   ├─ myip.py
│   └─ cli.py        # main CLI entrypoint
├─ pyproject.toml
└─ README.md
```


# Usage
Install script
```bash
curl -s https://raw.githubusercontent.com/you/aws-custom/main/install.sh | bash
```

install.sh should:

- Detect OS

- Backup existing aws binary

- Install wrapper

- Make everything executable

- Print success message







```
# MFA login
awscli-addons mfa --profile default --mfa-code 123456

# Assume IAM role
awscli-addons assume-role --role-arn arn:aws:iam::123456789012:role/MyRole

# Who am I?
awscli-addons whoami --profile mfa

# Public IP
awscli-addons myip
```



Steps

export AWS_DEFAULT_REGION=us-east-1
export AWS_PROFILE=mytest

Run:
python3 -m awscli_addons.cli verify
should be interactiv if user not exist procide with steps to add 




1) install.sh

  So we have 2 choises :
  1. req: git + python
    for install using pip
  2. req: curl or wget for install directly binery


   Force binary:
   ```bash
   curl -sSL https://raw.githubusercontent.com/.../install.sh | BINARY_CMD=true bash
   ```
   Force python:
   ```bash
   curl -sSL https://raw.githubusercontent.com/.../install.sh | PYTHON_ONLY=true bash
   ```
   Auto mode:
   ```bash
   curl -sSL https://raw.githubusercontent.com/.../install.sh | bash
   ```

   🔐 How Checksum Must Be Published

   In your GitHub release (in GitHub):

   Upload:
   ```
   awscli-addons-linux-amd64
   awscli-addons-macos-arm64
   checksums.txt
   ```

   Generate checksums like:
   ```bash
   sha256sum awscli-addons-* > checksums.txt
   ```


apt update && apt install -y unzip curl git binutils

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install


