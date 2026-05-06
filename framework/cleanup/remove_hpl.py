import os
import shutil
import sys
import subprocess


class HPLRemover:

    def __init__(self):
        self.src_dir = os.path.expanduser("~/hpl-2.3")
        self.run_dir = os.path.expanduser("~/hpc_runs/hpl")

    def remove_source(self):
        print("Removing HPL source...")

        if os.path.exists(self.src_dir):
            shutil.rmtree(self.src_dir, ignore_errors=True)
            print("✔ Removed ~/hpl-2.3")
        else:
            print("HPL source not found.")

    def remove_runs(self):
        print("Removing HPL run outputs...")

        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir, ignore_errors=True)
            print("✔ Removed ~/hpc_runs/hpl")
        else:
            print("No run outputs found.")

    def remove(self):
        print("\n===== Removing HPL =====\n")

        self.remove_source()
        self.remove_runs()

        print("\n===== HPL completely removed =====\n")


if __name__ == "__main__":
    remover = HPLRemover()
    remover.remove()