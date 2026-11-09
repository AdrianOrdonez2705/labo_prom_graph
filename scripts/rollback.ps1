$ErrorActionPreference = 'Stop'
docker compose -f compose.yaml up -d --no-deps --force-recreate api
if ($LASTEXITCODE -ne 0) { throw 'Falló el rollback' }
docker compose ps api
