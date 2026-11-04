import sys

from .ui.cli import run_cli_game


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    run_cli_game()
