SHELL:=bash
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(dir $(mkfile_path))

.PHONY: help html lint start purge stop recreate test maploom migrations

help:
	@echo "  make lint       - run to lint (style check) repo"
	@echo "  make html       - build sphinx documentation"
	@echo "  make start      - start containers"
	@echo "  make stop       - stop containers"
	@echo "  make purge      - stop containers and prune volumes"
	@echo "  make recreate   - stop containers, prune volumes and recreate/build containers"
	@echo "  make test       - run unit tests"
	@echo "  make maploom    - build maploom"
	@echo "  make migrations - create django migrations"

html:
	@docker run --rm -v $(current_dir):/code \
	                 -w /code quay.io/boundlessgeo/bex-py27-stretch bash \
	                 -e -c 'python setup.py build_sphinx'

lint:
	@docker run --rm -v $(current_dir):/code \
	                 -w /code quay.io/boundlessgeo/sonar-maven-py3-alpine bash \
	                 -e -c '. docker/devops/helper.sh && lint'

stop:
	@docker-compose down --remove-orphans

start: stop maploom
	@docker-compose up -d --build

purge: stop
	@docker volume prune -f

recreate: purge
	@docker-compose up -d --build --force-recreate

test: migration-check
	@echo "Note: test requires the exchange container to be running and healthy"
	@docker-compose exec exchange /code/docker/exchange/run_tests.sh

maploom:
	@docker run --rm -v $(current_dir):/code \
	                 -w /code quay.io/boundlessgeo/bex-nodejs-bower-grunt bash \
	                 -e -c '. docker/devops/helper.sh && build-maploom'

migration-check:
	@docker-compose exec -T exchange /bin/bash \
	                     -c '. docker/devops/helper.sh && makemigrations-check'

migrations:
	@docker-compose exec -T exchange /bin/bash \
	                     -c 'python manage.py makemigrations'
