import os
import sys

from .remove_python_env import PythonRemover
from .remove_openmpi import OpenMPIRemover
from .remove_gcc import GCCRemover
from .remove_slurm import SlurmRemover


class HPCCleanup:

    def remove_user_modules(self):
        print("Removing user-level HPC modules...")

        PythonRemover().remove()
        OpenMPIRemover().remove()
        GCCRemover().remove()

    def remove_slurm(self):
        print("Removing Slurm (system-level)...")

        if os.geteuid() != 0:
            print("⚠ Slurm removal requires root.")
            print("Please run with: sudo python3 master_cleanup.py")
            sys.exit(1)

        SlurmRemover().remove()

    def cleanup(self):
        print("===== HPC CLEANUP START =====")
        self.remove_user_modules()
        self.remove_slurm()

        print("===== CLEANUP COMPLETE =====")


if __name__ == "__main__":
    HPCCleanup().cleanup()