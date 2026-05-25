VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

.PHONY: all setup build run

all: setup build run

setup: $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -e package/sistema

build:
	$(PYTHON) -m build package/sistema -o static/packages

run:
	$(VENV)/bin/fastapi dev

$(VENV):
	python -m venv $(VENV)