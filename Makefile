set_local_env:
	export $(grep -v '^#' .envs/local.env | xargs)

alembic_upgrade_head:
	alembic upgrade head

alembic_downgrade_1:
	alembic downgrade -1

forward_migrations_head_local: set_local_env alembic_upgrade_head

rollback_one_migration_local: set_local_env alembic_downgrade_1

up-services:
	docker-compose --env-file .envs/local.env up -d postgres
