$ErrorActionPreference = 'Stop'
Write-Host 'TSI EC3 / Comprobaciones de entorno local'
$health = Invoke-RestMethod -Uri 'http://localhost:8000/health' -TimeoutSec 10
if ($health.status -ne 'ok') { throw 'API /health sin respuesta OK' }
Write-Host ('API OK | version ' + $health.version)
$targets = Invoke-RestMethod -Uri 'http://localhost:9090/api/v1/targets' -TimeoutSec 10
$active = @($targets.data.activeTargets)
if (@($active | Where-Object { $_.labels.job -eq 'tsi_api' -and $_.health -eq 'up' }).Count -lt 1) {
    throw 'Prometheus no reporta tsi_api como UP. Revise http://localhost:9090/targets'
}
Write-Host 'Prometheus OK | tsi_api UP'
$grafana = Invoke-RestMethod -Uri 'http://localhost:3000/api/health' -TimeoutSec 10
Write-Host ('Grafana responde | database=' + $grafana.database)
Write-Host 'Prueba correcta: tres componentes accesibles. No significa que /predict no tenga fallos.'
