import pandas as pd
import plotly.express as px
import os
import matplotlib.pyplot as plt # Añadimos matplotlib para gráficos simples

# Archivos de entrada
SAR_CSV = 'sar_metrics.csv'
# JMETER_RAW_RESULTS.jtl debe ser un archivo CSV.
# Si tu JMeter lo generó en XML, necesitas cambiar la línea de JMeter en el YAML a modo CSV.
JTL_FILE = 'results/jmeter_raw_results.jtl'
REPORT_HTML = 'combined_report.html'

def create_combined_report():
    """Genera un informe HTML combinando datos de sar y JMeter."""

    # --- 1. Análisis de sar (Métricas de Recursos) ---
    sar_html = ""
    try:
        # Asumimos que sadf -d (separado por ';') y omitimos las primeras líneas informativas
        df_sar = pd.read_csv(SAR_CSV, sep=';', skipinitialspace=True, header=None, skiprows=2)

        # Las columnas de sadf -d son fijas, pero pueden variar ligeramente.
        # Usamos nombres genéricos para el ejemplo:
        df_sar = df_sar.rename(columns={
            0: 'hostname',
            1: 'interval_id',
            2: 'Timestamp',
            3: 'Recurso',
            4: 'Total', # O una métrica base
            6: 'CPU_%' # El uso de CPU generalmente está en esta región
        })
        df_sar['Timestamp'] = pd.to_datetime(df_sar['Timestamp'])

        # Ejemplo de gráfico de sar: Uso de CPU (%user + %system)
        # Seleccionamos las filas que contienen la métrica de CPU y calculamos el uso total
        # (Este es un ejemplo, la lógica de sar puede ser más compleja)
        cpu_data = df_sar[df_sar['Recurso'] == 'CPU'].copy()

        # Nota: En sar, el %idle es el complemento. Usaremos %user (col 5) + %system (col 6)
        # Ajusta los índices de columna (5 y 6) según tu salida exacta de sadf.
        try:
             # Si el archivo tiene encabezados, mejor usar nombres:
             # df_sar.columns = ['hostname', 'interval', 'timestamp', 'metric', '%user', '%nice', '%system', '%iowait', '%steal', '%idle']
             cpu_data['CPU_Usage'] = df_sar[5].astype(float) + df_sar[6].astype(float)
        except Exception:
             cpu_data['CPU_Usage'] = cpu_data['CPU_%'] # Si no se puede calcular, usar la columna de ejemplo

        fig_cpu = px.line(cpu_data, x='Timestamp', y='CPU_Usage', title='Uso de CPU del Servidor (sar)',
                          labels={'CPU_Usage': 'Uso de CPU (%)'})
        sar_html = fig_cpu.to_html(full_html=False, include_plotlyjs='cdn')

    except Exception as e:
        sar_html = f"<h2>Error al procesar sar:</h2><p>Asegúrate de que 'sar_metrics.csv' exista y esté en formato delimitado por punto y coma (;). Error: {e}</p>"
        print(f"Error procesando sar: {e}")


    # --- 2. Análisis de JMeter (Métricas de Rendimiento) ---
    jmeter_html = ""
    summary_html = ""
    try:
        # Leer el archivo JTL (CSV)
        # El archivo JTL de JMeter por defecto tiene encabezados: timeStamp, elapsed, label, responseCode, success, etc.
        df_jmeter = pd.read_csv(JTL_FILE)

        # Convertir 'timeStamp' a datetime para análisis de series de tiempo
        df_jmeter['Timestamp'] = pd.to_datetime(df_jmeter['timeStamp'], unit='ms')

        # Gráfico de Latencia a lo largo del tiempo
        fig_latency = px.line(df_jmeter, x='Timestamp', y='elapsed',
                              title='Tiempos de Respuesta (JMeter)',
                              labels={'elapsed': 'Latencia (ms)'})
        jmeter_html = fig_latency.to_html(full_html=False, include_plotlyjs='cdn')

        # Generar un resumen de métricas (Percentiles, Promedio, Errores)
        summary = df_jmeter.agg(
            {
                'elapsed': ['mean', 'median', lambda x: x.quantile(0.90), lambda x: x.quantile(0.95)],
                'success': [lambda x: (x == False).sum()]
            }
        ).rename(columns={'<lambda_0>': '90th Percentile (ms)', '<lambda_1>': '95th Percentile (ms)', '<lambda_2>': 'Error Count'})

        summary_html = summary.to_html(classes='table table-striped', header=True, index=True)

    except Exception as e:
        jmeter_html = f"<h2>Error al procesar JMeter:</h2><p>Asegúrate de que 'jmeter_raw_results.jtl' exista y esté en formato CSV. Error: {e}</p>"
        summary_html = "<p>Resumen de JMeter no disponible.</p>"
        print(f"Error procesando JMeter: {e}")


    # --- 3. Generación del Informe HTML Combinado ---
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Informe de Pruebas de Rendimiento</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container">
            <h1 class="mt-4">🚀 Informe de Pruebas de Rendimiento Combinado</h1>
            <p>Generado por el Robot de GitHub Actions.</p>

            <hr>

            <h2>📈 Resumen de JMeter</h2>
            {summary_html}

            <hr>

            <h2>⏱️ Gráfico de Tiempos de Respuesta (JMeter)</h2>
            {jmeter_html}

            <hr>

            <h2>💻 Gráfico de Uso de Recursos (sar)</h2>
            <p>Monitoreo del Servidor durante la prueba.</p>
            {sar_html}

        </div>
    </body>
    </html>
    """

    with open(REPORT_HTML, 'w') as f:
        f.write(html_content)

    print(f"Informe HTML combinado generado: {REPORT_HTML}")

if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    create_combined_report()