import subprocess
import os
import re
import requests
import sys
from pathlib import Path
from system_check.detect_os import OSDetector

# Logger import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import setup_logger


class PythonInstaller:

    def __init__(self):
        self.home = str(Path.home())
        self.install_dir = f"{self.home}/hpc/python/{self.VERSION}"
        self.src_dir = f"{self.home}/hpc_sources"

        self.logger = setup_logger("python", "python.log")

        self.VERSION = self.get_latest_python_version()

        self.tar_name = f"Python-{self.VERSION}.tar.xz"
        self.src_folder = f"Python-{self.VERSION}"

    def get_latest_python_version(self):
        self.logger.info("Fetching latest Python version...")

        url = "https://www.python.org/ftp/python/"
        response = requests.get(url)

        versions = re.findall(r'href="(\d+\.\d+\.\d+)/"', response.text)
        versions.sort(key=lambda s: list(map(int, s.split("."))), reverse=True)

        for version in versions:
            tar_url = f"https://www.python.org/ftp/python/{version}/Python-{version}.tar.xz"
            check = requests.head(tar_url)

            if check.status_code == 200:
                self.logger.info(f"Latest Python version: {version}")
                return version

        raise Exception("No valid Python version found.")

    def run(self, command):
        self.logger.info(f"Running: {' '.join(command)}")

        process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

        for line in process.stdout:
            print(line, end="")              
            self.logger.info(line.strip()) 

        process.wait()
        if process.returncode != 0:
            raise Exception("Command failed")
            
    def install_dependencies(self, pkg_manager):
        self.logger.info("Installing Python dependencies...")

        if pkg_manager == "apt":
            self.run(["sudo", "apt", "update"])
            self.run([
                "sudo", "apt", "install", "-y",
                "build-essential",
                "libssl-dev",
                "zlib1g-dev",
                "libncurses5-dev",
                "libreadline-dev",
                "libsqlite3-dev",
                "libgdbm-dev",
                "libbz2-dev",
                "libexpat1-dev",
                "liblzma-dev",
                "tk-dev",
                "wget",
                "curl"
            ])

        elif pkg_manager == "dnf":
            self.run([
                "sudo", "dnf", "install", "-y",
                "gcc",
                "make",
                "openssl-devel",
                "bzip2-devel",
                "libffi-devel",
                "zlib-devel",
                "readline-devel",
                "sqlite-devel",
                "xz-devel",
                "tk-devel",
                "wget",
                "curl"
            ])

        else:
            raise Exception("Unsupported package manager.")


    def download_source(self):
        self.logger.info("Downloading Python source...")

        os.makedirs(self.src_dir, exist_ok=True)
        os.chdir(self.src_dir)

        if not os.path.exists(self.tar_name):
            url = f"https://www.python.org/ftp/python/{self.VERSION}/{self.tar_name}"
            self.run(["wget", url])
        else:
            self.logger.info("Source already exists")

    def build_and_install(self):
        self.logger.info("Building Python...")

        os.chdir(self.src_dir)

        if not os.path.exists(self.src_folder):
            self.run(["tar", "-xf", self.tar_name])

        os.chdir(self.src_folder)

        self.run([
            "./configure",
            f"--prefix={self.install_dir}",
            "--enable-optimizations"
        ])

        self.run(["make", f"-j{os.cpu_count()}"])
        self.run(["make", "install"])

    def create_module(self):
        self.logger.info("Creating Python modulefile...")

        module_base = "/usr/share/modules/modulefiles/python"
        module_file = os.path.join(module_base, self.VERSION)

        subprocess.run(["sudo", "mkdir", "-p", module_base])

        content = f"""#%Module1.0
proc ModulesHelp {{ }} {{
    puts stderr "Python {self.VERSION}"
}}
module-whatis "Python {self.VERSION}"

prepend-path PATH {self.install_dir}/bin
prepend-path LD_LIBRARY_PATH {self.install_dir}/lib
"""

        process = subprocess.Popen(
            ["sudo", "tee", module_file],
            stdin=subprocess.PIPE,
            text=True
        )
        process.communicate(content)

        self.logger.info(f"Module created: python/{self.VERSION}")


    def verify(self):
        self.logger.info("Verifying Python installation...")

        python_path = f"{self.install_dir}/bin/python3"

        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            self.logger.info(result.stdout.strip())
        else:
            raise Exception("Verification failed")

 
    def install(self):
        try:
            self.logger.info("=== PYTHON INSTALLATION STARTED ===")

            detector = OSDetector()
            system_info = detector.detect()
            pkg_manager = system_info["package_manager"]

            if os.path.exists(f"{self.install_dir}/bin/python3"):
                self.logger.info("Python already installed")
                self.verify()
                return

            self.install_dependencies(pkg_manager)
            self.download_source()
            self.build_and_install()
            self.create_module()
            self.verify()

            self.logger.info("=== PYTHON INSTALLATION SUCCESS ===")

        except Exception:
            self.logger.exception("PYTHON INSTALLATION FAILED")
            raise


if __name__ == "__main__":
    PythonInstaller().install()
