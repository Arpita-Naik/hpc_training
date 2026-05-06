'''import os
import shutil
import sys
import subprocess
class OpenMPIRemover:

    def __init__(self):
        self.install_dir = "/opt/openmpi"
        self.src_dir = "/opt/openmpi_sources"

    def ensure_root(self):
        if os.geteuid() != 0:
            print("Root privileges required. Re-running with sudo...")
            subprocess.call(["sudo", "python3"] + sys.argv)
            sys.exit()

    def remove_installation(self):
        print("Removing /opt OpenMPI installation...")

        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir, ignore_errors=True)
            print("✔ Removed /opt/openmpi")
        else:
            print("/opt/openmpi not found. Skipping.")


    def remove_sources(self):
        if os.path.exists(self.src_dir):
            shutil.rmtree(self.src_dir, ignore_errors=True)
            print("✔ Removed /opt/openmpi_sources")
        else:
            print("/opt/openmpi_sources not found.")

    def remove_symlinks(self):
        print("Removing symlinks...")

        paths = [
            "/usr/local/bin/mpirun",
            "/usr/local/bin/mpiexec",
            "/usr/local/bin/mpicc"
        ]

        for path in paths:
            if os.path.lexists(path):
                os.remove(path)
                print(f"✔ Removed {path}")
            else:
                print(f"{path} not found.")

    def remove(self):
        self.ensure_root()
        print("===== Removing System OpenMPI =====")

        self.remove_installation()
        self.remove_sources()
        self.remove_symlinks()

        print("===== OpenMPI completely removed =====")


if __name__ == "__main__":
    remover = OpenMPIRemover()
    remover.remove()'''


import os
import shutil
import sys
import subprocess


class OpenMPIRemover:

    def __init__(self):
        self.install_dir = "/opt/openmpi"
        self.src_dir = "/opt/openmpi_sources"
        self.module_dir = "/usr/share/modules/modulefiles/openmpi"

 
    def ensure_root(self):
        if os.geteuid() != 0:
            print("Root privileges required. Re-running with sudo...")
            subprocess.call(["sudo", sys.executable] + sys.argv)
            sys.exit()


    def remove_installation(self):
        print("Removing OpenMPI installation...")

        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir, ignore_errors=True)
            print("✔ Removed /opt/openmpi")
        else:
            print("/opt/openmpi not found. Skipping.")


    def remove_sources(self):
        print("Removing source files...")

        if os.path.exists(self.src_dir):
            shutil.rmtree(self.src_dir, ignore_errors=True)
            print("✔ Removed /opt/openmpi_sources")
        else:
            print("/opt/openmpi_sources not found.")


    def remove_symlinks(self):
        print("Removing symlinks...")

        paths = [
            "/usr/local/bin/mpirun",
            "/usr/local/bin/mpiexec",
            "/usr/local/bin/mpicc"
        ]

        for path in paths:
            if os.path.lexists(path):
                os.remove(path)
                print(f"✔ Removed {path}")
            else:
                print(f"{path} not found.")


    def remove_module(self):
        print("Removing module files...")

        if os.path.exists(self.module_dir):
            shutil.rmtree(self.module_dir, ignore_errors=True)
            print("✔ Removed modulefiles (openmpi)")
        else:
            print("Module files not found.")

 
    def remove(self):
        self.ensure_root()

        print("\n===== Removing OpenMPI =====\n")

        self.remove_installation()
        self.remove_sources()
        self.remove_symlinks()
        self.remove_module()

        print("\n===== OpenMPI completely removed =====\n")


if __name__ == "__main__":
    remover = OpenMPIRemover()
    remover.remove()