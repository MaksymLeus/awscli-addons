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


