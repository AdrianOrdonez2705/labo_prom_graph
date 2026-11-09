# PREPARACION DOCENTE | EC3 Proxmox conceptual + Docker operativo

**No instalar aplicaciones en Windows.** Pre-requisitos: Docker Desktop con Engine Linux y Compose v2, navegador; PowerShell o terminal integrada. Memoria recomendada: 8 GB libres y 6 GB para Docker (ajustar al equipo). Internet solo para descargar imagenes una vez.

1. Descomprimir el proyecto en una ruta sin espacios especiales (ej. C:/TSI/EC3-Obs).
2. En PowerShell, ejecutar `docker version` y `docker compose version`.
3. Ejecutar las dos compilaciones indicadas en `README.md`; descargar anticipadamente `prom/prometheus:v3.5.0` y `grafana/grafana:12.1.0` con `docker pull` individual.
4. Levantar entorno estable (`docker compose up -d`). Revisar http://localhost:8000/health, http://localhost:9090/targets, http://localhost:3000/d/tsi-ec3/tsi-ec3-observabilidad-de-inferencia (o buscar en Dashboards > Laboratorio TSI).
5. Generar trafico y comprobar métricas (`docker compose run --rm --no-deps traffic --count 40 --delay 0.1`).
6. Inyectar v1.1 con el override, generar 60 llamadas, comprobar aumento de errores y alertas en http://localhost:9090/alerts.
7. Recuperar v1.0 y generar tráfico normal. Las series son de ventana de 1 minuto: esperar >60 s puede ser necesario para que alertas se resuelvan.
8. Verificar que v1.1 fue construida localmente y que los puertos no están ocupados.
9. Preparar evidencia docente para conectividad degradada, NO sustituir trabajo individual sin declararlo.

No declarar prueba integral Docker exitosa si no se ejecutó contra un Docker Engine real. El clasificador usa ejemplos ficticios, sin datos reales.
