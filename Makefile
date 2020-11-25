build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

logs:
	docker-compose logs app | tail -100

test:
	pytest --tb=short

watch-tests:
	ls *.py | entr pytest --tb=short

all: down build up test