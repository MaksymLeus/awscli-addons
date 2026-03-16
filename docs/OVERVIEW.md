# Project Overview

`awscli-addons` is a standalone Python-based CLI application designed to eliminate the boilerplate associated with standard AWS CLI usage. It wraps complex API calls (via `boto3` or system-level AWS interactions) into intuitive, developer-friendly commands.

## Core Architecture

* **CLI Framework:** Built using `click`, leveraging a custom `AliasedGroup` class to provide fast, two-letter shorthand commands.
* **Modular Design:** The `awscli_addons/commands/` directory isolates the business logic of every command (e.g., `assume_role.py`, `ecr.py`), keeping the main `cli.py` entry point clean and manageable.
* **Distribution:** Packaged as both a standard Python module (via `pyproject.toml`) and as standalone compiled binaries (via PyInstaller/build scripts).

## Directory Structure
* `awscli_addons/`: The core Python package.
  * `cli.py`: Main entry point and alias routing.
  * `commands/`: Individual logic for each CLI command.
* `tools/`: Shell scripts for building (`build.sh`) and distributing (`installer.sh`) the application.

## Command Reference & Aliases

| Command | Alias | Description |
| :--- | :--- | :--- |
| `whoami` | `wi` | Retrieves active caller identity (`sts get-caller-identity`). |
| `mfa` | *None* | Prompts for token and creates temporary session credentials. |
| `assume-role` | `ar` | Requests and configures temporary role credentials. |
| `show-creds` | `sc` | Displays active IAM credentials, with optional shell export. |
| `configure` | `conf` | Interactive setup for standard AWS CLI configurations. |
| `verify` | `ver` | System health check for AWS connectivity and config validity. |
| `myip` | *None* | Fetches the user's public IP address. |
| `upgrade` | `up` | Replaces the current binary with the latest GitHub release. |

**ECR Subcommands (`awscli-addons ecr ...`)**
* `login`: Generates ECR Private Docker login string.
* `login-public`: Generates ECR Public Docker login string.
* `login-helm`: Generates Helm registry login string.
* `repo-list`: Lists ECR repositories.
* `purge`: Generates a command to delete untagged images.