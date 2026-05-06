import os
import shutil


class STREAMRemover:

    def __init__(self):
        self.src_dir = os.path.expanduser("~/STREAM")
        self.run_dir = os.path.expanduser("~/hpc_runs/stream")

    def remove_source(self):
        print("Removing STREAM source/build/install...")

        if os.path.exists(self.src_dir):
            shutil.rmtree(self.src_dir, ignore_errors=True)
            print("✔ Removed ~/STREAM")
        else:
            print("STREAM not found.")

    def remove_runs(self):
        print("Removing STREAM run outputs...")

        if os.path.exists(self.run_dir):
            shutil.rmtree(self.run_dir, ignore_errors=True)
            print("✔ Removed ~/hpc_runs/stream")
        else:
            print("No run outputs found.")

    def remove(self):
        print("\n===== Removing STREAM =====\n")

        self.remove_source()
        self.remove_runs()

        print("\n===== STREAM completely removed =====\n")


if __name__ == "__main__":
    remover = STREAMRemover()
    remover.remove()