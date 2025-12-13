import pandas as pd
import plotly.express as px
from jmeter_analysis import JMeterAnalysis
import os

# Archivos de entrada
SAR_CSV = 'sar_metrics.csv'
JTL_FILE = 'results/jmeter_raw_results.jtl'
REPORT_HTML = 'combined_report.html'

def create_combined_report():
    """Genera un informe HTML combinando datos de sar y JMeter."""

    # 1. Análisis de sar (Métricas de Recursos)
    try:
        # sar genera un archivo CSV con un encabezado complejo,
        # necesitamos identificar las columnas correctas.
        # Asumimos el CSV generado por sadf -d (separado por ';')
        df_sar = pd.read_csv(SAR_CSV, sep=';', skipinitialspace=True, header=None, skiprows=2)

        # Renombrar columnas clave. Las columnas 2 y 3 contienen Hora y Métrica (e.g., CPU, Memory)
        # Aquí solo se usa una muestra para el reporte, puedes expandir esto
        df_sar = df_sar.rename(columns={2: 'Timestamp', 3: 'Recurso', 6: 'CPU_%'})
        df_sar['Timestamp'] = pd.to_datetime(df_sar['Timestamp'])

        # Ejemplo de gráfico de sar: Uso de CPU
        cpu_data = df_sar[df_sar['Recurso'].str.contains('CPU', na=False)]
        fig_cpu = px.line(cpu_data, x='Timestamp', y='CPU_%', title='Uso de CPU del Servidor (sar)',
                          labels={'CPU_%': 'Uso de CPU (%)'})
        sar_html = fig_cpu.to_html(full_html=False, include_plotlyjs='cdn')

    except Exception as e:
        sar_html = f"<h2>Error al procesar sar:</h2><p>{e}</p>"
        print(f"Error procesando sar: {e}")


    # 2. Análisis de JMeter (Métricas de Rendimiento)
    try:
        # Usa la librería jmeter-analysis para obtener métricas clave
        analysis = JMeterAnalysis(JTL_FILE)

        # Métrica clave: Tiempos de respuesta (Latency)
        df_jmeter = analysis.data
        fig_latency = px.line(df_jmeter, x='timeStamp', y='Latency',
                              title='Tiempos de Respuesta (JMeter)',
                              labels={'Latency': 'Latencia (ms)', 'timeStamp': 'Tiempo'})

        jmeter_html = fig_latency.to_html(full_html=False, include_plotlyjs='cdn')

        # Generar un resumen de métricas
        summary = analysis.get_summary()
        summary_html = summary.to_html(classes='table table-striped', header=True, index=True)

    except Exception as e:
        jmeter_html = f"<h2>Error al procesar JMeter:</h2><p>{e}</p>"
        summary_html = "<p>Resumen de JMeter no disponible.</p>"
        print(f"Error procesando JMeter: {e}")


    # 3. Generación del Informe HTML Combinado
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
    # Asegúrate de que el directorio de resultados exista
    os.makedirs('results', exist_ok=True)
    create_combined_report()