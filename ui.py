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
    
    # CSS mejorado con tipografía profesional
    custom_css = """
    /* Importar fuente profesional */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Tema principal */
    .gradio-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Contenedor principal */
    .main-container {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        margin: 1rem !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Títulos con tipografía profesional */
    h1 {
        color: #2d3748 !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.025em !important;
    }
    
    h3 {
        color: #4a5568 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.01em !important;
    }
    
    /* Texto general */
    body, .gr-textbox, .gr-dropdown, .gr-button, label {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Controles */
    .gr-dropdown {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
    }
    
    .gr-dropdown:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Botón principal con loader */
    .gr-button-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        color: white !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
    }
    
    .gr-button-primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    .gr-button-primary:disabled {
        opacity: 0.7 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }
    
    /* Loader spinner */
    .loading-spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Checkboxes */
    .gr-checkbox {
        margin: 0.5rem 0 !important;
    }
    
    /* Área de texto */
    .gr-textbox {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    /* Pestañas */
    .gr-tabs {
        margin-top: 2rem !important;
    }
    
    .gr-tab-nav {
        background: #f7fafc !important;
        border-radius: 12px 12px 0 0 !important;
        border: none !important;
    }
    
    .gr-tab-nav button {
        border-radius: 8px !important;
        margin: 4px !important;
        border: none !important;
        background: transparent !important;
        color: #4a5568 !important;
        font-weight: 500 !important;
    }
    
    .gr-tab-nav button.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Gráficos */
    .gr-plot {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        background: white !important;
    }
    
    /* Información lateral */
    .info-panel {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        color: white !important;
        margin-left: 1rem !important;
    }
    
    .info-panel h3 {
        color: white !important;
        margin-bottom: 1rem !important;
    }
    
    .info-panel p {
        color: rgba(255,255,255,0.9) !important;
        line-height: 1.6 !important;
    }
    """
    
    # Lista de provincias ordenada
    provincias_lista = sorted(list(PROVINCIAS_COORDS.keys()))
    
    # Interfaz mejorada
    with gr.Blocks(css=custom_css, title="Lluv.IA", theme=gr.themes.Soft()) as app:
        
        with gr.Column(elem_classes=["main-container"]):
            # Encabezado
            gr.Markdown("#Lluv.IA - Análisis Meteorológico Inteligente")
            gr.Markdown("### 🇦🇷 Predicción y análisis climático para todas las provincias argentinas")
            
            with gr.Row():
                with gr.Column(scale=3):
                    # Controles principales
                    provincia_input = gr.Dropdown(
                        choices=provincias_lista,
                        value="Buenos Aires",
                        label="🗺️ Seleccionar Provincia",
                        info="Elegí una provincia argentina para analizar"
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
                    gr.Markdown(
                        "### 📋 Información\n\n"
                        "🌧️ **Precipitaciones**\n"
                        "Datos históricos 1981-2025\n\n"
                        "🌡️ **Temperatura**\n"
                        "Promedio, máxima y mínima\n\n"
                        "💧 **Humedad**\n"
                        "Humedad relativa del aire\n\n"
                        "🔮 **Predicción**\n"
                        "Proyección a 24 meses\n\n"
                        "📊 **Métricas**\n"
                        "• Promedios históricos\n"
                        "• Tendencias estacionales\n"
                        "• Índices de variabilidad\n"
                        "• Alertas climáticas"
                    )
            
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
                "*Desarrollado para el sector agropecuario argentino* 🇦🇷"
            )
        
        # Eventos con progress
        analizar_btn.click(
            fn=analizar_provincia_completo,
            inputs=[provincia_input, incluir_temp, incluir_comp, fecha_inicio_input, fecha_fin_input],
            outputs=[reporte_output, plot_historico, plot_prediccion, plot_temperatura, plot_comparativo],
            show_progress=True
        )
    
    return app
