#!/bin/bash

# Ejecutar el script app.py por primera vez
echo "Ejecutando app.py por primera vez..."
python3 /app/app.py

# Configurar y activar el crontab
echo "Iniciando cron para ejecución periódica..."
cron -f
