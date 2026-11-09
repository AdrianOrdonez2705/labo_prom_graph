$ErrorActionPreference = 'Stop'
Write-Host '=== TSI EC3 / verificacion previa ==='
docker version
docker compose version
Write-Host 'Puertos para probar: 8000, 9090 y 3000 (solo localhost)'
Write-Host 'IMPORTANTE: Docker Desktop debe mostrar Engine running; sin descargas activas, verifique conectividad.'
