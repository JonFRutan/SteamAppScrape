.phony: default
default:
	type Makefile

up:
	docker-compose up -d

down:
	docker-compose down

config:
	docker-compose config

scrape:
	poetry run python scraper/scrape.py

install:
	poetry install

update:
	poetry install --no-root
