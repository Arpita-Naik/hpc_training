import subprocess
import os
import sys
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
