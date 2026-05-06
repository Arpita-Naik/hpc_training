'''import subprocess
from core.config_loader import load_all_configs
from core.parser import Parser
from performance.graphs import plot_performance


class RunManager:

    def __init__(self, args):
        self.app = args.app
        self.do_build = args.build
        self.do_run = args.run
        self.plot = args.plot

        cfg = load_all_configs(self.app)
        self.parser = Parser(cfg, self.app)

    def run(self):

        paths = self.parser.get_paths()
        print("[RunManager] Paths:", paths)

        if self.plot:
            if self.app == "stream":
                plot_performance(
                    "performance/data/stream_history.json",
                    "triad",
                    "STREAM Performance Trend"
                )

            elif self.app == "hpl":
                plot_performance(
                    "performance/data/hpl_history.json",
                    "gflops",
                    "HPL Performance Trend"
                )

            return  

        if self.do_build and not self.do_run:
            mode = "build"

        elif self.do_run and not self.do_build:
            mode = "run"

        else:
            mode = "all"

        print(f"[RunManager] Mode: {mode}")

        self._execute_app(mode)

    def _execute_app(self, mode):

        if self.app == "stream":
            subprocess.run([
                "python3",
                "-m",
                "hpc_apps.stream.stream",
                mode
            ])

        elif self.app == "hpl":
            subprocess.run([
                "python3",
                "-m",
                "hpc_apps.hpl.hpl",
                mode
            ])

        else:
            print("Invalid app")'''

            
from core.config_loader import load_all_configs
from core.parser import Parser


class RunManager:

    def __init__(self, args):
        self.app = args.app
        self.do_build = args.build
        self.do_run = args.run
        self.plot = args.plot  
        self.profile = bool(args.profile)

        cfg = load_all_configs(self.app)
        self.parser = Parser(cfg, self.app)

    def run(self):

        paths = self.parser.get_paths()
        print("[RunManager] Paths:", paths)
        print(f"[RunManager] Profiling: {self.profile}")
        if self.plot:

            if self.app == "stream":

                if self.plot == "avg":
                    from performance.graphs import plot_avg_history
                    plot_avg_history()

                elif self.plot == "iterations":
                    from performance.graphs import plot_last_iterations
                    plot_last_iterations()

            elif self.app == "hpl":
                if self.plot == "avg":
                    from performance.graphs import plot_hpl_avg
                    plot_hpl_avg()

                elif self.plot == "iterations":
                    from performance.graphs import plot_hpl_last_iterations
                    plot_hpl_last_iterations()
            return

        if self.do_build and not self.do_run:
            mode = "build"
        elif self.do_run and not self.do_build:
            mode = "run"
        else:
            mode = "all"

        print(f"[RunManager] Mode: {mode}")

        self._execute_app(mode)

    def _execute_app(self, mode):

        if self.app == "stream":
            from hpc_apps.stream import stream
            stream.execute(self.parser, mode,self.profile)

        elif self.app == "hpl":
            from hpc_apps.hpl import hpl
            hpl.execute(self.parser, mode,self.profile)

        else:
            print("Invalid app")