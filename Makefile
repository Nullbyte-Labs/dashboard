.PHONY: install build serve deploy clean

install:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

build:
	.venv/bin/python build.py

serve:
	.venv/bin/python build.py --serve

deploy: build
	docker compose up -d --force-recreate web

clean:
	rm -rf site
