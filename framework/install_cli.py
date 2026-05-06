import os
import shutil
import subprocess
import sys

def check_root():
    if os.geteuid() != 0:
        print("Run this installer with sudo.")
        sys.exit(1)

def install_cli():
    print("Installing HPC Framework CLI...")

    src = os.path.join(os.getcwd(), "hpcctl")
    dest = "/usr/local/bin/hpcctl"

    if not os.path.exists(src):
        print("hpcctl file not found.")
        sys.exit(1)

    shutil.copy(src, dest)
    os.chmod(dest, 0o755)

    print("✔ hpcctl installed globally.")

if __name__ == "__main__":
    check_root()
    install_cli()