import sys
import os
import platform
import stat
import click
import requests
import subprocess
from awscli_addons.cli import __version__

def get_platform_info():
    """Detects current OS and Architecture to match GitHub Release names."""
    system = platform.system().lower()
    os_map = {"darwin": "darwin", "linux": "linux", "windows": "windows"}
    current_os = os_map.get(system, system)

    machine = platform.machine().lower()
    arch_map = {"x86_64": "amd64", "amd64": "amd64", "arm64": "arm64", "aarch64": "arm64"}
    current_arch = arch_map.get(machine, machine)

    return f"awscli-addons-{current_os}-{current_arch}"

def perform_binary_upgrade(download_url, current_bin_path):
    """Downloads, validates, and replaces the currently running binary."""
    click.echo(f"⬇️  Downloading update...")
    
    # OS-safe temporary filenames
    if os.name == 'nt':
        new_bin_path = current_bin_path.replace(".exe", "") + "_new.exe"
        old_bin_path = current_bin_path.replace(".exe", "") + "_old.exe"
    else:
        new_bin_path = current_bin_path + ".new"
        old_bin_path = current_bin_path + ".old"

    try:
        # 1. Download
        with requests.get(download_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(new_bin_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # 2. Make executable
        if os.name != 'nt':
            st = os.stat(new_bin_path)
            os.chmod(new_bin_path, st.st_mode | stat.S_IEXEC)

        # 3. 🛡️ VALIDATION STEP: Test the new binary
        click.echo("🧪 Testing new binary integrity...")
        try:
            # We run the new binary with --version. 
            # If it crashes, raises an error, or returns non-zero, it fails.
            result = subprocess.run([new_bin_path, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise ValueError(f"Binary test failed with exit code {result.returncode}.\nOutput: {result.stderr}")
            click.echo("✅ Binary test passed!")
        except Exception as test_err:
            # Test failed! Clean up the bad download and abort.
            os.remove(new_bin_path)
            click.secho(f"❌ Update aborted. The downloaded file is corrupt or incompatible:\n{test_err}", fg="red")
            return

        # 4. Cleanup old backups
        if os.path.exists(old_bin_path):
            try:
                os.remove(old_bin_path)
            except OSError:
                pass

        # 5. The Swap
        os.rename(current_bin_path, old_bin_path)
        os.rename(new_bin_path, current_bin_path)

        click.secho("\n✨ Upgrade complete! You are now running the latest version.", fg="green", bold=True)
        
        if os.name == 'nt':
            click.secho(f"ℹ️  Note: The old version was saved as {os.path.basename(old_bin_path)} and can be deleted manually.", fg="yellow", italic=True)

    except Exception as e:
        click.secho(f"\n❌ Failed to apply update: {e}", fg="red")
        if os.path.exists(new_bin_path):
            os.remove(new_bin_path)
        if not os.path.exists(current_bin_path) and os.path.exists(old_bin_path):
            os.rename(old_bin_path, current_bin_path)

def run_upgrade(force: bool = False):
    repo = "MaksymLeus/awscli-addons"
    current = __version__
    target_artifact = get_platform_info()
    
    click.echo(f"Current version: {click.style(current, fg='yellow')}")
    
    try:
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        release_data = response.json()
    except Exception as e:
        click.secho(f"⚠️  Could not check for updates: {e}", fg="red")
        return

    latest_tag = release_data["tag_name"]
    
    if latest_tag == current and not force:
        click.secho("✅ You are up to date! (Use --force to reinstall)", fg="green")
        return

    if latest_tag == current and force:
        click.secho("🔄 Force flag detected: Reinstalling current version...", fg="yellow")

    download_url = next(
        (asset["browser_download_url"] for asset in release_data.get("assets", []) 
         if asset["name"] == target_artifact), 
        None
    )

    if not download_url:
        click.secho(f"❌ Could not find a binary matching your system: {target_artifact}", fg="red")
        return

    click.secho(f"🆕 Target version: {latest_tag}", fg="cyan", bold=True)
    
    if getattr(sys, 'frozen', False):
        perform_binary_upgrade(download_url, sys.executable)
    else:
        click.echo("🐍 Python package detected. Upgrading via pip...")
        try:
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "awscli-addons"]
            subprocess.run(cmd, check=True)
            click.secho("✅ Pip upgrade successful!", fg="green")
        except subprocess.CalledProcessError:
            click.secho("❌ Pip upgrade failed.", fg="red")