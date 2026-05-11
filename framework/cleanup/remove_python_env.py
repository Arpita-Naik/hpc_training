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
