'''import subprocess
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import setup_logger

class OpenMPIInstaller:

    def __init__(self):
        self.install_dir = "/opt/openmpi"
        self.src_dir = "/opt/openmpi_sources"
        self.logger = setup_logger("openmpi", "openmpi.log")
        self.VERSION = self.find_working_version()

        self.tar_name = f"openmpi-{self.VERSION}.tar.gz"
        self.src_folder = f"openmpi-{self.VERSION}"

 
    def find_working_version(self):
        print("Searching for downloadable OpenMPI version...")

        candidate_versions = [
            "5.0.3",
            "5.0.2",
            "5.0.1",
            "4.1.6",
            "4.1.5",
            "4.1.4"
        ]

        base_url = "https://download.open-mpi.org/release/open-mpi"

        for version in candidate_versions:
            major_minor = ".".join(version.split(".")[:2])
            url = f"{base_url}/v{major_minor}/openmpi-{version}.tar.gz"

            print(f"Trying {version}...")

            result = subprocess.run(
                ["wget", "--spider", "-q", url]
            )

            if result.returncode == 0:
                print(f"✔ Found working version: {version}")
                return version

        raise Exception("No downloadable OpenMPI version found.")

  
    def run(self, command):
        subprocess.run(command, check=True)

    def detect_package_manager(self):
        if subprocess.run(["which", "apt"], stdout=subprocess.DEVNULL).returncode == 0:
            return "apt"
        elif subprocess.run(["which", "dnf"], stdout=subprocess.DEVNULL).returncode == 0:
            return "dnf"
        else:
            raise Exception("Unsupported Linux distribution.")

    def install_dependencies(self, pkg_manager):
        print("Installing build dependencies...")

        if pkg_manager == "apt":
            self.run(["apt", "update"])
            self.run([
                "apt", "install", "-y",
                "build-essential", "gcc", "g++",
                "make", "wget"
            ])

        elif pkg_manager == "dnf":
            self.run([
                "dnf", "install", "-y",
                "gcc", "gcc-c++", "make",
                "wget"
            ])

    def download_source(self):
        print("Downloading source...")

        os.makedirs(self.src_dir, exist_ok=True)
        os.chdir(self.src_dir)

        major_minor = ".".join(self.VERSION.split(".")[:2])
        url = f"https://download.open-mpi.org/release/open-mpi/v{major_minor}/{self.tar_name}"

        self.run(["wget", url])

    def build_and_install(self):
        print("Extracting...")
        os.chdir(self.src_dir)
        self.run(["tar", "-xf", self.tar_name])
        os.chdir(self.src_folder)

        print("Running ./configure...")
        self.run(["./configure", f"--prefix={self.install_dir}"])

        print("Running make...")
        self.run(["make", f"-j{os.cpu_count()}"])

        print("Running make install...")
        self.run(["make", "install"])

        print("Creating symlinks...")
        self.run(["ln", "-sf", "/opt/openmpi/bin/mpirun", "/usr/local/bin/mpirun"])
        self.run(["ln", "-sf", "/opt/openmpi/bin/mpicc", "/usr/local/bin/mpicc"])

    def verify(self):
        result = subprocess.run(
            ["mpirun", "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✔ OpenMPI Installed Successfully")
            print(result.stdout.splitlines()[0])
        else:
            raise Exception("Verification failed.")

    def install(self):
        pkg_manager = self.detect_package_manager()
        self.install_dependencies(pkg_manager)
        self.download_source()
        self.build_and_install()
        self.verify()

        print("OpenMPI installation complete.")


if __name__ == "__main__":
    OpenMPIInstaller().install()'''


import subprocess
import os
import sys

# Import logger
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import setup_logger


class OpenMPIInstaller:

    def __init__(self):
        self.src_dir = "/opt/openmpi_sources"

        self.logger = setup_logger("openmpi", "openmpi.log")

        self.VERSION = self.find_working_version()
        self.install_dir = f"/opt/openmpi/{self.VERSION}"

        self.tar_name = f"openmpi-{self.VERSION}.tar.gz"
        self.src_folder = f"openmpi-{self.VERSION}"

    
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

    def find_working_version(self):
        self.logger.info("Searching OpenMPI version...")

        versions = ["5.0.3", "5.0.2", "4.1.6"]

        base = "https://download.open-mpi.org/release/open-mpi"

        for v in versions:
            major = ".".join(v.split(".")[:2])
            url = f"{base}/v{major}/openmpi-{v}.tar.gz"

            if subprocess.run(["wget", "--spider", "-q", url]).returncode == 0:
                self.logger.info(f"Using version {v}")
                return v

        raise Exception("No valid version found")

    def install_dependencies(self):
        self.logger.info("Installing dependencies...")

        self.run(["apt", "update"])
        self.run([
            "apt", "install", "-y",
            "build-essential", "gcc", "g++",
            "make", "wget", "environment-modules"
        ])

    def setup_module_system(self):
        self.logger.info("Configuring module system...")

        bashrc = os.path.expanduser("~/.bashrc")

        lines = [
            "\n# HPC MODULE SYSTEM\n",
            "source /etc/profile.d/modules.sh\n",
            "export MODULEPATH=$MODULEPATH:/usr/share/modules/modulefiles\n"
        ]

        with open(bashrc, "r") as f:
            content = f.read()

        with open(bashrc, "a") as f:
            for line in lines:
                if line not in content:
                    f.write(line)

        self.logger.info("Module system configured in .bashrc")

    def download(self):
        self.logger.info("Downloading OpenMPI...")

        os.makedirs(self.src_dir, exist_ok=True)
        os.chdir(self.src_dir)

        major = ".".join(self.VERSION.split(".")[:2])
        url = f"https://download.open-mpi.org/release/open-mpi/v{major}/{self.tar_name}"

        self.run(["wget", url])

    def build(self):
        self.logger.info("Building OpenMPI...")

        os.chdir(self.src_dir)
        self.run(["tar", "-xf", self.tar_name])
        os.chdir(self.src_folder)

        self.run(["./configure", f"--prefix={self.install_dir}"])
        self.run(["make", f"-j{os.cpu_count()}"])
        self.run(["make", "install"])

        # Symlinks
        self.run(["ln", "-sf", f"{self.install_dir}/bin/mpirun", "/usr/local/bin/mpirun"])
        self.run(["ln", "-sf", f"{self.install_dir}/bin/mpicc", "/usr/local/bin/mpicc"])

    def create_module(self):
        self.logger.info("Creating versioned modulefile...")
        module_base = "/usr/share/modules/modulefiles/openmpi"
        module_file = os.path.join(module_base, self.VERSION)

        subprocess.run(["sudo", "mkdir", "-p", module_base])

        content = f"""#%Module1.0
proc ModulesHelp {{ }} {{
    puts stderr "OpenMPI {self.VERSION}"
}}
module-whatis "OpenMPI {self.VERSION}"

prepend-path PATH {self.install_dir}/bin
prepend-path LD_LIBRARY_PATH {self.install_dir}/lib
"""

        process = subprocess.Popen(
        ["sudo", "tee", module_file],
        stdin=subprocess.PIPE,
        text=True
    )
        process.communicate(content)
        self.logger.info(f"Modulefile created: openmpi/{self.VERSION}")

    # -------------------------------
    # Verify
    # -------------------------------
    def verify(self):
        self.logger.info("Verifying installation...")

        result = subprocess.run(
            ["mpirun", "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            self.logger.info(result.stdout.splitlines()[0])
        else:
            raise Exception("Verification failed")


    def install(self):
        try:
            self.logger.info("=== OpenMPI Installation Started ===")

            self.install_dependencies()
            self.setup_module_system()
            self.download()
            self.build()
            self.create_module()
            self.verify()

            self.logger.info("=== INSTALLATION SUCCESS ===")

        except Exception as e:
            self.logger.exception("INSTALLATION FAILED")
            raise


if __name__ == "__main__":
    OpenMPIInstaller().install()