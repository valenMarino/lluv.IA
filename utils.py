import plotly.express as px
import pandas as pd

def graficar_historico(df: pd.DataFrame, provincia: str):
    return px.line(df, x="ds", y="y",
                   title=f"📊 Precipitación histórica - {provincia}",
                   labels={"ds": "Fecha", "y": "mm/mes"})

def graficar_prediccion(forecast: pd.DataFrame, provincia: str):
    return px.line(forecast, x="ds", y="yhat",
                   title=f"🔮 Predicción de precipitación - {provincia}",
                   labels={"ds": "Fecha", "yhat": "mm/mes"})
