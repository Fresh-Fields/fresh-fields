SHELL = /bin/bash

default: runall

setup:
	@echo "------ setting up vite ------"
	@cd vite && npm i
	@echo "------- entering venv -------"
	@source bin/activate
	@echo "-- installing requirements --"
	@pip install -r requirements.txt -r ml/requirements.txt
	@echo "-- preparing sample dataset --"
	@cd ml && make build && make generate
	@echo "----------- done! -----------"

build:
	@python splice.rec.data.py
	@cd vite && npm run build

run:
	@python app.py

# runall doesn't run setup
# the name runall is a lie
runall:
	@make build && make run

update:
	@git submodule update
	@cd vite && npm i
