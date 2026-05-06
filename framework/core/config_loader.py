import yaml
import os

BASE = os.path.join(os.path.dirname(__file__), "../yaml_inputs")
BASE = os.path.abspath(BASE)


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_all_configs(app):
    build = load_yaml(os.path.join(BASE, "build_recipe.yaml"))
    run = load_yaml(os.path.join(BASE, app, "run_recipe.yaml"))

    return {
        "build": build["build"],
        app: run[app]
    }