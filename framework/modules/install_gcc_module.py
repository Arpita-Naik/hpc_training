import subprocess
import os
import re
import requests
import sys
from pathlib import Path

# Logger import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import setup_logger


class GCCInstaller:

    def __init__(self):
        self.home = str(Path.home())
        self.install_dir = f"{self.home}/hpc/gcc{self.VERSION}"
        self.src_dir = f"{self.home}/hpc_sources"

        self.logger = setup_logger("gcc", "gcc.log")

        self.VERSION = self.get_latest_gcc_version()
        self.tar_name = f"gcc-{self.VERSION}.tar.gz"
        self.src_folder = f"gcc-{self.VERSION}"

    def get_latest_gcc_version(self):
        self.logger.info("Fetching latest GCC version...")

        url = "https://ftp.gnu.org/gnu/gcc/"
        response = requests.get(url)

        versions = re.findall(r'gcc-(\d+\.\d+\.\d+)/', response.text)
        versions.sort(key=lambda s: list(map(int, s.split("."))))

        latest = versions[-1]
        self.logger.info(f"Latest GCC version: {latest}")

        return latest

 
    def run(self, command):
        self.logger.info(f"Running: {' '.join(command)}")

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            self.logger.error(result.stderr)
            raise Exception("Command failed")
        else:
            if result.stdout:
                self.logger.info(result.stdout)

    def detect_package_manager(self):
        if subprocess.run(["which", "apt"], stdout=subprocess.DEVNULL).returncode == 0:
            return "apt"
        elif subprocess.run(["which", "dnf"], stdout=subprocess.DEVNULL).returncode == 0:
            return "dnf"
        else:
            raise Exception("Unsupported Linux distribution.")

    def install_dependencies(self, pkg_manager):
        self.logger.info("Installing GCC dependencies...")

        if pkg_manager == "apt":
            self.run(["sudo", "apt", "update"])
            self.run([
                "sudo", "apt", "install", "-y",
                "build-essential",
                "libgmp-dev",
                "libmpfr-dev",
                "libmpc-dev",
                "wget",
                "curl"
            ])

        elif pkg_manager == "dnf":
            self.run([
                "sudo", "dnf", "install", "-y",
                "gcc",
                "gcc-c++",
                "make",
                "gmp-devel",
                "mpfr-devel",
                "libmpc-devel",
                "wget",
                "curl"
            ])


    def download_source(self):
        self.logger.info("Downloading GCC source...")

        os.makedirs(self.src_dir, exist_ok=True)
        os.chdir(self.src_dir)

        if not os.path.exists(self.tar_name):
            url = f"https://ftp.gnu.org/gnu/gcc/gcc-{self.VERSION}/{self.tar_name}"
            self.run(["wget", url])
        else:
            self.logger.info("Source already exists")
    def build_and_install(self):
        self.logger.info("Building GCC...")

        os.chdir(self.src_dir)

        if not os.path.exists(self.src_folder):
            self.run(["tar", "-xf", self.tar_name])

        os.chdir(self.src_folder)

        if os.path.exists("contrib/download_prerequisites"):
            self.run(["./contrib/download_prerequisites"])

        os.makedirs("build", exist_ok=True)
        os.chdir("build")

        self.run([
            "../configure",
            f"--prefix={self.install_dir}",
            "--enable-languages=c,c++",
            "--disable-multilib"
        ])

        self.run(["make", f"-j{os.cpu_count()}"])
        self.run(["make", "install"])

  
    def create_module(self):
        self.logger.info("Creating GCC modulefile...")

        module_base = "/usr/share/modules/modulefiles/gcc"
        module_file = os.path.join(module_base, self.VERSION)

        subprocess.run(["sudo", "mkdir", "-p", module_base])

        content = f"""#%Module1.0
proc ModulesHelp {{ }} {{
    puts stderr "GCC {self.VERSION}"
}}
module-whatis "GCC {self.VERSION}"

prepend-path PATH {self.install_dir}/bin
prepend-path LD_LIBRARY_PATH {self.install_dir}/lib64
"""

        process = subprocess.Popen(
            ["sudo", "tee", module_file],
            stdin=subprocess.PIPE,
            text=True
        )
        process.communicate(content)

        self.logger.info(f"Module created: gcc/{self.VERSION}")

    def verify(self):
        self.logger.info("Verifying GCC installation...")

        gcc_path = f"{self.install_dir}/bin/gcc"

        result = subprocess.run(
            [gcc_path, "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            self.logger.info(result.stdout.splitlines()[0])
        else:
            raise Exception("Verification failed")


    def install(self):
        try:
            self.logger.info("=== GCC INSTALLATION STARTED ===")

            if os.path.exists(f"{self.install_dir}/bin/gcc"):
                self.logger.info("GCC already installed")
                self.verify()
                return

            pkg_manager = self.detect_package_manager()

            self.install_dependencies(pkg_manager)
            self.download_source()
            self.build_and_install()
            self.create_module()
            self.verify()

            self.logger.info("=== GCC INSTALLATION SUCCESS ===")

        except Exception:
            self.logger.exception("GCC INSTALLATION FAILED")
            raise


if __name__ == "__main__":
    GCCInstaller().install()
