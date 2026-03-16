# Deployment & Distribution

This document outlines how `awscli-addons` is packaged, distributed, and containerized for end-users.

## Standalone Binaries

To ensure users do not need to worry about Python environments, dependencies, or virtual environments, `awscli-addons` is compiled into standalone binaries for different architectures (e.g., Linux AMD64, macOS ARM64).

* **Build Script:** `tools/build.sh` handles the packaging. 
* **Release Process:** When a new tag is pushed to GitHub, CI/CD pipelines (GitHub Actions) should run `build.sh` and attach the resulting binaries to the GitHub Release.

## The Installer Script

The `tools/installer.sh` script is the primary entry point for users. It performs the following deployment tasks dynamically:
1. Detects the host Operating System and Architecture.
2. Downloads the matching binary from the GitHub Releases API.
3. Installs the binary to a system path (e.g., `/usr/local/bin/`).
4. Configures the `~/.aws/cli/alias` integration automatically.

## Docker Deployment

For CI/CD pipelines or strict local environments, the tool can be run as a Docker container.

**Building the Image:**
Ensure your `Dockerfile` at the repository root uses a lightweight Python base image and runs `pip install .`.

**Running the Container:**
Because the tool needs to interact with AWS, you must mount your local AWS credentials directory into the container at runtime:

```bash
docker run --rm -v ~/.aws:/root/.aws awscli-addons whoami
```