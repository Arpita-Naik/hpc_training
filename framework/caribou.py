# caribou.py
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.parser_cli import ParserCLI
from core.run_manager import RunManager

def main():
    cli = ParserCLI()
    args = cli.parse()

    manager = RunManager(args)
    manager.run()

if __name__ == "__main__":
    main()