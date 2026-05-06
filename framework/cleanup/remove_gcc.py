'''import os
import shutil
from pathlib import Path


class GCCRemover:

    def __init__(self):
        self.home = str(Path.home())
        self.install_dir = f"{self.home}/hpc/gcc"
        self.src_dir = f"{self.home}/hpc_sources"
        self.bashrc = f"{self.home}/.bashrc"

    def remove_installation(self):
        print("Removing GCC installation...")

        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir, ignore_errors=True)
            print("✔ Removed install directory.")
        else:
            print("Install directory not found. Skipping.")

    def remove_sources(self):
        if not os.path.exists(self.src_dir):
            return

        for item in os.listdir(self.src_dir):
            if item.startswith("gcc-"):
                path = os.path.join(self.src_dir, item)

                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    print(f"✔ Removed source folder: {item}")

                elif item.endswith(".tar.gz"):
                    os.remove(path)
                    print(f"✔ Removed tar file: {item}")

    def clean_bashrc(self):
        if not os.path.exists(self.bashrc):
            return

        with open(self.bashrc, "r") as f:
            lines = f.readlines()

        with open(self.bashrc, "w") as f:
            for line in lines:
                if "hpc/gcc/bin" not in line:
                    f.write(line)

        print("✔ Removed GCC PATH entry from ~/.bashrc")


    def remove(self):
        print("===== Removing GCC (HPC Version) =====")

        self.remove_installation()
        self.remove_sources()
        self.clean_bashrc()

        print("===== GCC completely removed =====")
        print("Run: source ~/.bashrc")


if __name__ == "__main__":
    remover = GCCRemover()
    remover.remove()'''

import os
import shutil
import sys
import subprocess
from pathlib import Path

# Logger import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import setup_logger


class GCCRemover:

    def __init__(self):
        self.home = str(Path.home())
        self.install_dir = f"{self.home}/hpc/gcc"
        self.src_dir = f"{self.home}/hpc_sources"
        self.module_dir = "/usr/share/modules/modulefiles/gcc"

        self.logger = setup_logger("gcc_remove", "gcc_remove.log")


    def ensure_root(self):
        if os.geteuid() != 0:
            print("Re-running with sudo...")
            subprocess.call(["sudo", sys.executable] + sys.argv)
            sys.exit()

    def remove_installation(self):
        self.logger.info("Removing GCC installation...")

        if os.path.exists(self.install_dir):
            shutil.rmtree(self.install_dir, ignore_errors=True)
            self.logger.info("Removed install directory")
        else:
            self.logger.info("Install directory not found")


    def remove_sources(self):
        self.logger.info("Removing GCC sources...")

        if not os.path.exists(self.src_dir):
            self.logger.info("Source directory not found")
            return

        for item in os.listdir(self.src_dir):
            if item.startswith("gcc-"):
                path = os.path.join(self.src_dir, item)

                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                    self.logger.info(f"Removed folder: {item}")

                elif item.endswith(".tar.gz"):
                    os.remove(path)
                    self.logger.info(f"Removed tar: {item}")

    def remove_module(self):
        self.logger.info("Removing GCC modulefiles...")

        if os.path.exists(self.module_dir):
            shutil.rmtree(self.module_dir, ignore_errors=True)
            self.logger.info("Removed gcc module directory")
        else:
            self.logger.info("Module directory not found")

    def remove(self):
        try:
            self.ensure_root()

            self.logger.info("=== GCC REMOVAL STARTED ===")

            self.remove_installation()
            self.remove_sources()
            self.remove_module()

            self.logger.info("=== GCC REMOVAL COMPLETE ===")

        except Exception:
            self.logger.exception("GCC REMOVAL FAILED")
            raise


if __name__ == "__main__":
    GCCRemover().remove()