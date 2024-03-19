set_local_env:
	export $(grep -v '^#' .envs/local.env | xargs)

alembic_upgrade:
	alembic upgrade head

local_migrations: set_local_env alembic_upgrade

rollback_one_migrations:
	alembic downgrade -1

up-services:
	docker-compose --env-file .envs/local.env up -d postgres

