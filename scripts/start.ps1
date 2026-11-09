$ErrorActionPreference = 'Stop'
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw 'Falló compose up' }
docker compose ps
