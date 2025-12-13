#!/bin/bash
# 1. Detiene el proceso de sar
SAR_PID=$(cat sar_pid.txt)
echo "Deteniendo sar (PID: $SAR_PID)..."
# Usamos SIGTERM (15) para permitir que el proceso termine limpiamente
kill -15 $SAR_PID

# Esperar un momento (vital) para que sar escriba los datos binarios finales
sleep 5

# 2. Convierte el archivo binario de sar a CSV
# sadf necesita el path del archivo binario (-F sar.bin) y la salida (-d)
sadf -d sar.bin -- -A > sar_metrics.csv
echo "Métricas de sar guardadas en sar_metrics.csv"