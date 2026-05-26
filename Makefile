VENV = .venv

ifeq ($(OS),Windows_NT)
    PYTHON = $(VENV)/Scripts/python
else
    PYTHON = $(VENV)/bin/python
endif

.PHONY: all setup build run

all: setup build run

setup: $(VENV)
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e package/sistema

build:
	$(PYTHON) -m build package/sistema -o static/packages

run:
	$(PYTHON) -m fastapi dev

$(VENV):
	python -m venv $(VENV)