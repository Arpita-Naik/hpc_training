import os
import subprocess

MODULE_DIR = "/opt/hpc/modulefiles"


def run(cmd):
    subprocess.run(cmd, check=True)


def install_modules_system():

    if os.path.exists("/usr/bin/modulecmd"):
        print("Environment Modules already installed")
        return

    print("Installing Environment Modules")

    if os.path.exists("/usr/bin/dnf"):
        run(["sudo", "dnf", "install", "-y", "environment-modules"])

    elif os.path.exists("/usr/bin/apt"):
        run(["sudo", "apt", "install", "-y", "environment-modules"])


def create_module_dir():

    os.makedirs(MODULE_DIR, exist_ok=True)


def create_python_module():

    content = """#%Module1.0
module-whatis "Python module"

prepend-path PATH /home/arpita/hpc/python/bin
prepend-path LD_LIBRARY_PATH /home/arpita/hpc/python/lib
"""

    with open("/tmp/python_module", "w") as f:
        f.write(content)

    run(["sudo", "mv", "/tmp/python_module", f"{MODULE_DIR}/python"])


def create_slurm_module():

    content = """#%Module1.0
module-whatis "Slurm module"

prepend-path PATH /opt/hpc/slurm/bin
prepend-path LD_LIBRARY_PATH /opt/hpc/slurm/lib
"""

    with open("/tmp/slurm_module", "w") as f:
        f.write(content)

    run(["sudo", "mv", "/tmp/slurm_module", f"{MODULE_DIR}/slurm"])


def configure_module_path():

    bashrc = os.path.expanduser("~/.bashrc")

    line = "module use /opt/hpc/modulefiles"

    with open(bashrc, "r") as f:
        data = f.read()

    if line not in data:
        with open(bashrc, "a") as f:
            f.write("\n" + line + "\n")


def setup():

    install_modules_system()
    create_module_dir()
    create_python_module()
    create_slurm_module()
    configure_module_path()

    print("Modules configured successfully")


if __name__ == "__main__":
    setup()