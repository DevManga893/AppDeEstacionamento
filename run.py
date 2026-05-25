import argparse
from os import system
from pathlib import Path

VENV = Path(".venv")
PIP = VENV / "bin" / "pip"
PYTHON = VENV / "bin" / "python"
FASTAPI = VENV / "bin" / "fastapi"

def setup():
    if not VENV.exists():
        system("python -m venv .venv")

    system(f"{PIP} install -r requirements.txt")
    system(f"{PIP} install -e package/sistema")

def build():
    system(f"{PYTHON} -m build package/sistema -o static/packages")

def run():
    system(f"{FASTAPI} dev")

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
