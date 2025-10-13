import plotly.express as px
import pandas as pd
import datetime
import plotly.graph_objects as go

DEFAULT_TEMPLATE = "plotly_dark"

def graficar_historico(df: pd.DataFrame, provincia: str):
    fig = px.line(df, x="ds", y="y",
                  title=f"📊 Precipitación histórica - {provincia}",
                  labels={"ds": "Fecha", "y": "mm/mes"},
                  template=DEFAULT_TEMPLATE)
    fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117")
    fig.update_traces(line=dict(color="#7fb3ff"))
    return fig

def graficar_prediccion(forecast: pd.DataFrame, provincia: str):
    # Mostrar solo desde el primer día del mes siguiente
    today = datetime.date.today()
    if today.month == 12:
        next_month_start = datetime.date(today.year + 1, 1, 1)
    else:
        next_month_start = datetime.date(today.year, today.month + 1, 1)

    df = forecast.copy()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title=f"🔮 Predicción de precipitación - {provincia}", template=DEFAULT_TEMPLATE,
                          plot_bgcolor="#0e1117", paper_bgcolor="#0e1117")
        return fig

    if not pd.api.types.is_datetime64_any_dtype(df["ds"]):
        df["ds"] = pd.to_datetime(df["ds"]) 

    filtered = df[df["ds"].dt.date >= next_month_start]

    if filtered.empty:
        fig = go.Figure()
        fig.update_layout(title=f"🔮 Predicción de precipitación - {provincia} (no hay datos a partir del próximo mes)",
                          template=DEFAULT_TEMPLATE, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117")
        return fig

    fig = px.line(filtered, x="ds", y="yhat",
                  title=f"🔮 Predicción de precipitación - {provincia}",
                  labels={"ds": "Fecha", "yhat": "mm/mes"},
                  template=DEFAULT_TEMPLATE)
    fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117")
    fig.update_traces(line=dict(color="#ffd07f"))
    return fig
