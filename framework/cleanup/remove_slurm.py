'''import os
import subprocess
class SlurmRemover:

    PREFIX = "/opt/hpc/slurm"

    def run(self, command, ignore_error=False):
        print("Running:", " ".join(command))
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            if not ignore_error:
                raise

    def stop_services(self):
        print("==== Stopping Slurm Services ====")

        services = ["slurmctld", "slurmd", "munge"]

        for service in services:
            self.run(["sudo", "systemctl", "stop", service], ignore_error=True)
            self.run(["sudo", "systemctl", "disable", service], ignore_error=True)

    def remove_service_files(self):
        print("==== Removing systemd Service Files ====")

        service_files = [
            "/etc/systemd/system/slurmctld.service",
            "/etc/systemd/system/slurmd.service"
        ]

        for file in service_files:
            if os.path.exists(file):
                self.run(["sudo", "rm", "-f", file])

        self.run(["sudo", "systemctl", "daemon-reload"])

    def remove_command_symlinks(self):
        print("==== Removing Slurm command symlinks ====")
        binaries = ["sinfo","squeue","sbatch","scancel","scontrol"]
        for cmd in binaries:
            link = f"/usr/local/bin/{cmd}"
            if os.path.islink(link):
                self.run(["sudo", "rm", "-f", link])


    def remove_installation(self):
        print("==== Removing Slurm Installation Directory ====")

        if os.path.exists(self.PREFIX):
            self.run(["sudo", "rm", "-rf", self.PREFIX])


    def remove_runtime_files(self):
        print("==== Removing Slurm Runtime Files ====")

        paths = [
            "/etc/slurm",
            "/var/spool/slurmctld",
            "/var/spool/slurmd",
            "/var/log/slurm",
            "/run/slurm"
        ]

        for path in paths:
            if os.path.exists(path):
                self.run(["sudo", "rm", "-rf", path])

    def remove_profile(self):
        print("==== Removing PATH Configuration ====")

        profile_file = "/etc/profile.d/slurm.sh"

        if os.path.exists(profile_file):
            self.run(["sudo", "rm", "-f", profile_file])

    def remove_ldconfig(self):
        print("==== Cleaning Linker Cache ====")

        conf_file = "/etc/ld.so.conf.d/slurm.conf"

        if os.path.exists(conf_file):
            self.run(["sudo", "rm", "-f", conf_file])

        self.run(["sudo", "ldconfig"], ignore_error=True)

    def remove_munge(self):
        print("==== Removing Munge Authentication ====")
        paths = [
            "/etc/munge/munge.key",
            "/var/run/munge",
            "/var/lib/munge",
            "/var/log/munge"
            ]
        for path in paths:
            if os.path.exists(path):
                self.run(["sudo", "rm", "-rf", path])
        self.run(["sudo", "apt", "remove", "-y", "munge", "libmunge-dev"], ignore_error=True)
        self.run(["sudo", "apt", "autoremove", "-y"], ignore_error=True)

    def remove_slurm_user(self):
        print("==== Removing Slurm User ====")

        self.run(["sudo", "userdel", "-r", "slurm"], ignore_error=True)

    def remove(self):
        self.stop_services()
        self.remove_service_files()
        self.remove_command_symlinks()
        self.remove_installation()
        self.remove_runtime_files()
        self.remove_profile()
        self.remove_ldconfig()
        self.remove_munge()
        self.remove_slurm_user()

        print("==== Slurm Fully Removed (/opt/hpc/slurm version) ====")


if __name__ == "__main__":
    remover = SlurmRemover()
    remover.remove()'''


import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import setup_logger


class SlurmRemover:

    PREFIX = "/opt/hpc/slurm"
    MODULE_DIR = "/usr/share/modules/modulefiles/slurm"

    def __init__(self):
        self.logger = setup_logger("slurm_remove", "slurm_remove.log")

   
    def run(self, command, ignore_error=False):
        self.logger.info(f"Running: {' '.join(command)}")

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            if not ignore_error:
                self.logger.error(str(e))
                raise

    def stop_services(self):
        self.logger.info("Stopping Slurm services...")

        services = ["slurmctld", "slurmd", "munge"]

        for service in services:
            self.run(["sudo", "systemctl", "stop", service], ignore_error=True)
            self.run(["sudo", "systemctl", "disable", service], ignore_error=True)

    def remove_service_files(self):
        self.logger.info("Removing service files...")

        service_files = [
            "/etc/systemd/system/slurmctld.service",
            "/etc/systemd/system/slurmd.service"
        ]

        for file in service_files:
            if os.path.exists(file):
                self.run(["sudo", "rm", "-f", file])

        self.run(["sudo", "systemctl", "daemon-reload"])

    def remove_command_symlinks(self):
        self.logger.info("Removing symlinks...")

        binaries = ["sinfo", "squeue", "sbatch", "scancel", "scontrol"]

        for cmd in binaries:
            link = f"/usr/local/bin/{cmd}"
            if os.path.islink(link):
                self.run(["sudo", "rm", "-f", link])

    
    def remove_installation(self):
        self.logger.info("Removing installation...")

        if os.path.exists(self.PREFIX):
            self.run(["sudo", "rm", "-rf", self.PREFIX])

    
    def remove_runtime_files(self):
        self.logger.info("Removing runtime files...")

        paths = [
            "/etc/slurm",
            "/var/spool/slurmctld",
            "/var/spool/slurmd",
            "/var/log/slurm",
            "/run/slurm"
        ]

        for path in paths:
            if os.path.exists(path):
                self.run(["sudo", "rm", "-rf", path])

    def remove_module(self):
        self.logger.info("Removing modulefiles...")

        if os.path.exists(self.MODULE_DIR):
            self.run(["sudo", "rm", "-rf", self.MODULE_DIR])
        else:
            self.logger.info("Module directory not found")

    def remove_ldconfig(self):
        self.logger.info("Cleaning linker cache...")

        conf_file = "/etc/ld.so.conf.d/slurm.conf"

        if os.path.exists(conf_file):
            self.run(["sudo", "rm", "-f", conf_file])

        self.run(["sudo", "ldconfig"], ignore_error=True)

    
    def remove_munge(self):
        self.logger.info("Removing Munge...")

        paths = [
            "/etc/munge/munge.key",
            "/var/run/munge",
            "/var/lib/munge",
            "/var/log/munge"
        ]

        for path in paths:
            if os.path.exists(path):
                self.run(["sudo", "rm", "-rf", path])

        self.run(["sudo", "apt", "remove", "-y", "munge", "libmunge-dev"], ignore_error=True)
        self.run(["sudo", "apt", "autoremove", "-y"], ignore_error=True)

    
    def remove_slurm_user(self):
        self.logger.info("Removing slurm user...")
        self.run(["sudo", "userdel", "-r", "slurm"], ignore_error=True)

    def remove(self):
        try:
            self.logger.info("=== SLURM REMOVAL STARTED ===")

            self.stop_services()
            self.remove_service_files()
            self.remove_command_symlinks()
            self.remove_installation()
            self.remove_runtime_files()
            self.remove_module()   
            self.remove_ldconfig()
            self.remove_munge()
            self.remove_slurm_user()

            self.logger.info("=== SLURM REMOVAL COMPLETE ===")

        except Exception:
            self.logger.exception("SLURM REMOVAL FAILED")
            raise


if __name__ == "__main__":
    SlurmRemover().remove()