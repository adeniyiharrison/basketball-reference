PSQL_URL="postgres://pguser:pgpass@localhost:5432/basketball-reference"
MIGRATE_PSQL_URL="postgres://pguser:pgpass@localhost:5432/basketball-reference?sslmode=disable&x-multi-statement=true"

migrate.up:
	migrate -database ${MIGRATE_PSQL_URL} -path migrations -verbose up

migrate.down:
	migrate -database ${MIGRATE_PSQL_URL} -path migrations -verbose down

db.setup:
	docker compose up postgres -d
	sleep 3
	migrate.up
