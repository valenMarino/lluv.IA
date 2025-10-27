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
from mcp_core import MCPContext, QdrantRetriever
from agents import AdvisorAgent

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
        reporte = generar_reporte_climatico(provincia, df_completo, forecast, estadisticas, fecha_inicio, fecha_fin)
        
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
        # Devolvemos el reporte dos veces: para el Textbox y para el gr.State que usa el chat
        return reporte, *graficos, reporte
        
    except Exception as e:
        mensaje = f"❌ Error al procesar datos de {provincia}: {str(e)}"
        return mensaje, None, None, None, None, ""

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
                
                with gr.TabItem("🤖 Recomendador de riego"):
                    chat = gr.Chatbot(label="Recomendador de riego", height=400, type='messages')
                    with gr.Row():
                        user_msg = gr.Textbox(placeholder="Preguntá: '¿Cómo viene la tendencia de lluvias en Córdoba?'", label="Mensaje", scale=4)
                        send_btn = gr.Button("Enviar", variant="primary", scale=1)
                    backend_label = gr.HTML(value='<div class="backend-label">Modelo: (detectando)</div>')
                    # Estados MCP
                    mcp_state = gr.State(value=None)
                    advisor_state = gr.State(value=None)
                    reporte_state = gr.State(value=None)
                    qdrant_state = gr.State(value=None)
                    
                    def _chat_respond(message, history, mcp, advisor, reporte_txt, qdrant_retriever):
                        if mcp is None or advisor is None:
                            mcp = MCPContext()
                            advisor = AdvisorAgent(mcp, model="google/flan-t5-base")
                        
                        # Inicializar Qdrant solo si OpenAI está activo
                        if qdrant_retriever is None and advisor.llm.is_openai_active():
                            qdrant_retriever = QdrantRetriever()
                            if qdrant_retriever.is_available():
                                print("✅ Qdrant conectado y disponible para búsqueda vectorial")
                            else:
                                print("⚠️ Qdrant no disponible (verifica QDRANT_URL y QDRANT_API_KEY)")
                                qdrant_retriever = None
                        # Normalizar historial al formato messages [{role, content}]
                        history = history or []
                        if history and isinstance(history[0], (list, tuple)):
                            try:
                                history = (
                                    [{"role": "user", "content": u} , {"role": "assistant", "content": a}]
                                    for (u, a) in history
                                )
                            except Exception:
                                history = []
                            # Aplanar pares en una sola lista
                            flat = []
                            for pair in history:
                                flat.extend(pair)
                            history = flat
                        if not message:
                            # Actualizar backend label aun sin mensaje
                            try:
                                bk = advisor.llm.backend()
                                mcp.set("llm_backend", bk)
                            except Exception:
                                bk = "(desconocido)"
                            return history, mcp, advisor, reporte_txt, qdrant_retriever, f'<div class="backend-label">Modelo: {bk}</div>'
                        
                        # Buscar contexto en Qdrant solo si OpenAI está activo
                        qdrant_context = ""
                        if qdrant_retriever is not None and qdrant_retriever.is_available():
                            try:
                                qdrant_context = qdrant_retriever.get_context(message, limit=3)
                                if qdrant_context:
                                    mcp.set("qdrant_context", qdrant_context)
                                    print(f"📚 Contexto de Qdrant obtenido ({len(qdrant_context)} caracteres)")
                            except Exception as e:
                                print(f"⚠️ Error obteniendo contexto de Qdrant: {e}")
                        
                        # Inyectar el reporte detallado en el contexto compartido
                        try:
                            if isinstance(reporte_txt, str) and len(reporte_txt.strip()) > 0:
                                mcp.set("reporte_detallado", reporte_txt)
                        except Exception:
                            pass
                        try:
                            reply = advisor.call(message)
                        except Exception as e:
                            reply = f"Error del asistente: {e}"
                        # Agregar mensajes al historial en formato messages
                        history = history + [
                            {"role": "user", "content": message},
                            {"role": "assistant", "content": reply},
                        ]
                        # Guardar backend y devolver etiqueta
                        try:
                            bk = advisor.llm.backend()
                            mcp.set("llm_backend", bk)
                        except Exception:
                            bk = "(desconocido)"
                        return history, mcp, advisor, reporte_txt, qdrant_retriever, f'<div class="backend-label">Modelo: {bk}</div>'
                    
                    send_btn.click(
                        fn=_chat_respond,
                        inputs=[user_msg, chat, mcp_state, advisor_state, reporte_state, qdrant_state],
                        outputs=[chat, mcp_state, advisor_state, reporte_state, qdrant_state, backend_label]
                    )
                    user_msg.submit(
                        fn=_chat_respond,
                        inputs=[user_msg, chat, mcp_state, advisor_state, reporte_state, qdrant_state],
                        outputs=[chat, mcp_state, advisor_state, reporte_state, qdrant_state, backend_label]
                    )
            
            
        
        # Eventos con progress
        analizar_btn.click(
            fn=analizar_provincia_completo,
            inputs=[provincia_input, incluir_temp, incluir_comp, fecha_inicio_input, fecha_fin_input],
            outputs=[reporte_output, plot_historico, plot_prediccion, plot_temperatura, plot_comparativo, reporte_state],
            show_progress=True
        )
    
    return app
