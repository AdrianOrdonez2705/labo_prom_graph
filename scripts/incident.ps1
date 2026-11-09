$ErrorActionPreference = 'Stop'
docker compose -f compose.yaml -f compose.incident.yaml up -d --no-deps --force-recreate api
if ($LASTEXITCODE -ne 0) { throw 'Falló la liberación defectuosa' }
docker compose -f compose.yaml -f compose.incident.yaml ps api
