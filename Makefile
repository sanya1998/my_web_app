black-check:
	black . --config linters/.black --check --diff --color

isort-check:
	isort . --settings-file linters/.isort --check-only  --diff

flake8-check:
	flake8 --config=linters/.flake8

autoflake-check:
	autoflake . --config linters/.autoflake

black:
	black . --config linters/.black

isort:
	isort . --settings-file linters/.isort

# TODO: verbose не работает на этом примере
autoflake:
	autoflake . --config linters/.autoflake --in-place

pyright:
	pyright

#linters-check: black-check isort-check autoflake-check flake8-check  # autoflake долгий
linters-check: black-check isort-check flake8-check

# autoflake лечит не все проблемы, которые находит flake, поэтому вызывается flake8-check
#linters: autoflake isort black flake8-check # autoflake долгий
linters: isort black flake8-check


set_local_env:
	export $(grep -v '^#' envs/local.env | xargs)

alembic_create_first_revision:
	alembic revision --autogenerate -m "Initial migration"

alembic_upgrade_head:
	alembic upgrade head

alembic_downgrade_1:
	alembic downgrade -1

create_first_migration_local: set_local_env alembic_create_first_revision

forward_migrations_head_local: set_local_env alembic_upgrade_head

rollback_one_migration_local: set_local_env alembic_downgrade_1


up-celery-worker:
	celery --app app.resources.celery_:celery worker --loglevel=INFO --pool=solo

up-celery-flower:
	celery --app app.resources.celery_:celery flower

clear-celery-tasks:
	celery -A app.resources.celery_:celery purge


docker-stop:
	docker stop my_web_app_container

docker-remove-container:
	docker rm my_web_app_container

docker-remove-image:
	docker rmi my_web_app_image

docker-build-image:
	docker build -t my_web_app_image .

help-for-using:
	echo "Use on host: http://0.0.0.0:8020"

docker-run:
	docker run --name my_web_app_container -p 8020:8010 my_web_app_image

docker-build-and-start: docker-build-image help-for-using docker-run

docker-rebuild-and-start: docker-stop docker-remove-container docker-remove-image docker-build-and-start

docker-start:
	docker start -i my_web_app_container


up-services:
	docker-compose --env-file envs/local.env up -d postgres redis

run-tests:
	pytest -v -s --envfile=envs/test.env
