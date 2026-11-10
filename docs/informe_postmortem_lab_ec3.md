# LAB EC3 - Informe individual y postmortem

**Estudiantes:** Adrian Gonzales Ferreira, Adrián Fabricio Ordóñez Paredes
**Fecha:** 09/11/2026
**Laboratorio:** Observabilidad, incidente y rollback (Prometheus + Grafana + Docker)

> **Cómo leer este informe:** los *hechos* son lo que se ve en las capturas (`evidencias/informe_gonzales_ordonez.pdf`) o en el código del repositorio. 

---

## 1. Arquitectura y relación con Proxmox

**Hardware:** es la base física (servidor con CPU, memoria RAM, discos y tarjetas de red).

**Proxmox:** hipervisor de tipo 1 instalado directamente en el hardware. Gestiona y virtualiza los recursos.

**VM Linux:** máquina virtual con su propio sistema operativo Linux. Da aislamiento y seguridad.

**Docker:** motor de contenedores dentro de la VM Linux. Empaqueta las dependencias de forma ligera y eficiente.

**API:** servicio backend dentro del contenedor Docker. Expone sus funciones por HTTP.

**Observabilidad:** capa transversal que recoge métricas, registros y trazas de las capas anteriores. Sirve para revisar la salud, el rendimiento y el comportamiento en tiempo real.

---

## 2. Pre-flight

- **`docker version` / `docker compose version`: Se encuentra en el documento de evidencia
- **`docker compose ps`: Se encuentra en el documento de evidencia
- **`docker images tsi-ec3-api`** (Evidencia 1, 20:10):

| Imagen | ID | Disco | Contenido |
|---|---|---|---|
| `tsi-ec3-api:1.0` | `54d919ea0e7a` | 209 MB | 50.8 MB |
| `tsi-ec3-api:1.1` | `07a549486a0d` | 209 MB | 50.8 MB |

---

## 3. Estado estable (v1.0)

- **`/health`** (20:20): `status: "ok"`, `version: "1.0.0"`, `incident_mode: "off"`.
- **`/docs`:** la API aparece como "TSI EC3 - API de inferencia (datos sinteticos)" versión 1.0.0, con los endpoints `/`, `/health`, `/predict` y `/metrics`.
- **`/predict`** (20:26): se envió `{"texto": "servidor no responde urgente"}`. Respuesta **200 OK** con `categoria: "critico"`, `score_no_calibrado: 0.96`, `version: "1.0.0"`, `modelo: "naive_bayes_sintetico_v1"` y `request_id: 7494436b7ed3b84e98c57a2f444ad876`.
- **`/metrics`** (20:21): `tsi_http_requests_total` registra 40 respuestas 200 en `POST /predict` y 46 en `GET /health`.
- **Prometheus** (20:28): target `http://api:8000/metrics`, job `tsi_api`, estado **UP**.
- **Dashboard Grafana** (20:29):
  - Disponibilidad del scraping: **1**.
  - Predicciones realizadas: **41** (coincide con las 40 del tráfico generado más la 1 manual de 20:26).
  - Latencia p95: alrededor de **9 a 10 ms**.
  - Alertas activas: **0**.

---

## 4. Incidente (v1.1)

### Evidencia de nueva imagen y versión

- `/health` después del despliegue: `status: "ok"`, `version: "1.1.0"`, `incident_mode: "degraded"`.
- **Hecho importante:** `/health` sigue diciendo `ok` aunque el servicio está degradado. Esto se explica en la sección 7.

### Tasa 5xx, p95 y alerta observados

| Indicador | Lo que muestra la captura (20:38) |
|---|---|
| Solicitudes / segundo | Un pico de cerca de **1 req/s** entre 20:33 y 20:35 (tráfico del incidente) y otro pico de cerca de 0.7 req/s alrededor de 20:37 |
| Latencia p95 | Punto cercano a **1 s (≈ 970 ms)** alrededor de 20:34, frente a ~10 ms en v1.0 |
| Alertas activas | Subió a **1** de forma visible entre ~20:33 y ~20:35, y hubo otro subida más corta cerca de 20:37 |
| Proporción de errores 5xx | Muestra **"No data"** con un ícono rojo de error en el panel |

- **Alertas definidas** (`monitoring/prometheus/alerts.yml`): `TSI_API_Latencia_Alta` (p95 > 400 ms en ventana de 1 min) y `TSI_API_Alta_Tasa_Errores` (más del 15 % de 5xx en `/predict`, ventana de 1 min). Ambas con `for: 0s`, severidad `warning`, y sin notificaciones externas.
- **Estado de la alerta:** la captura del panel "Alertas activas" confirma que *alguna* alerta estuvo en estado firing. El panel suma las dos reglas, por lo que **no se puede saber solo con esa captura cuál de las dos se activó**. Por el p95 de ~1 s (mayor que 0.4 s), la de latencia es casi seguro.
- **Observación sobre el p95 de ~970 ms:** el defecto agrega 650 ms, pero el panel muestra casi 1 s. **Hipótesis:** el histograma solo tiene buckets en 0.5 s y 1 s (`buckets=(.01,.05,.1,.25,.5,1,2,5)`). `histogram_quantile` interpola dentro de ese bucket, así que el valor calculado se acerca al límite superior y sobreestima el tiempo real. La latencia real debería estar cerca de 650 ms más el tiempo normal.
- **Observación sobre el panel de 5xx:** el panel mostró "No data" con ícono de error. Es un problema del dashboard, no prueba de que no hubo errores 5xx. La causa **no se determinó** en el laboratorio. Queda como punto a revisar (ver sección 6, prevención).

### Hipótesis de causa raíz

- **Lo que se vio (hechos):** al desplegar la imagen 1.1 sube la latencia, aparecen alertas activas y `/health` sigue en `ok`.
- **Hipótesis a partir de los síntomas:** el release 1.1 introduce un defecto en el camino de inferencia que agrega espera y provoca respuestas 503 intermitentes. Al volver a la 1.0 todo se normaliza, lo que apunta al release y no a la infraestructura (Prometheus, Grafana y la red no cambiaron).
- **Confirmación en el código (hecho):** en `app/main.py`, cuando `INCIDENT_MODE == 'degraded'`, `/predict` hace `await asyncio.sleep(0.65)` y devuelve **503 en una de cada tres llamadas** (`order % 3 == 0`). La imagen 1.1 se construyó con `INCIDENT_MODE=degraded`. El defecto es **intencional y simulado**, solo para el laboratorio.

---

## 5. Recuperación

- **Comando de rollback** (del README): `docker compose -f compose.yaml up -d --no-deps --force-recreate api`. Con esto Compose vuelve a usar la imagen `tsi-ec3-api:1.0` definida en `compose.yaml`, sin tocar Prometheus ni Grafana (`--no-deps`).
- **`/health` después del rollback:** `status: "ok"`, `version: "1.0.0"`, `incident_mode: "off"`.
- **Solicitudes después del rollback:** a las 20:39 un `POST /predict` devolvió **200 OK** con `version: "1.0.0"` y `request_id: 86b45a16e742dddf049ef30b34772343`. El dashboard muestra una segunda ráfaga de tráfico alrededor de 20:37, con p95 muy bajo (unos 20 ms).
- **Estado final de alertas** (20:40): `TSI_API_Alta_Tasa_Errores` y `TSI_API_Latencia_Alta` aparecen **INACTIVE (2)** en Prometheus.
- **¿Por qué una alerta puede seguir activa unos segundos después de recuperarse?** Las dos reglas usan `rate(...[1m])`, es decir, una ventana móvil de un minuto. Durante ese minuto todavía entran datos viejos del período con fallas. Además, Prometheus evalúa las reglas cada 5 s y hace scrape cada 5 s, así que hay un pequeño retraso extra. Por eso el valor tarda en bajar del umbral aunque el servicio ya esté sano. En el dashboard, el segundo aumento corto de "Alertas activas" cerca de 20:37 es consistente con esto, aunque con estas capturas es una **hipótesis**, no una confirmación.

**Respuesta de la Evidencia 4 (rollback de snapshot vs. restauración de imagen en Proxmox):** el rollback de snapshot revierte la VM de inmediato a un estado anterior usando cambios locales, y sirve para pruebas rápidas. La restauración de imagen (backup) reconstruye la VM desde una copia externa, y sirve para recuperarse de fallos graves de almacenamiento. En este laboratorio el rollback fue distinto: se volvió a desplegar una **imagen de contenedor anterior**, no se restauró una VM.

---

## 6. Mini-postmortem

**Resumen:** durante el despliegue simulado de la versión 1.1.0 de la API de inferencia, el servicio se volvió lento y devolvió errores 503 intermitentes. Se detectó con el dashboard y las alertas de Prometheus. Se resolvió con rollback a la imagen 1.0.

### Línea de tiempo (hora de las capturas, 09/11/2026)

| Hora | Evento | Tipo |
|---|---|---|
| 20:10 | Se construyen las imágenes `tsi-ec3-api:1.0` y `1.1` | Hecho |
| 20:20 - 20:29 | v1.0 estable: `/health` ok, `/predict` 200, target UP, p95 ~10 ms, alertas 0 | Hecho |
| ~20:33 - 20:35 | Se despliega v1.1 y se genera tráfico. p95 sube a ~1 s y se activa una alerta | Hecho (horas leídas del gráfico) |
| ~20:35 - 20:37 | Rollback a v1.0 y nueva ráfaga de tráfico | Hecho (horas aproximadas) |
| 20:39 | `/predict` responde 200 con versión 1.0.0 | Hecho |
| 20:40 | Las dos alertas figuran INACTIVE | Hecho |

### Impacto

- **Hecho:** durante el incidente la latencia de `/predict` subió a ~1 s en el dashboard (contra ~10 ms normal) y `/health` siguió en `ok`.
- **Por código:** se espera que 1 de cada 3 llamadas a `/predict` dé 503 (unas 20 de 60).
- **Alcance:** laboratorio local con tráfico sintético. No hubo usuarios ni datos reales afectados.

### Detección

- **Hecho:** se detectó mirando el dashboard de Grafana y la página de alertas de Prometheus. Las alertas existen y se activaron, pero **no envían notificaciones** (el propio `alerts.yml` lo aclara), así que dependen de que alguien las mire.
- **Hecho:** `/health` no sirvió para detectar el problema, porque seguía devolviendo `ok`.

### Causa probable

- **Hecho (código):** el defecto está en la imagen 1.1: `INCIDENT_MODE=degraded` agrega 650 ms de espera y 503 cada tres llamadas.
- **Hipótesis:** en un caso real, un cambio de configuración o de código que pasa los tests pero se degrada bajo tráfico produciría síntomas parecidos. Los 6 tests del repositorio no lo detectarían, porque corren con `INCIDENT_MODE` apagado y no miden latencia.

### Mitigación

- **Hecho:** rollback a la imagen 1.0 con `docker compose -f compose.yaml up -d --no-deps --force-recreate api`. Se verificó `/health` en 1.0.0 y las alertas quedaron inactivas.
- **Por qué funcionó:** la imagen anterior seguía disponible en local, y `--no-deps` evitó reiniciar el monitoreo.

### Prevención (propuestas, no verificadas)

1. Hacer un smoke test de `/predict` (latencia y estado) antes de dar por bueno un release.
2. Desplegar de forma gradual (canary) en lugar de reemplazar todo de golpe.
3. Un healthcheck que pruebe una inferencia real, no solo que el proceso responde.
4. Conectar las alertas a un canal de notificación y definir qué hace quien las recibe.
5. Corregir el panel de errores 5xx del dashboard, que mostró "No data" con ícono de error.
6. Agregar buckets entre 0.5 s y 1 s al histograma para que el p95 sea más preciso.
7. Mantener siempre la imagen anterior etiquetada para poder volver rápido.

### Qué salió bien / qué salió mal

- **Bien:** el stack levantó, Prometheus tomó las métricas, el rollback fue rápido y limpio.
- **Mal:** el panel de 5xx no mostró datos, no hay alertas con notificación y `/health` no refleja degradación.

---

## 7. Riesgos y limitaciones

**¿Qué no demuestra el endpoint `/health`?**
Solo demuestra que el proceso responde y devuelve una versión. En la v1.1 devolvió `status: "ok"` mientras `/predict` estaba lento y fallaba. No prueba que el modelo cargue bien, que la inferencia funcione, que la latencia sea aceptable ni que los errores sean bajos. El `healthcheck` de `compose.yaml` usa este mismo endpoint, así que Docker también habría visto el contenedor como sano.

**¿Por qué el modelo con datos sintéticos no es apto para uso real?**
El clasificador es un Naive Bayes muy pequeño entrenado con un archivo de ejemplos ficticios (`tickets_sinteticos.csv`, unos 700 bytes). No representa tickets reales, no fue validado y sus puntajes **no están calibrados** (`score_no_calibrado`). Un 0.96 no significa 96 % de probabilidad real. El propio código dice que no es apto para decisiones operativas.

**¿Qué datos se excluyen deliberadamente de los logs?**
Según el código y el test `test_log_no_pii`, no se registran el cuerpo de la solicitud, el texto del ticket, tokens ni contraseñas. Solo se guardan evento, `request_id`, método, ruta normalizada, estado, duración y versión. Las rutas desconocidas se agrupan como `/other` para evitar etiquetas con demasiados valores distintos (cardinalidad) en Prometheus.

**Otras limitaciones de esta práctica:**
- Se ejecutó en Codespaces, no en el entorno descrito en el README. Los tiempos del navegador (por ejemplo 628 ms y 512 ms en los `POST /predict` de httpie) incluyen la red de Codespaces y **no sirven** para medir la latencia del servidor. Para eso se usan las métricas de Prometheus.
- Algunas horas se leyeron de gráficos, por lo que son aproximadas.
- Grafana corre con acceso anónimo y las interfaces solo en `127.0.0.1`: es solo para demostración, no para producción.
- El paquete original aclara que no se validó de extremo a extremo con Docker real antes de entregarse; esta práctica es esa validación.

---

## 8. Referencias y uso de IA

**Fuentes oficiales (citadas en el README del laboratorio):**
- Proxmox VE: https://proxmox.com/en/products/proxmox-virtual-environment/overview
- Docker Compose: https://docs.docker.com/compose/
- Prometheus, reglas de alerta: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Grafana, provisioning: https://grafana.com/docs/grafana/latest/administration/provisioning/

**Material del laboratorio usado:** `README.md`, `app/main.py`, `app/ml.py`, `monitoring/prometheus/alerts.yml`, `monitoring/grafana/dashboards/tsi-dashboard.json`, `compose.yaml`, `compose.incident.yaml`, `Dockerfile` y `evidencias/informe_gonzales_ordonez.pdf`.

**Uso de IA:** se usó Claude (Anthropic) como apoyo para ordenar el informe según `docs/PLANTILLA_INFORME_INDIVIDUAL.md`, leer el código del repositorio y revisar las capturas.

**Decisiones verificadas:** los datos de versiones, imágenes, métricas y estados de alerta salen de las capturas; el comportamiento del defecto sale de `app/main.py`; las explicaciones sobre p95 y la ventana de 1 minuto son hipótesis razonadas y están marcadas como tales.

**Responsabilidad individual:** cada integrante revisó el contenido y responde por él.
