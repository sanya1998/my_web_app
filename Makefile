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


set_base_env:
	export $(grep -v '^#' envs/base.env | xargs)

alembic_create_first_revision:
	alembic revision --autogenerate -m "Initial migration"

alembic_upgrade_head:
	alembic upgrade head

alembic_downgrade_1:
	alembic downgrade -1

create_first_migration_base: set_base_env alembic_create_first_revision

forward_migrations_head_base: set_base_env alembic_upgrade_head

rollback_one_migration_base: set_base_env alembic_downgrade_1


up-celery-worker:
	celery --app app.resources.celery_:celery worker --loglevel=INFO --pool=solo

up-celery-flower:
	celery --app app.resources.celery_:celery flower

clear-celery-tasks:
	celery -A app.resources.celery_:celery purge


up-related-services:
	docker-compose --env-file envs/base.env -f docker/docker-compose.yaml -p "my-web-services" up -d postgres redis celery-worker celery-flower


up-base-app:
	docker-compose --env-file envs/base.env -f docker/docker-compose.yaml -p "my-web-app" up -d api


run-tests:
	pytest -v -s --envfile=envs/test.env
