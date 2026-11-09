$ErrorActionPreference = 'Stop'
docker build --build-arg RELEASE_VERSION=1.0.0 --build-arg INCIDENT_MODE=off -t tsi-ec3-api:1.0 .
if ($LASTEXITCODE -ne 0) { throw 'No se pudo construir v1.0' }
docker build --build-arg RELEASE_VERSION=1.1.0 --build-arg INCIDENT_MODE=degraded -t tsi-ec3-api:1.1 .
if ($LASTEXITCODE -ne 0) { throw 'No se pudo construir v1.1' }
Write-Host 'Imagenes preparadas; compruebe con docker images tsi-ec3-api'
