flake8-check:
	flake8 --config=.flake8

black-check:
	black . --config pyproject.toml --check

isort-check:
	isort -c . --diff

black:
	black . --config pyproject.toml

isort:
	isort .

linters-check: isort-check black-check flake8-check

linters: black isort linters-check

set_local_env:
	export $(grep -v '^#' .envs/local.env | xargs)

alembic_create_first_revision:
	alembic revision --autogenerate -m "Initial migration"

alembic_upgrade_head:
	alembic upgrade head

alembic_downgrade_1:
	alembic downgrade -1

create_first_migration_local: set_local_env alembic_create_first_revision

forward_migrations_head_local: set_local_env alembic_upgrade_head

rollback_one_migration_local: set_local_env alembic_downgrade_1

up-services:
	docker-compose --env-file .envs/local.env up -d postgres
