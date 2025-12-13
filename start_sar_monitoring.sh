#!/bin/bash
# Crea un archivo binario para sar y lo ejecuta en segundo plano
# -o: Guarda la salida en formato binario (sa.bin)
# 5 0: Recolección cada 5 segundos (0 significa hasta que se detenga)
sar -o sar.bin -A 5 0 > /dev/null 2>&1 &
echo $! > sar_pid.txt
echo "sar iniciado en background con PID $(cat sar_pid.txt)"