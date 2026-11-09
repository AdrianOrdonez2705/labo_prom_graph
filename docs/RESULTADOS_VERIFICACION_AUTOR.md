# Pruebas realizadas al crear el paquete

| Comprobación | Resultado |
|---|---|
| `pytest` (6 pruebas FastAPI + modelo) | PASÓ (6/6) |
| Análisis YAML y JSON de configuraciones | PASÓ |
| API local 1.0.0 (`/health`, `/predict`, `/metrics`) | PASÓ, 3 inferencias 200 |
| API local 1.1.0 (`/health`, `/predict`, `/metrics`) | PASÓ, secuencia 200, 200, 503 |
| Renderización y control de desbordamiento de PowerPoint | PASÓ |
| Renderización visual de guías Word | PASÓ |
| Construcción de imágenes Docker en este contenedor | NO EJECUTADA: no hay Docker Engine ni Docker CLI en el entorno |
| Stack Prometheus/Grafana funcionando en Docker | PENDIENTE de validación en equipo docente |

**Interpretación:** los resultados anteriores no equivalen a una validación de extremo a extremo en Docker. La preparación docente debe ejecutar el checklist en un equipo real antes de distribuir el laboratorio.
