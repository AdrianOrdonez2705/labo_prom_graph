# LAB EC3 - Informe individual

**Estudiante:** Adrian Gonzales Ferreira, Adrián Fabricio Ordóñez Paredes  **Fecha:** 09/11/2026

## 1. Arquitectura y relación con Proxmox
Hardware: Constituye la base física (servidor con CPU, memoria RAM, discos y tarjetas de red).

Proxmox: Hipervisor de tipo 1 instalado directamente en el hardware para gestionar y virtualizar recursos.

VM Linux: Máquina virtual con un sistema operativo Linux independiente que garantiza aislamiento y seguridad.

Docker: Motor de contenedores dentro de la VM Linux que empaqueta dependencias de forma ligera y eficiente.

API: Aplicación o servicio backend alojado dentro del contenedor Docker que expone funcionalidades mediante HTTP o gRPC.

Observabilidad: Capa transversal que rastrea métricas, registros y trazas de las capas anteriores para auditar salud, rendimiento y comportamiento en tiempo real.

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

> **NOTE**: Las imágenes se encuentran en el documento PDF evidencias/informe_gonzales_ordonez.pdf
