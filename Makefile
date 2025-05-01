.phony: default

default:
	type Makefile

scrape:
	poetry run python scraper/scrape.py

install:
	poetry install

update:
	poetry install --no-root
