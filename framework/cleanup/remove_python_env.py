'''import os
import shutil
from pathlib import Path
import re


class PythonRemover:

    def __init__(self):
        self.home = str(Path.home())
        self.install_dir = f"{self.home}/hpc/python"
        self.src_dir = f"{self.home}/hpc_sources"
        self.bashrc = f"{self.home}/.bashrc"

    def remove_installation(self):
        print("Removing Python installation...")

        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir)
            print("✔ Removed install directory.")
        else:
            print("Install directory not found. Skipping.")

    def remove_sources(self):
        if not os.path.exists(self.src_dir):
            return

        for item in os.listdir(self.src_dir):
            if item.startswith("Python-"):
                path = os.path.join(self.src_dir, item)

                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    print(f"✔ Removed source folder: {item}")

                elif item.endswith(".tar.xz"):
                    os.remove(path)
                    print(f"✔ Removed tar file: {item}")

    def clean_bashrc(self):
        if not os.path.exists(self.bashrc):
            return

        with open(self.bashrc, "r") as f:
            lines = f.readlines()

        with open(self.bashrc, "w") as f:
            for line in lines:
                if "hpc/python/bin" not in line:
                    f.write(line)

        print("✔ Removed PATH entry from ~/.bashrc")

    def verify(self):


        python_path = f"{self.install_dir}/bin/python3"

        if not os.path.exists(python_path):
            print("✔ Python successfully removed")
        else:
            print("⚠ Python still exists")

    def remove(self):
        print("===== Removing Python (HPC Version) =====")

        self.remove_installation()
        self.remove_sources()
        self.clean_bashrc()

        print("===== Python completely removed =====")
        print("Run: source ~/.bashrc")

if __name__ == "__main__":
    remover = PythonRemover()
    remover.remove()'''


import os
import shutil
import sys
import subprocess
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import setup_logger

class PythonRemover:

    def __init__(self):
        self.home = str(Path.home())
        self.install_dir = f"{self.home}/hpc/python"
        self.src_dir = f"{self.home}/hpc_sources"
        self.module_dir = "/usr/share/modules/modulefiles/python"

        self.logger = setup_logger("python_remove", "python_remove.log")

    def ensure_root(self):
        if os.geteuid() != 0:
            print("Re-running with sudo...")
            subprocess.call(["sudo", sys.executable] + sys.argv)
            sys.exit()


    def remove_installation(self):
        self.logger.info("Removing Python installation...")

        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir, ignore_errors=True)
            self.logger.info("Removed install directory")
        else:
            self.logger.info("Install directory not found")

    def remove_sources(self):
        self.logger.info("Removing Python sources...")

        if not os.path.exists(self.src_dir):
            self.logger.info("Source directory not found")
            return

        for item in os.listdir(self.src_dir):
            if item.startswith("Python-"):
                path = os.path.join(self.src_dir, item)

                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    self.logger.info(f"Removed folder: {item}")

                elif item.endswith(".tar.xz"):
                    os.remove(path)
                    self.logger.info(f"Removed tar: {item}")

    def remove_module(self):
        self.logger.info("Removing Python modulefiles...")

        if os.path.exists(self.module_dir):
            shutil.rmtree(self.module_dir, ignore_errors=True)
            self.logger.info("Removed python module directory")
        else:
            self.logger.info("Module directory not found")


    def verify(self):
        python_path = f"{self.install_dir}/bin/python3"

        if not os.path.exists(python_path):
            self.logger.info("Python successfully removed")
        else:
            self.logger.warning("Python still exists")

 
    def remove(self):
        try:
            self.ensure_root()

            self.logger.info("=== PYTHON REMOVAL STARTED ===")

            self.remove_installation()
            self.remove_sources()
            self.remove_module()
            self.verify()

            self.logger.info("=== PYTHON REMOVAL COMPLETE ===")

        except Exception:
            self.logger.exception("PYTHON REMOVAL FAILED")
            raise


if __name__ == "__main__":
    remover = PythonRemover()
    remover.remove()