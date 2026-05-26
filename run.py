import argparse
import sys
from os import system
from pathlib import Path

VENV = Path(".venv")

BIN = VENV / ("Scripts" if sys.platform == "win32" else "bin")
PYTHON = BIN / "python"

def setup():
    if not VENV.exists():
        system("python -m venv .venv")

    system(f"{PYTHON} -m pip install -r requirements.txt")
    system(f"{PYTHON} -m pip install -e package/sistema")

def build():
    system(f"{PYTHON} -m build package/sistema -o static/packages")

def run():
    system(f"{PYTHON} -m fastapi dev")

def all_targets():
    setup()
    build()
    run()

TARGETS = {
    "setup": setup,
    "build": build,
    "run": run,
    "all": all_targets,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build script do estacionamento")

    parser.add_argument(
        "target",
        nargs="?",
        default="all",
        choices=TARGETS,
        help="Target a executar (padrão: all)",
    )

    args = parser.parse_args()
    
    TARGETS[args.target]()