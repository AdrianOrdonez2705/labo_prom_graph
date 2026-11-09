# TSI — LAB EC3: Observabilidad, incidente y rollback (individual)

**Objetivo:** comparar Proxmox (hipervisor KVM/LXC) con la capa Docker y ejecutar un caso real de operación: API de inferencia + Prometheus + Grafana + incidente + recuperación de una imagen anterior.

**No se instalan aplicaciones nuevas en Windows.** Se reutiliza Docker Desktop + Docker Compose (Linux containers), navegador y PowerShell. Las imágenes y paquetes se descargan dentro del entorno Docker al construir. VirtualBox NO es necesario para este laboratorio. El primer arranque puede requerir Internet y varios GB de almacenamiento.

## Estructura
- `app/`: API FastAPI, métricas, logs JSON y clasificador Naive Bayes didáctico.
- `assets/`: dataset **sintético** y artefacto entrenado en JSON.
- `monitoring/`: Prometheus (scrape + reglas) y Grafana (data source + dashboard), ya configurados.
- `scripts/`: tráfico, entrenamiento y scripts PowerShell opcionales.
- `compose.yaml`: release estable v1.0 y servicios de monitoreo.
- `compose.incident.yaml`: release defectuoso v1.1, conservando monitoreo.
- `docs/`: pauta individual y rúbrica.

## 1. Preparación (PowerShell, carpeta del proyecto)
```powershell
docker version
docker compose version
# Si faltan imágenes, Docker las descargará. No hace falta pip/npm en Windows.
docker build --build-arg RELEASE_VERSION=1.0.0 --build-arg INCIDENT_MODE=off -t tsi-ec3-api:1.0 .
docker build --build-arg RELEASE_VERSION=1.1.0 --build-arg INCIDENT_MODE=degraded -t tsi-ec3-api:1.1 .
```

## 2. Despliegue estable
```powershell
docker compose up -d
docker compose ps
docker compose run --rm --no-deps traffic --count 40 --delay 0.1
docker compose logs --tail 15 api
```
Abrir:
- API: http://localhost:8000/docs
- Salud: http://localhost:8000/health
- Métricas: http://localhost:8000/metrics
- Prometheus targets: http://localhost:9090/targets
- Alertas: http://localhost:9090/alerts
- Grafana: http://localhost:3000 (Dashboards > Laboratorio TSI > **TSI EC3 | Observabilidad de inferencia**)

## 3. Incidente reproducible (release v1.1)
```powershell
docker compose -f compose.yaml -f compose.incident.yaml up -d --no-deps --force-recreate api
docker compose run --rm --no-deps traffic --count 60 --delay 0.1
docker compose logs --tail 25 api
```
La v1.1 introduce 650 ms de latencia en inferencia y respuestas HTTP 503 en aproximadamente 1 de cada 3 llamadas. **Es un defecto de release empaquetado intencionalmente en otra imagen**, no un daño real ni un ataque.

## 4. Rollback real a la imagen estable
```powershell
docker compose -f compose.yaml up -d --no-deps --force-recreate api
docker compose run --rm --no-deps traffic --count 40 --delay 0.1
docker compose ps
```
La API vuelve a v1.0 (comprobar `http://localhost:8000/health`). La alerta puede tardar aproximadamente un minuto en desaparecer porque usa tasas móviles de 1 minuto.

## 5. Apagado
```powershell
docker compose down
```
`down` detiene y elimina contenedores/redes; no borra las imágenes construidas. **No utilizar `down -v` sin entender sus efectos sobre volúmenes de otros proyectos.**

## 6. Problemas frecuentes
- `Cannot connect to Docker daemon`: iniciar Docker Desktop y cambiar a Linux containers si corresponde.
- `port already allocated` 8000/9090/3000: detener el otro servicio o pedir al docente una variante de puertos.
- Grafana sin métricas: revisar `http://localhost:9090/targets` (debe decir UP), esperar al menos 10–20 segundos y generar tráfico.
- Prometheus alerta no aparece: comprobar versión v1.1 en `/health`, generar 60 solicitudes, esperar 5–15 segundos, revisar `/alerts`.
- Gráficos aún muestran valores viejos después del rollback: ventana de 1 minuto y retención de series; esperar y generar tráfico normal.
- PowerShell impide `.ps1`: ejecutar los comandos del README uno por uno; los scripts son solo atajos opcionales.
- Computador con pocos recursos: ejecutar primero solo `api` y `prometheus`, y mostrar Grafana mediante la demostración del docente.

## 7. Seguridad y límites
Las tres interfaces publicadas se enlazan solo a `127.0.0.1`. **No exponer este entorno educativo a Internet ni utilizarlo en producción.** La autenticación anónima de Grafana es SOLO para demostración local. No hay datos personales ni secretos en el proyecto. No se registran cuerpos de solicitudes. Las etiquetas Prometheus evitan IDs únicos (cardinalidad excesiva).

## Fuentes oficiales
- Proxmox: https://proxmox.com/en/products/proxmox-virtual-environment/overview
- Docker Compose: https://docs.docker.com/compose/
- Prometheus: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Grafana provisioning: https://grafana.com/docs/grafana/latest/administration/provisioning/
