import os


def expand_path(path):
    return os.path.expanduser(path)


def create_run_dir(base_dir, naming, run_id):
    base_dir = expand_path(base_dir)

    name = naming.replace("{id}", str(run_id))
    path = os.path.join(base_dir, name)

    os.makedirs(path, exist_ok=True)

    return path


def print_banner(title):
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50 + "\n")