UID = $(shell id -u)
DC = docker compose


# First installation of the project
install:
	docker network create laughing_octo_pancake_backend
	make build
	${DC} run django python manage.py migrate

# Format python files.
format:
	${DC} run --no-deps --user ${UID} django bash -c "ruff check --fix . && ruff format ."

# Build docker images.
build:
	${DC} build --pull

# Run django tests.
test:
	${DC} run django python manage.py test -v 3 $(arg)

# Exec bash shell on django container.
shell:
	${DC} run --user ${UID} --rm django bash

# Start project.
start:
	${DC} up --remove-orphans

# Run code coverage.
coverage:
	${DC} run --user ${UID} django bash -c " \
		coverage run ./manage.py test --keepdb && \
		coverage report --show-missing && \
		coverage html \
	"

service:
	mkdir -p /tmp/sqlite3/ && chown -R 1000:1000 /tmp/sqlite3 \
	&& docker run --rm -p 5000:5000 -v /tmp/sqlite3/:/app/sqlite3/ \
	ldnunespwf/dev-recruiting-challenge-monitor:latest