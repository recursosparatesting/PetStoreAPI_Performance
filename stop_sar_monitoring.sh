#!/bin/bash
# Detiene el proceso de sar
SAR_PID=$(cat sar_pid.txt)
echo "Deteniendo sar (PID: $SAR_PID)..."
kill $SAR_PID

# Convierte el archivo binario de sar a CSV
# -d: Formato delimitado (CSV)
# -A: Todas las métricas
sadf -d sar.bin -- -A > sar_metrics.csv
echo "Métricas de sar guardadas en sar_metrics.csv"