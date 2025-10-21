import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import datetime
import numpy as np
from typing import Dict, Any

DEFAULT_TEMPLATE = "plotly_dark"
PLOT_BGCOLOR = "rgba(17, 24, 39, 0.8)"
FONT_COLOR = '#e5e7eb'

COLOR_PALETTE = {
    'primary': '#3b82f6',
    'secondary': '#10b981', 
    'accent': '#f59e0b',
    'danger': '#ef4444',
    'precipitation': '#60a5fa',
    'temperature': '#fb7185',
    'humidity': '#34d399'
}

def graficar_historico(df: pd.DataFrame, provincia: str):
    """Genera gráfico mejorado de precipitación histórica."""
    fig = go.Figure()
    
    # Línea principal de precipitación
    fig.add_trace(go.Scatter(
        x=df['ds'],
        y=df['y'],
        mode='lines',
        name='Precipitación mensual',
        line={'color': COLOR_PALETTE['precipitation'], 'width': 2},
        hovertemplate='<b>%{x}</b><br>Precipitación: %{y:.1f} mm<extra></extra>'
    ))
    
    # Promedio histórico como línea horizontal
    promedio = df['y'].mean()
    fig.add_hline(
        y=promedio,
        line_dash="dash",
        line_color=COLOR_PALETTE['secondary'],
        annotation_text=f"Promedio: {promedio:.1f} mm",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title={
            'text': f"🌧️ Evolución Histórica de Precipitaciones - {provincia}",
            'x': 0.5,
            'font': {'size': 18, 'color': '#e5e7eb'}
        },
        xaxis_title="Año",
        yaxis_title="Precipitación (mm/mes)",
        template=DEFAULT_TEMPLATE,
        plot_bgcolor="rgba(17, 24, 39, 0.8)",
        paper_bgcolor="rgba(17, 24, 39, 0.8)",
        font=dict(color='#e5e7eb'),
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def graficar_prediccion(forecast: pd.DataFrame, provincia: str):
    """Genera gráfico mejorado de predicción con intervalos de confianza."""
    today = datetime.date.today()
    if today.month == 12:
        next_month_start = datetime.date(today.year + 1, 1, 1)
    else:
        next_month_start = datetime.date(today.year, today.month + 1, 1)

    df = forecast.copy()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"🔮 Predicción de precipitación - {provincia}", 
            template=DEFAULT_TEMPLATE,
            plot_bgcolor="rgba(17, 24, 39, 0.8)", 
            paper_bgcolor="rgba(17, 24, 39, 0.8)"
        )
        return fig

    if not pd.api.types.is_datetime64_any_dtype(df["ds"]):
        df["ds"] = pd.to_datetime(df["ds"]) 

    # Filtrar datos futuros
    filtered = df[df["ds"].dt.date >= next_month_start]

    if filtered.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"🔮 Predicción - {provincia} (Sin datos futuros)",
            template=DEFAULT_TEMPLATE, 
            plot_bgcolor="rgba(17, 24, 39, 0.8)", 
            paper_bgcolor="rgba(17, 24, 39, 0.8)"
        )
        return fig

    fig = go.Figure()
    
    # Intervalo de confianza
    if 'yhat_upper' in filtered.columns and 'yhat_lower' in filtered.columns:
        fig.add_trace(go.Scatter(
            x=list(filtered['ds']) + list(filtered['ds'][::-1]),
            y=list(filtered['yhat_upper']) + list(filtered['yhat_lower'][::-1]),
            fill='toself',
            fillcolor='rgba(251, 113, 133, 0.2)',
            line={'color': 'rgba(255,255,255,0)'},
            name='Intervalo de confianza',
            hoverinfo='skip'
        ))
    
    # Línea de predicción
    fig.add_trace(go.Scatter(
        x=filtered['ds'],
        y=filtered['yhat'],
        mode='lines+markers',
        name='Predicción',
        line={'color': COLOR_PALETTE['accent'], 'width': 3},
        marker={'size': 6},
        hovertemplate='<b>%{x}</b><br>Predicción: %{y:.1f} mm<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f"🔮 Predicción de Precipitaciones - {provincia}",
            'x': 0.5,
            'font': {'size': 18, 'color': '#e5e7eb'}
        },
        xaxis_title="Fecha",
        yaxis_title="Precipitación Predicha (mm/mes)",
        template=DEFAULT_TEMPLATE,
        plot_bgcolor="rgba(17, 24, 39, 0.8)",
        paper_bgcolor="rgba(17, 24, 39, 0.8)",
        font=dict(color='#e5e7eb'),
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def graficar_temperatura(df: pd.DataFrame, provincia: str):
    """Genera gráfico de análisis de temperatura."""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Temperatura Promedio Mensual', 'Rango de Temperaturas (Máx/Mín)'),
        vertical_spacing=0.1
    )
    
    if 'temperatura' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['ds'],
                y=df['temperatura'],
                mode='lines',
                name='Temp. Promedio',
                line={'color': COLOR_PALETTE['temperature'], 'width': 2},
                hovertemplate='<b>%{x}</b><br>Temperatura: %{y:.1f}°C<extra></extra>'
            ),
            row=1, col=1
        )
    
    if 'temp_max' in df.columns and 'temp_min' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['ds'],
                y=df['temp_max'],
                mode='lines',
                name='Temp. Máxima',
                line={'color': '#ff6b6b', 'width': 1.5},
                hovertemplate='<b>%{x}</b><br>Temp. Máx: %{y:.1f}°C<extra></extra>'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['ds'],
                y=df['temp_min'],
                mode='lines',
                name='Temp. Mínima',
                line={'color': '#4ecdc4', 'width': 1.5},
                fill='tonexty',
                fillcolor='rgba(78, 205, 196, 0.1)',
                hovertemplate='<b>%{x}</b><br>Temp. Mín: %{y:.1f}°C<extra></extra>'
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        title={
            'text': f"🌡️ Análisis de Temperatura - {provincia}",
            'x': 0.5,
            'font': {'size': 18, 'color': FONT_COLOR}
        },
        template=DEFAULT_TEMPLATE,
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PLOT_BGCOLOR,
        font={'color': FONT_COLOR},
        hovermode='x unified',
        showlegend=True,
        height=600
    )
    
    fig.update_xaxes(title_text="Año", row=2, col=1)
    fig.update_yaxes(title_text="Temperatura (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Temperatura (°C)", row=2, col=1)
    
    return fig

def graficar_comparativo_anual(df: pd.DataFrame, provincia: str):
    """Genera gráfico comparativo entre años recientes."""
    df_copy = df.copy()
    df_copy['año'] = df_copy['ds'].dt.year
    df_copy['mes'] = df_copy['ds'].dt.month
    
    años_recientes = sorted(df_copy['año'].unique())[-6:-1]
    df_filtered = df_copy[df_copy['año'].isin(años_recientes)]
    
    fig = go.Figure()
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    for i, año in enumerate(años_recientes):
        data_año = df_filtered[df_filtered['año'] == año]
        
        fig.add_trace(go.Scatter(
            x=data_año['mes'],
            y=data_año['y'],
            mode='lines+markers',
            name=str(año),
            line={'color': colors[i % len(colors)], 'width': 2},
            marker={'size': 6},
            hovertemplate=f'<b>Año {año}</b><br>Mes: %{{x}}<br>Precipitación: %{{y:.1f}} mm<extra></extra>'
        ))
    
    promedio_mensual = df_copy.groupby('mes')['y'].mean()
    fig.add_trace(go.Scatter(
        x=promedio_mensual.index,
        y=promedio_mensual.values,
        mode='lines',
        name='Promedio Histórico',
        line={'color': 'white', 'width': 3, 'dash': 'dash'},
        hovertemplate='<b>Promedio Histórico</b><br>Mes: %{x}<br>Precipitación: %{y:.1f} mm<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f"📊 Comparativo Anual de Precipitaciones - {provincia}",
            'x': 0.5,
            'font': {'size': 18, 'color': FONT_COLOR}
        },
        xaxis_title="Mes",
        yaxis_title="Precipitación (mm/mes)",
        template=DEFAULT_TEMPLATE,
        plot_bgcolor=PLOT_BGCOLOR,
        paper_bgcolor=PLOT_BGCOLOR,
        font={'color': FONT_COLOR},
        hovermode='x unified',
        showlegend=True,
        xaxis={
            'tickmode': 'array',
            'tickvals': list(range(1, 13)),
            'ticktext': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        }
    )
    
    return fig

def calcular_estadisticas_climaticas(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula estadísticas climáticas detalladas."""
    estadisticas = {}
    
    if 'y' in df.columns:
        estadisticas['precipitacion'] = {
            'promedio_anual': df['y'].mean() * 12,
            'promedio_mensual': df['y'].mean(),
            'maximo': df['y'].max(),
            'minimo': df['y'].min(),
            'desviacion': df['y'].std(),
            'coef_variacion': (df['y'].std() / df['y'].mean()) * 100
        }
    
    if 'temperatura' in df.columns:
        estadisticas['temperatura'] = {
            'promedio': df['temperatura'].mean(),
            'maximo': df['temperatura'].max(),
            'minimo': df['temperatura'].min(),
            'amplitud': df['temperatura'].max() - df['temperatura'].min()
        }
    
    if 'humedad' in df.columns:
        estadisticas['humedad'] = {
            'promedio': df['humedad'].mean(),
            'maximo': df['humedad'].max(),
            'minimo': df['humedad'].min()
        }
    
    df_copy = df.copy()
    df_copy['mes'] = df_copy['ds'].dt.month
    
    def obtener_estacion(mes):
        if mes in [12, 1, 2]: return 'Verano'
        elif mes in [3, 4, 5]: return 'Otoño'
        elif mes in [6, 7, 8]: return 'Invierno'
        else: return 'Primavera'
    
    df_copy['estacion'] = df_copy['mes'].apply(obtener_estacion)
    
    estadisticas['estacional'] = {}
    for estacion in ['Verano', 'Otoño', 'Invierno', 'Primavera']:
        data_estacion = df_copy[df_copy['estacion'] == estacion]
        if not data_estacion.empty:
            estadisticas['estacional'][estacion] = {
                'precipitacion_promedio': data_estacion['y'].mean(),
                'temperatura_promedio': data_estacion['temperatura'].mean() if 'temperatura' in data_estacion.columns else None
            }
    
    return estadisticas

def generar_reporte_climatico(provincia: str, df: pd.DataFrame, forecast: pd.DataFrame, estadisticas: Dict[str, Any], fecha_inicio: str, fecha_fin: str) -> str:
    """Genera un reporte climático detallado en español."""
    reporte = []
    
    reporte.append(f"🌾 REPORTE CLIMÁTICO DETALLADO - {provincia.upper()}")
    reporte.append("=" * 60)
    reporte.append(f"📅 Período analizado: {fecha_inicio} - {fecha_fin} | Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    reporte.append("")
    
    reporte.append("📊 RESUMEN EJECUTIVO")
    reporte.append("-" * 30)
    
    if 'precipitacion' in estadisticas:
        p = estadisticas['precipitacion']
        reporte.append(f"🌧️ Precipitación promedio anual: {p['promedio_anual']:.1f} mm")
        reporte.append(f"📈 Precipitación promedio mensual: {p['promedio_mensual']:.1f} mm")
        reporte.append(f"⬆️ Máximo histórico mensual: {p['maximo']:.1f} mm")
        reporte.append(f"⬇️ Mínimo histórico mensual: {p['minimo']:.1f} mm")
        reporte.append(f"📊 Coeficiente de variación: {p['coef_variacion']:.1f}%")
        
        if p['coef_variacion'] < 20:
            variabilidad = "Baja (clima estable)"
        elif p['coef_variacion'] < 40:
            variabilidad = "Moderada"
        else:
            variabilidad = "Alta (clima variable)"
        reporte.append(f"🎯 Variabilidad climática: {variabilidad}")
    
    reporte.append("")
    
    if 'temperatura' in estadisticas:
        t = estadisticas['temperatura']
        reporte.append("🌡️ ANÁLISIS DE TEMPERATURA")
        reporte.append("-" * 30)
        reporte.append(f"🌡️ Temperatura promedio: {t['promedio']:.1f}°C")
        reporte.append(f"🔥 Temperatura máxima registrada: {t['maximo']:.1f}°C")
        reporte.append(f"❄️ Temperatura mínima registrada: {t['minimo']:.1f}°C")
        reporte.append(f"📏 Amplitud térmica: {t['amplitud']:.1f}°C")
        reporte.append("")
    
    if 'humedad' in estadisticas:
        h = estadisticas['humedad']
        reporte.append("💧 ANÁLISIS DE HUMEDAD")
        reporte.append("-" * 30)
        reporte.append(f"💧 Humedad relativa promedio: {h['promedio']:.1f}%")
        reporte.append(f"⬆️ Humedad máxima: {h['maximo']:.1f}%")
        reporte.append(f"⬇️ Humedad mínima: {h['minimo']:.1f}%")
        reporte.append("")
    
    if 'estacional' in estadisticas:
        reporte.append("🍂 ANÁLISIS ESTACIONAL")
        reporte.append("-" * 30)
        
        estaciones_emoji = {
            'Verano': '☀️',
            'Otoño': '🍂', 
            'Invierno': '❄️',
            'Primavera': '🌸'
        }
        
        for estacion, datos in estadisticas['estacional'].items():
            emoji = estaciones_emoji.get(estacion, '🌿')
            reporte.append(f"{emoji} {estacion}:")
            reporte.append(f"   • Precipitación: {datos['precipitacion_promedio']:.1f} mm/mes")
            if datos['temperatura_promedio'] is not None:
                reporte.append(f"   • Temperatura: {datos['temperatura_promedio']:.1f}°C")
        reporte.append("")
    
    reporte.append("🔮 PREDICCIÓN FUTURA (24 MESES)")
    reporte.append("-" * 30)
    
    if not forecast.empty:
        today = datetime.date.today()
        forecast_future = forecast[forecast['ds'].dt.date > today]
        
        if not forecast_future.empty:
            pred_promedio = forecast_future['yhat'].mean()
            pred_max = forecast_future['yhat'].max()
            pred_min = forecast_future['yhat'].min()
            
            reporte.append(f"📈 Precipitación promedio predicha: {pred_promedio:.1f} mm/mes")
            reporte.append(f"⬆️ Máximo predicho: {pred_max:.1f} mm/mes")
            reporte.append(f"⬇️ Mínimo predicho: {pred_min:.1f} mm/mes")
            
            if 'precipitacion' in estadisticas:
                hist_promedio = estadisticas['precipitacion']['promedio_mensual']
                diferencia = pred_promedio - hist_promedio
                porcentaje = (diferencia / hist_promedio) * 100
                
                if abs(porcentaje) < 5:
                    tendencia = "🟢 Normal (similar al promedio histórico)"
                elif porcentaje > 0:
                    tendencia = f"🔵 Húmedo ({porcentaje:+.1f}% sobre el promedio)"
                else:
                    tendencia = f"🟡 Seco ({porcentaje:+.1f}% bajo el promedio)"
                
                reporte.append(f"📊 Tendencia predicha: {tendencia}")
        else:
            reporte.append("⚠️ No hay predicciones futuras disponibles")
    
    reporte.append("")
    
    reporte.append("⚠️ ALERTAS Y RECOMENDACIONES")
    reporte.append("-" * 30)
    
    alertas = []
    
    if 'precipitacion' in estadisticas:
        p = estadisticas['precipitacion']
        if p['coef_variacion'] > 50:
            alertas.append("🟡 Alta variabilidad en precipitaciones - Planificar sistemas de riego flexibles")
        
        if p['promedio_anual'] < 500:
            alertas.append("🔴 Región de baja precipitación - Considerar cultivos resistentes a sequía")
        elif p['promedio_anual'] > 1500:
            alertas.append("🔵 Región de alta precipitación - Atención al drenaje y enfermedades fúngicas")
    
    if not alertas:
        alertas.append("✅ No se detectaron alertas climáticas significativas")
    
    for alerta in alertas:
        reporte.append(alerta)
    
    reporte.append("")
    reporte.append("📝 NOTAS TÉCNICAS")
    reporte.append("-" * 30)
    reporte.append("• Datos obtenidos de NASA POWER API (satélites y reanálisis)")
    reporte.append("• Predicciones generadas con modelo Prophet de Facebook")
    reporte.append("• Resolución temporal: mensual | Período: 1981-2025")
    reporte.append("• Las predicciones incluyen intervalos de confianza del 80%")
    
    return "\n".join(reporte)
