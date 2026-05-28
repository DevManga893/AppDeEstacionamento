VENV = .venv

ifeq ($(OS),Windows_NT)
    PYTHON = $(VENV)/Scripts/python
    PYTEST = $(VENV)/Scripts/pytest
else
    PYTHON = $(VENV)/bin/python
    PYTEST = $(VENV)/bin/pytest
endif

.PHONY: all setup build run test

all: setup build run

setup: $(VENV)
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e package/sistema

build:
	$(PYTHON) -m build package/sistema -o static/packages

run:
	$(PYTHON) -m fastapi dev

test:
	$(PYTEST) package/sistema/tests/ -v

$(VENV):
	python -m venv $(VENV)
