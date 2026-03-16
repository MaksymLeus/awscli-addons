# Development Guide

Want to contribute or build `awscli-addons` from source? Follow these instructions to set up your local environment.

## Environment Setup

1. Ensure you have Python 3.11+ installed.
2. Clone the repository and navigate into the root directory.
3. Install the package in editable mode:

```bash
pip install -e .
```
## Adding a New Command
The project uses a modular `click` structure. To add a new command (e.g., `cleanup`):

1. **Create the logic file**:
Create `awscli_addons/commands/cleanup.py` and write your underlying logic.

2. **Register the command in `cli.py`**:
Import your function and use the `@cli.command()` decorator.
```py
@cli.command("cleanup")
@click.option("--dry-run", is_flag=True, help="Simulate the cleanup")
def cleanup_command(dry_run):
    """Clean up old AWS resources."""
    from awscli_addons.commands.cleanup import run_cleanup
    run_cleanup(dry_run)
```

3. **Add an Alias (Optional)**:
If you want a shortcut, add it to the MAP dictionary inside the AliasedGroup class in cli.py:
```py
MAP = {
    # ... existing aliases ...
    'cl': 'cleanup'
}
```
## Compiling Binaries Locally
To test the binary compilation process on your machine, use the build script:
```bash
./tools/build.sh
```
This script packages the Python application into a standalone executable using tools like PyInstaller.

## Docker 
If you want to test the application within a containerized environment, you can build the image locally. We use a build argument to inject the version string into the CLI.

```bash
docker build --build-arg VERSION=feature/init -t awscli-addons .
```
### Run the Container
Once built, you can run the container by mounting your local AWS configuration:

```bash
docker run --rm -v ~/.aws:/root/.aws awscli-addons wi
```
Use VERSION=$(git describe --tags --always) if you want the Docker image to match your current git state exactly.