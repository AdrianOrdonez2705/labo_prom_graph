# Checklist de prueba — EC3 Observabilidad y recuperación

**Condición**: Docker Desktop ya instalado y ejecutándose en modo Linux. No instalar software nuevo en Windows.

## A. Preparación individual
- [ ] `docker version` muestra cliente y servidor.
- [ ] `docker compose version` se ejecuta.
- [ ] Puertos locales 8000, 9090, 3000 libres.
- [ ] Dos imágenes `tsi-ec3-api:1.0` y `tsi-ec3-api:1.1` construidas con los comandos del README.

## B. Estado inicial v1.0
- [ ] `docker compose up -d` ejecutado.
- [ ] `docker compose ps` muestra api, prometheus y grafana.
- [ ] `http://localhost:8000/health` devuelve versión `1.0.0`.
- [ ] `http://localhost:9090/targets` muestra `tsi_api` en UP.
- [ ] Dashboard `TSI EC3 | Observabilidad de inferencia` disponible.
- [ ] `docker compose run --rm --no-deps traffic --count 40 --delay 0.1` devuelve principalmente/solo HTTP 200.

## C. Incidente v1.1
- [ ] Desplegado `compose.incident.yaml` con `--no-deps --force-recreate api`.
- [ ] `/health` muestra versión `1.1.0` y todavía puede mostrar status `ok`.
- [ ] Generadas 60 peticiones de inferencia.
- [ ] Se ven HTTP 503 en logs de api.
- [ ] Se incrementan latencia p95 y proporción 5xx.
- [ ] Se revisa el estado de alertas en Prometheus (sin afirmar que se enviaron notificaciones).

## D. Recuperación
- [ ] Desplegada imagen v1.0 nuevamente, con comando de rollback en README.
- [ ] `/health` vuelve a `1.0.0`.
- [ ] 40 solicitudes posteriores retornan correctamente.
- [ ] Se explica por qué los indicadores de ventana de 1m pueden tardar en normalizarse.

## E. Cierre
- [ ] Evidencias guardadas en `evidencias/` (imágenes y/o salida de comandos, sin secretos).
- [ ] Informe individual basado en `docs/PLANTILLA_INFORME_INDIVIDUAL.md`.
- [ ] `docker compose down` al finalizar.

### Limitación de la verificación previa
Se validaron unit tests y respuestas HTTP de ambas versiones usando un servidor local Python, además de sintaxis YAML/JSON. No hay Docker Engine disponible en el entorno de creación de este paquete: la ejecución multiproceso Docker+Prometheus+Grafana se verifica durante la prueba docente en el aula.
