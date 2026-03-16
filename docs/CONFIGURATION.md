# Configuration Guide

`awscli-addons` relies on the standard AWS configuration files and environment variables, meaning it works seamlessly with your existing setup.

## AWS Credentials

The tool reads from standard AWS locations:
1.  Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`).
2.  Your local credentials file (`~/.aws/credentials`).
3.  Your local configuration file (`~/.aws/config`).

You can explicitly target specific profiles using the `-p` or `--profile` flag on most commands:
```bash
awscli-addons whoami --profile production
```

## Native AWS CLI Alias Integration
To use the tool as `aws addons <command>`, you need to register it in the AWS CLI alias file. The installer script does this automatically, but if you need to do it manually:

1. Open or create the file at `~/.aws/cli/alias`.

2. Add the following block:
   ```ini
   [toplevel]
   addons = !awscli-addons
   ```
   Once saved, aws addons myip will pass the execution seamlessly to the awscli-addons binary.

## Interactive Configuration
You can use the built-in configuration tool to set up new profiles interactively, similar to aws configure:
```bash
awscli-addons configure --profile new-dev-profile
```