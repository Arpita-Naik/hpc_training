class Parser:
    def __init__(self, cfg, app):
        self.cfg = cfg
        self.app = app

    def get_paths(self):
        paths = self.cfg["build"].get("paths", {})
        return {
            "base_dir": paths.get("base_dir"),
            "run_dir": paths.get("run_dir")
        }

    def get_app_config(self):
        return self.cfg[self.app]

    def get_runtime(self):
        return self.cfg[self.app]["runtime"]

    def get_problem(self):
        return self.cfg[self.app]["problem"]

    # ✅ ADD THIS
    def get_process_grid(self):
        return self.cfg[self.app]["process_grid"]
    