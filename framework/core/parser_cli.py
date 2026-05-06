import argparse
class ParserCLI:
    def parse(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("app", help="hpl or stream")
        parser.add_argument("--build", action="store_true")
        parser.add_argument("--run", action="store_true")
        parser.add_argument("--plot", choices=["avg", "iterations"])
        parser.add_argument("--profile",action="store_true",help="Enable performance profiling")
        return parser.parse_args()