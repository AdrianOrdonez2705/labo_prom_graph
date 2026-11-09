# LAB EC3 - Informe individual

**Estudiante:** [nombre y código]  **Fecha:** [fecha]

## 1. Arquitectura y relación con Proxmox
Explique en 120–160 palabras las capas hardware / Proxmox / VM Linux / Docker / API / observabilidad.

## 2. Pre-flight
- Docker version / Compose version: 
- Captura de `docker compose ps`:
- Imagenes locales `docker images tsi-ec3-api`:

## 3. Estado estable (v1.0)
- `/health` (estado + versión):
- `/predict` (categoría y solicitud):
- Captura del dashboard y métrica de latencia:

## 4. Incidente (v1.1)
- Evidencia de nueva imagen y versión:
- Errores HTTP y logs con `request_id`:
- Tasa 5xx, p95 y alerta observada (estado y hora):
- Hipótesis de causa raíz:

## 5. Recuperación
- Comando de rollback:
- `/health` versión restituida:
- Solicitudes después del rollback:
- ¿Por qué una alerta puede seguir activa unos segundos tras recuperarse?:

## 6. Mini-postmortem
Impacto, detección, causa probable, mitigación, prevención; separar hechos de hipótesis.

## 7. Riesgos y limitaciones
- ¿Qué no demuestra el endpoint `/health`?
- ¿Por qué el modelo con datos sintéticos no es apto para uso real?
- ¿Qué datos se excluyen deliberadamente de logs?

## 8. Referencias y uso de IA
Fuentes, prompts, decisiones verificadas y responsabilidad individual.
