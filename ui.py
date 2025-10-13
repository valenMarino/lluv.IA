import gradio as gr
from nasa_api import obtener_datos_precipitacion
from forecast_model import predecir_precipitacion
from utils import graficar_historico, graficar_prediccion

def analizar_provincia(provincia):
    df = obtener_datos_precipitacion(provincia)
    forecast = predecir_precipitacion(df)

    resumen = (
        f"📍 Provincia: {provincia}\n"
        f"📈 Promedio histórico: {df['y'].mean():.2f} mm/mes\n"
        f"🌦️ Predicción próximo año: {forecast.tail(12)['yhat'].mean():.2f} mm/mes"
    )

    return resumen, graficar_historico(df, provincia), graficar_prediccion(forecast, provincia)

def crear_ui():
    return gr.Interface(
        fn=analizar_provincia,
        inputs=gr.Dropdown(
            ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Salta", "Misiones"],
            label="Seleccionar provincia"
        ),
        outputs=[
            gr.Textbox(label="Resumen del análisis"),
            gr.Plot(label="Histórico"),
            gr.Plot(label="Predicción"),
        ],
        title="🌾 AgroRain - Predicción Inteligente de Precipitaciones",
        description="Seleccioná una provincia argentina para analizar la evolución y predicción de precipitaciones con datos de NASA POWER."
    )
