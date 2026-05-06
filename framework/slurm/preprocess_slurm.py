import subprocess
import shutil
import os

class SlurmPreprocessor:

    def command_exists(self, command):
        """Check if a command exists in PATH"""
        if shutil.which(command):
            return True
        
        slurm_path=f"/opt/hpc/slurm/bin/{command}"
        if os.path.exists(slurm_path):
            return True
        return False

    def is_service_active(self, service):
        """Check if a systemd service is active"""
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", service],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0

    def service_exists(self, service):
        """Check if a systemd service exists"""
        result = subprocess.run(
            ["systemctl", "list-unit-files"],
            capture_output=True,
            text=True
        )
        return service in result.stdout

    def clean_broken_state(self):
        print("⚠ Detected broken Slurm environment.")
        print("Cleaning runtime leftovers (not uninstalling packages)...")
        subprocess.run(["sudo", "systemctl", "stop", "slurmctld.service"],
                       stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "systemctl", "stop", "slurmd.service"],
                       stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "systemctl", "stop", "munge.service"],
                       stderr=subprocess.DEVNULL)

        subprocess.run(["sudo", "rm", "-rf", "/var/spool/slurm"],
                       stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "rm", "-rf", "/var/run/munge"],
                       stderr=subprocess.DEVNULL)

        print("✔ Broken runtime cleaned successfully.")


    def check(self):
        print("===== CHECKING SLURM STATUS =====")

        if not self.command_exists("sinfo"):
            print("Slurm not installed.")
            return "not_installed"

        print("Slurm command found.")

        if not self.service_exists("slurmctld.service"):
            print("Slurm partially installed (service file missing).")
            self.clean_broken_state()
            return "broken_cleaned"

        if not self.is_service_active("munge.service"):
            print("Munge service not running.")
            self.clean_broken_state()
            return "broken_cleaned"

        if self.is_service_active("slurmctld.service"):
            print("✔ Slurm is running properly.")
            return "installed"

        print("Slurm installed but not active.")
        self.clean_broken_state()
        return "broken_cleaned"
    
if __name__ == "__main__":
    preprocessor = SlurmPreprocessor()
    status = preprocessor.check()
    print(f"Detected status: {status}")