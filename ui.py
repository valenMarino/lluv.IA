import gradio as gr
import pandas as pd
import datetime
from nasa_api import obtener_datos_meteorologicos, PROVINCIAS_COORDS
from forecast_model import predecir_precipitacion
from utils import (
    graficar_historico, graficar_prediccion, 
    graficar_temperatura, graficar_comparativo_anual,
    calcular_estadisticas_climaticas, generar_reporte_climatico
)

def _generar_opciones_fechas():
    """Genera lista de opciones de fechas desde 1981-01 hasta el mes actual."""
    opciones = []
    fecha_actual = datetime.date.today()
    
    for año in range(1981, fecha_actual.year + 1):
        mes_fin = 12 if año < fecha_actual.year else fecha_actual.month
        for mes in range(1, mes_fin + 1):
            opciones.append(f"{año}-{mes:02d}")
    
    return opciones

def _obtener_fecha_actual():
    """Obtiene la fecha actual en formato YYYY-MM."""
    fecha_actual = datetime.date.today()
    return f"{fecha_actual.year}-{fecha_actual.month:02d}"

def analizar_provincia_completo(provincia, incluir_temperatura=True, incluir_comparativo=True, fecha_inicio=None, fecha_fin=None, progress=gr.Progress()):
    """Análisis meteorológico completo de una provincia con indicador de progreso."""
    try:
        progress(0.1, desc="Iniciando análisis...")
        
        # Obtener datos meteorológicos completos
        progress(0.2, desc="Obteniendo datos de NASA POWER...")
        df_completo = obtener_datos_meteorologicos(provincia, fecha_inicio, fecha_fin)
        
        progress(0.4, desc="Procesando datos climáticos...")
        df_precipitacion = df_completo[['ds', 'y']]
        
        # Generar predicción
        progress(0.5, desc="Generando predicciones con IA...")
        forecast = predecir_precipitacion(df_precipitacion)
        
        # Calcular estadísticas climáticas
        progress(0.6, desc="Calculando estadísticas...")
        estadisticas = calcular_estadisticas_climaticas(df_completo)
        
        # Generar reporte detallado
        progress(0.7, desc="Generando reporte detallado...")
        reporte = generar_reporte_climatico(provincia, df_completo, forecast, estadisticas)
        
        # Generar gráficos
        progress(0.8, desc="Creando visualizaciones...")
        graficos = []
        
        # Gráfico de precipitación histórica (siempre incluido)
        graficos.append(graficar_historico(df_precipitacion, provincia))
        
        # Gráfico de predicción (siempre incluido)
        graficos.append(graficar_prediccion(forecast, provincia))
        
        # Gráfico de temperatura (opcional)
        if incluir_temperatura and 'temperatura' in df_completo.columns:
            graficos.append(graficar_temperatura(df_completo, provincia))
        else:
            graficos.append(None)
        
        # Gráfico comparativo anual (opcional)
        if incluir_comparativo:
            graficos.append(graficar_comparativo_anual(df_completo, provincia))
        else:
            graficos.append(None)
        
        progress(1.0, desc="¡Análisis completado!")
        return reporte, *graficos
        
    except Exception as e:
        mensaje = f"❌ Error al procesar datos de {provincia}: {str(e)}"
        return mensaje, None, None, None, None

def crear_ui():
    """Crea la interfaz de usuario mejorada y funcional."""
    
    # Cargar CSS desde archivo externo
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            custom_css = f.read()
    except FileNotFoundError:
        # CSS de respaldo en caso de que no se encuentre el archivo
        custom_css = ""
    
    # Lista de provincias ordenada
    provincias_lista = sorted(list(PROVINCIAS_COORDS.keys()))
    
    # Interfaz mejorada
    with gr.Blocks(css=custom_css, title="Lluv.IA", theme=gr.themes.Soft()) as app:
        
        with gr.Column(elem_classes=["main-container"]):
            # Header profesional
            with gr.Column(elem_classes=["header-container"]):
                gr.HTML('<h1 class="main-title">Lluv.IA</h1>')
                gr.HTML('<p class="main-subtitle">Predicción y análisis climático para todas las provincias argentinas</p>')
            
            with gr.Row():
                with gr.Column(scale=3):
                    # Controles principales
                    provincia_input = gr.Dropdown(
                        choices=provincias_lista,
                        value="Buenos Aires",
                        label="🗺️ Seleccionar Provincia",
                        info="Elegí una provincia para analizar"
                    )
                    
                    # Selector de rango de fechas
                    with gr.Row():
                        fecha_inicio_input = gr.Dropdown(
                            choices=_generar_opciones_fechas(),
                            value="1981-01",
                            label="📅 Fecha de Inicio",
                            info="Año y mes de inicio del análisis"
                        )
                        fecha_fin_input = gr.Dropdown(
                            choices=_generar_opciones_fechas(),
                            value=_obtener_fecha_actual(),
                            label="📅 Fecha de Fin",
                            info="Año y mes de fin del análisis"
                        )
                    
                    with gr.Row():
                        incluir_temp = gr.Checkbox(
                            value=True,
                            label="🌡️ Incluir análisis de temperatura"
                        )
                        incluir_comp = gr.Checkbox(
                            value=True,
                            label="📊 Incluir comparativo anual"
                        )
                    
                    analizar_btn = gr.Button(
                        "🔍 Analizar Clima",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=1, elem_classes=["info-panel"]):
                    gr.HTML("""
                        <h3>📋 Información</h3>
                        
                        <div style="margin-bottom: 1rem;">
                            <div style="color: #ffffff; font-weight: 600; margin-bottom: 0.25rem;">
                                🌧️ <strong>Precipitaciones</strong>
                            </div>
                            <div style="color: #f1f5f9; font-size: 0.9rem;">
                                Datos históricos 1981-2025
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <div style="color: #ffffff; font-weight: 600; margin-bottom: 0.25rem;">
                                🌡️ <strong>Temperatura</strong>
                            </div>
                            <div style="color: #f1f5f9; font-size: 0.9rem;">
                                Promedio, máxima y mínima
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <div style="color: #ffffff; font-weight: 600; margin-bottom: 0.25rem;">
                                💧 <strong>Humedad</strong>
                            </div>
                            <div style="color: #f1f5f9; font-size: 0.9rem;">
                                Humedad relativa del aire
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <div style="color: #ffffff; font-weight: 600; margin-bottom: 0.25rem;">
                                🔮 <strong>Predicción</strong>
                            </div>
                            <div style="color: #f1f5f9; font-size: 0.9rem;">
                                Proyección a 24 meses
                            </div>
                        </div>
                        
                        <div>
                            <div style="color: #ffffff; font-weight: 600; margin-bottom: 0.25rem;">
                                📊 <strong>Métricas</strong>
                            </div>
                            <div style="color: #f1f5f9; font-size: 0.9rem;">
                                • Promedios históricos<br>
                                • Tendencias estacionales<br>
                                • Índices de variabilidad<br>
                                • Alertas climáticas
                            </div>
                        </div>
                    """)
            
            # Resultados
            reporte_output = gr.Textbox(
                label="📈 Reporte Climático Detallado",
                lines=12,
                show_copy_button=True,
                placeholder="Seleccioná una provincia y hacé clic en 'Analizar Clima' para ver el reporte completo..."
            )
            
            # Gráficos en pestañas
            with gr.Tabs():
                with gr.TabItem("🌧️ Precipitaciones Históricas"):
                    plot_historico = gr.Plot()
                
                with gr.TabItem("🔮 Predicción Futura"):
                    plot_prediccion = gr.Plot()
                
                with gr.TabItem("🌡️ Análisis de Temperatura"):
                    plot_temperatura = gr.Plot()
                
                with gr.TabItem("📊 Comparativo Anual"):
                    plot_comparativo = gr.Plot()
            
            # Pie de página
            gr.Markdown(
                "---\n"
                "🔬 **Fuente:** NASA POWER API • "
                "🤖 **IA:** Prophet (Facebook) • "
                "📅 **Actualización:** 2025\n\n"
                "*Desarrollado para el sector agropecuario argentino*"
            )
        
        # Eventos con progress
        analizar_btn.click(
            fn=analizar_provincia_completo,
            inputs=[provincia_input, incluir_temp, incluir_comp, fecha_inicio_input, fecha_fin_input],
            outputs=[reporte_output, plot_historico, plot_prediccion, plot_temperatura, plot_comparativo],
            show_progress=True
        )
    
    return app
