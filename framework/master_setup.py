import os
import sys
import time
import subprocess

from system_check.detect_os import OSDetector
from slurm.preprocess_slurm import SlurmPreprocessor
from slurm.install_slurm import SlurmInstaller
from modules.install_python_module import PythonInstaller
from modules.install_openmpi_module import OpenMPIInstaller
from cleanup.master_cleanup import HPCCleanup
from modules.setup_modules import setup as setup_modules

class HPCFramework:

    def check_root(self):
        if os.geteuid() != 0:
            print("Run as root: sudo python3 master_setup.py")
            sys.exit(1)

    def verify_munge(self):
        print("Verifying Munge...")

        if subprocess.run(
            ["systemctl", "is-active", "--quiet", "munge"]
        ).returncode!= 0:
            subprocess.run(["systemctl", "restart", "munge"])

        if subprocess.run(
            ["systemctl", "is-active", "--quiet", "munge"]
        ).returncode != 0:
            print("Munge failed. Stopping setup.")
            sys.exit(1)

        print("✔ Munge running.")

    def verify_slurm(self):
        print("Verifying Slurm...")
        time.sleep(2)

        result = subprocess.run(
            ["sinfo"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✔ Slurm responding correctly.")
            print(result.stdout)
        else:
            print("Slurm installed but not responding.")

    '''def submit_job(self):
        print("Submitting Slurm Job...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        job_file = os.path.join(base_dir, "se.sh")

        if not os.path.exists(job_file):
            print("Job file se.sh not found in current directory.")
            return

        result = subprocess.run(
            ["sbatch", job_file],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✔ Job Submitted Successfully")
            print(result.stdout)
        else:
            print("Job submission failed.")
            print(result.stderr)

    def run_cleanup(self):
        print("Running Master Cleanup...")

        cleaner = HPCCleanup()
        cleaner.cleanup()

        print("✔ Cleanup completed.")'''

    def setup(self):

        print("===== HPC FRAMEWORK START =====")

        self.check_root()

        detector = OSDetector()
        detector.detect()

        print("===== OS CHECK COMPLETE =====")

        preprocessor = SlurmPreprocessor()
        slurm_status = preprocessor.check()

        print("--------------------------------")

        if slurm_status == "installed":
            print("Slurm fully configured. Skipping installation.")

        elif slurm_status in ["broken_cleaned", "not_installed"]:
            print("Installing Slurm...")
            SlurmInstaller().install()

        else:
            print("Unknown Slurm status.")
            sys.exit(1)

        print("--------------------------------")
        self.verify_munge()

        #print("--------------------------------")
        #print("Setting up Python...")
        #PythonInstaller().install()

        print("--------------------------------")
        print("Setting up OpenMPI...")
        OpenMPIInstaller().install()
        print("--------------------------------")
        print("Configuring Environment Modules...")
        setup_modules()
        print("--------------------------------")

        self.verify_slurm()

        print("--------------------------------")

        #self.submit_job()

        print("--------------------------------")

        #self.run_cleanup()

        print("===== HPC FRAMEWORK SETUP COMPLETE =====")


if __name__ == "__main__":
    HPCFramework().setup()