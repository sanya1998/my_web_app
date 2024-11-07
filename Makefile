flake8-check:
	flake8 --config=linters/.flake8

black-check:
	black . --config linters/.black --check --diff

isort-check:
	isort . --settings-file linters/.isort --check-only  --diff

black:
	black . --config linters/.black

isort:
	isort . --settings-file linters/.isort

linters-check: isort-check black-check flake8-check

linters: black isort flake8-check

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
	celery --app app.resources.celery:celery worker --loglevel=INFO --pool=solo

up-celery-flower:
	celery --app app.resources.celery:celery flower

up-services:
	docker-compose --env-file envs/local.env up -d postgres redis
