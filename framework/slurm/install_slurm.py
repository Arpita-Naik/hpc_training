import subprocess
import os
import shutil
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from system_check.detect_os import OSDetector
from logger import setup_logger


class SlurmInstaller:

    DEFAULT_VERSION = "24.11.1"
    WORKDIR = "/root"
    PREFIX = "/opt/hpc/slurm"

    def __init__(self):
        self.logger = setup_logger("slurm", "slurm.log")

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

    def get_latest_version(self):
        self.logger.info("Fetching latest Slurm version...")

        try:
            result = subprocess.run(
                ["curl", "-s", "https://download.schedmd.com/slurm/"],
                capture_output=True,
                text=True
            )

            matches = re.findall(r"slurm-(\d+\.\d+\.\d+)\.tar\.bz2", result.stdout)

            if matches:
                latest = sorted(matches, key=lambda x: list(map(int, x.split("."))))[-1]
                self.logger.info(f"Latest version: {latest}")
                return latest

        except Exception as e:
            self.logger.error(str(e))

        self.logger.info(f"Using default version: {self.DEFAULT_VERSION}")
        return self.DEFAULT_VERSION

    def install_dependencies(self, pkg_manager):
        self.logger.info("Installing dependencies...")

        if pkg_manager == "apt":
            self.run(["sudo", "apt", "update"])

            packages = [
                "build-essential", "munge", "libmunge-dev",
                "libssl-dev", "libpam0g-dev", "libmariadb-dev",
                "libjson-c-dev", "libhwloc-dev", "libbpf-dev",
                "libdbus-1-dev", "libsystemd-dev", "libnuma-dev",
                "pkg-config", "bison", "flex",
                "mariadb-server", "curl", "wget"
            ]

            self.run(["sudo", "apt", "install", "-y"] + packages)

        elif pkg_manager in ["dnf", "yum"]:
            self.run(["sudo", pkg_manager, "install", "-y", "gcc", "make"])

        else:
            raise Exception("Unsupported package manager")

    def enable_munge(self):
        self.logger.info("Enabling Munge...")

        key_path = "/etc/munge/munge.key"

        if not os.path.exists(key_path):

            if shutil.which("create-munge-key"):
                self.run(["sudo", "create-munge-key"])
            elif shutil.which("mungekey"):
                self.run(["sudo", "mungekey", "--create"])
            else:
                raise Exception("No munge key generator found")

            self.run(["sudo", "chown", "munge:munge", key_path])
            self.run(["sudo", "chmod", "400", key_path])

        self.run(["sudo", "systemctl", "enable", "munge"])
        self.run(["sudo", "systemctl", "restart", "munge"])


    def download_and_build(self):
        self.logger.info("Downloading and building Slurm...")

        self.VERSION = self.get_latest_version()

        os.chdir(self.WORKDIR)

        tar_file = f"slurm-{self.VERSION}.tar.bz2"
        source_dir = f"slurm-{self.VERSION}"

        if not os.path.exists(tar_file):
            self.run(["sudo", "wget", f"https://download.schedmd.com/slurm/{tar_file}"])

        if os.path.exists(source_dir):
            self.run(["sudo", "rm", "-rf", source_dir])

        self.run(["sudo", "tar", "-xjf", tar_file])
        os.chdir(os.path.join(self.WORKDIR, source_dir))

        self.run([
            "sudo",
            "./configure",
            f"--prefix={self.PREFIX}",
            "--sysconfdir=/etc/slurm"
        ])

        self.run(["sudo", "make", f"-j{os.cpu_count()}"])
        self.run(["sudo", "make", "install"])

        with open("/tmp/slurm_lib.conf", "w") as f:
            f.write(f"{self.PREFIX}/lib\n")

        self.run(["sudo", "mv", "/tmp/slurm_lib.conf", "/etc/ld.so.conf.d/slurm.conf"])
        self.run(["sudo", "ldconfig"])


    def create_module(self):
        self.logger.info("Creating Slurm modulefile...")

        module_base = "/usr/share/modules/modulefiles/slurm"
        module_file = os.path.join(module_base, self.VERSION)

        subprocess.run(["sudo", "mkdir", "-p", module_base])

        content = f"""#%Module1.0
proc ModulesHelp {{ }} {{
    puts stderr "Slurm {self.VERSION}"
}}
module-whatis "Slurm {self.VERSION}"

prepend-path PATH {self.PREFIX}/bin
prepend-path PATH {self.PREFIX}/sbin
prepend-path LD_LIBRARY_PATH {self.PREFIX}/lib
"""

        process = subprocess.Popen(
            ["sudo", "tee", module_file],
            stdin=subprocess.PIPE,
            text=True
        )
        process.communicate(content)

        self.logger.info(f"Module created: slurm/{self.VERSION}")

    def create_command_symlinks(self):
        self.logger.info("Creating command symlinks...")

        binaries = ["sinfo", "squeue", "sbatch", "scancel", "scontrol"]

        for cmd in binaries:
            target = f"{self.PREFIX}/bin/{cmd}"
            link = f"/usr/local/bin/{cmd}"

            if os.path.exists(target) and not os.path.exists(link):
                self.run(["sudo", "ln", "-s", target, link])

    def create_slurm_user(self):
        if subprocess.run(
            ["id", "slurm"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode != 0:

            self.run(["sudo", "useradd", "-r", "-m", "slurm"])

    def setup_directories(self):
        self.logger.info("Setting up directories...")

        dirs = [
            "/etc/slurm",
            "/var/spool/slurmctld",
            "/var/spool/slurmd",
            "/var/log/slurm",
            "/run/slurm"
        ]

        for d in dirs:
            self.run(["sudo", "mkdir", "-p", d])

        self.run(["sudo", "chown", "-R", "slurm:slurm", "/var/spool/slurmctld"])
        self.run(["sudo", "chown", "-R", "slurm:slurm", "/var/spool/slurmd"])
        self.run(["sudo", "chown", "-R", "slurm:slurm", "/var/log/slurm"])
        self.run(["sudo", "chown", "-R", "slurm:slurm", "/run/slurm"])


    def create_slurm_conf(self):
        self.logger.info("Creating slurm.conf...")

        hostname = subprocess.check_output(["hostname"], text=True).strip()
        cpu_count = os.cpu_count()

        config = f"""
ClusterName=cluster
SlurmctldHost={hostname}

SlurmUser=slurm
StateSaveLocation=/var/spool/slurmctld
SlurmdSpoolDir=/var/spool/slurmd

AuthType=auth/munge
ProctrackType=proctrack/linuxproc

NodeName={hostname} CPUs={cpu_count} State=UNKNOWN
PartitionName=debug Nodes={hostname} Default=YES MaxTime=INFINITE State=UP
"""

        with open("/tmp/slurm.conf", "w") as f:
            f.write(config)

        self.run(["sudo", "mv", "/tmp/slurm.conf", "/etc/slurm/slurm.conf"])


    def install_systemd_services(self):
        source_dir = f"{self.WORKDIR}/slurm-{self.VERSION}"

        self.run(["sudo", "cp", f"{source_dir}/etc/slurmctld.service", "/etc/systemd/system/"])
        self.run(["sudo", "cp", f"{source_dir}/etc/slurmd.service", "/etc/systemd/system/"])
        self.run(["sudo", "systemctl", "daemon-reload"])

    def enable_services(self):
        self.run(["sudo", "systemctl", "enable", "slurmctld"])
        self.run(["sudo", "systemctl", "enable", "slurmd"])
        self.run(["sudo", "systemctl", "start", "slurmctld"])
        self.run(["sudo", "systemctl", "start", "slurmd"])


    def verify(self):
        self.logger.info("Verifying Slurm...")

        result = subprocess.run(
            [f"{self.PREFIX}/bin/sinfo"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            self.logger.info("Slurm Installed Successfully")
            self.logger.info(result.stdout)
        else:
            self.logger.error(result.stderr)
            raise Exception("Verification failed")

    def install(self):
        try:
            self.logger.info("=== SLURM INSTALL STARTED ===")

            detector = OSDetector()
            pkg_manager = detector.detect()["package_manager"]

            self.install_dependencies(pkg_manager)
            self.enable_munge()
            self.download_and_build()

            self.create_module()  

            self.create_command_symlinks()
            self.create_slurm_user()
            self.setup_directories()
            self.create_slurm_conf()
            self.install_systemd_services()
            self.enable_services()
            self.verify()

            self.logger.info("=== SLURM INSTALL SUCCESS ===")

        except Exception:
            self.logger.exception("SLURM INSTALL FAILED")
            raise


if __name__ == "__main__":
    SlurmInstaller().install()
