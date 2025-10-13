import gradio as gr
from nasa_api import obtener_datos_precipitacion
from forecast_model import predecir_precipitacion
from utils import graficar_historico, graficar_prediccion

def analizar_provincia(provincia):
    try:
        df = obtener_datos_precipitacion(provincia)
        forecast = predecir_precipitacion(df)

        resumen = (
            f"📍 Provincia: {provincia}\n"
            f"📈 Promedio histórico: {df['y'].mean():.2f} mm/mes\n"
            f"🌦️ Predicción próximo año: {forecast.tail(12)['yhat'].mean():.2f} mm/mes"
        )

        return resumen, graficar_historico(df, provincia), graficar_prediccion(forecast, provincia)
    except Exception as e:
        mensaje = f"Error al obtener o procesar datos: {e}"
        return mensaje, None, None

def crear_ui():
    custom_css = """
    body { background: #0b0f14; color: #e6eef8 }
    .gradio-container { background: #0b0f14 }
    .gradio-interface { background: #0b0f14 }
    .card { background: #0f151b !important; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.6); }
    .output-textbox textarea { background: #071018; color: #e6eef8; border: 1px solid #1f2a35 }
    .output-plot { background: #071018 }
    """

    return gr.Interface(
        fn=analizar_provincia,
        inputs=gr.Dropdown(
            ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Salta", "Misiones"],
            label="Seleccionar provincia"
        ),
        outputs=[
            gr.Textbox(label="Resumen del análisis", lines=6),
            gr.Plot(label="Histórico"),
            gr.Plot(label="Predicción"),
        ],
        title="🌾 Lluvi.IA - Predicción Inteligente de Precipitaciones",
        description="Seleccioná una provincia argentina para analizar la evolución y predicción de precipitaciones con datos de NASA POWER.",
        css=custom_css
    )
