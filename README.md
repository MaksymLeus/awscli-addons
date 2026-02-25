# 🚀 AWSCLI-Addons
A collection of high-performance, standalone CLI utilities designed to extend and simplify your daily AWS workflows. These tools bridge the gap between complex aws cli commands and common developer tasks like MFA authentication, role assumption, and identity verification.

## 🛠️ Features
This suite adds specialized commands to your toolkit:

- `whoami`: Quickly identifies the current IAM identity, account ID, and region.

- `mfa`: Streamlines the generation of temporary session tokens using a multi-factor authentication device.

- `assume-role`: Simplifies switching between AWS accounts and IAM roles with automatic environment variable management.

- `myip`: Instantly retrieves your current public IP address (crucial for updating Security Group ingress rules).

- `verify`: Validates your current credentials and connection to ensure your environment is "cloud-ready."

## 📂 Project Structure
```txt
awscli-addons
├── awscli_addons/      # Core Python package
│   ├── cli.py          # Main entry point
│   └── commands/       # Individual command implementations
├── tools/
│   ├── build.sh        # Script for creating standalone binaries
│   └── installer.sh    # Quick-install script for users
├── pyproject.toml      # Dependency and package management
└── docs/TODO.md        # Future roadmap and pending features
```


## 🚀 Installation

### Instant Install (Recommended)

Use our hosted installer to automatically detect your OS and Architecture.


| Mode             | Command       |
| :----------------: | --------------------------------- |
| Auto | `curl -sSL https://raw.githubusercontent.com/MaksymLeus/awscli-addons/main/tools/installer.sh \| bash` |
| Force Binary	| `curl -sSL https://raw.githubusercontent.com/MaksymLeus/awscli-addons/main/tools/installer.sh \| BINARY_CMD=true bash` | 
| Force Python	| `curl -sSL https://raw.githubusercontent.com/MaksymLeus/awscli-addons/main/tools/installer.sh \| PYTHON_ONLY=true bash` |

Prerequisites: git and python 3.11+ (for Python mode).

#### Install Specific Version:

```bash
curl -sSL https://raw.githubusercontent.com/MaksymLeus/awscli-addons/main/tools/installer.sh | VERSION=v1.1.2 bash
```

### Manual Installation

Download the appropriate binary for your platform from the [`Releases page`](https://github.com/MaksymLeus/awscli-addons/releases):


```bash
# Example for Linux AMD64
wget https://github.com{VERSION}/awscli-addons-linux-amd64
chmod +x awscli-addons-linux-amd64
sudo mv awscli-addons-linux-amd64 /usr/local/bin/awscli-addons

```

## 📖 Usage
Once installed, you can use the commands directly or as an AWS CLI alias.

### Direct Usage
```bash
# Check your current identity
awscli-addons whoami

# Generate MFA session
# Prompts for code if not provided; works with profiles 
awscli-addons mfa --profile default --mfa-code 123456 

# Get your public IP for Security Group rules
awscli-addons myip
```

### Power User: Native AWS CLI Integration
The installer **automatically** configures an AWS CLI alias for you. Even if you install the official AWS CLI after these addons, the integration will be ready to use.

```bash
# Use it like a native AWS command
aws addons whoami
aws addons mfa
aws addons myip
```

How it works: The installer adds a persistent alias to your **`~/.aws/cli/alias`** configuration, mapping **`aws addons`** directly to your `awscli-addons` binary.


##  🔨 Development & Building

To build the project from source or add new commands:

1. Install dependencies:
   ```bash
   pip install .
   ```
2. Add a command:

	Create a new `.py` file in `awscli_addons/commands/` and register it in `cli.py`.

3. Build standalone binaries:
	
	```bash
	./tools/build.sh
	```