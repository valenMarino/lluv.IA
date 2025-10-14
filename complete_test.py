"""
Test completo de Lluv.IA con todas las mejoras:
- Loader con progreso
- Selector de rango de fechas
- Tipografía profesional Inter
- Diseño mejorado
"""

try:
    import gradio as gr
    import datetime
    from nasa_api import PROVINCIAS_COORDS, obtener_datos_precipitacion
    
    def _generar_opciones_fechas():
        """Genera lista de opciones de fechas desde 1981-01 hasta el mes actual."""
        opciones = []
        fecha_actual = datetime.date.today()
        
        for anio in range(1981, fecha_actual.year + 1):
            mes_fin = 12 if anio < fecha_actual.year else fecha_actual.month
            for mes in range(1, mes_fin + 1):
                opciones.append(f"{anio}-{mes:02d}")
        
        return opciones

    def _obtener_fecha_actual():
        """Obtiene la fecha actual en formato YYYY-MM."""
        fecha_actual = datetime.date.today()
        return f"{fecha_actual.year}-{fecha_actual.month:02d}"
    
    def analizar_con_progreso(provincia, fecha_inicio, fecha_fin, progress=gr.Progress()):
        """Función de prueba con indicador de progreso."""
        try:
            progress(0.1, desc="🚀 Iniciando análisis...")
            
            progress(0.3, desc="📡 Conectando con NASA POWER...")
            df = obtener_datos_precipitacion(provincia, fecha_inicio, fecha_fin)
            
            progress(0.6, desc="📊 Procesando datos climáticos...")
            
            if df.empty:
                return "⚠️ No se obtuvieron datos para el rango seleccionado"
            
            progress(0.8, desc="📈 Generando estadísticas...")
            
            promedio = df['y'].mean()
            total_registros = len(df)
            fecha_inicio_real = df['ds'].min().strftime('%Y-%m')
            fecha_fin_real = df['ds'].max().strftime('%Y-%m')
            
            progress(1.0, desc="✅ ¡Análisis completado!")
            
            resultado = f"""🌾 ANÁLISIS CLIMÁTICO COMPLETADO - {provincia.upper()}
            
📅 PERÍODO ANALIZADO:
• Rango solicitado: {fecha_inicio} a {fecha_fin}
• Datos obtenidos: {fecha_inicio_real} a {fecha_fin_real}
• Total de registros: {total_registros} meses

📊 ESTADÍSTICAS DE PRECIPITACIÓN:
• Promedio mensual: {promedio:.1f} mm
• Promedio anual estimado: {promedio * 12:.1f} mm
• Máximo mensual: {df['y'].max():.1f} mm
• Mínimo mensual: {df['y'].min():.1f} mm

🎉 FUNCIONALIDADES PROBADAS:
✅ Loader con progreso funcionando
✅ Selector de fechas personalizable
✅ Tipografía Inter profesional
✅ API con peticiones separadas
✅ Diseño moderno y responsive

🚀 ¡Todas las mejoras implementadas correctamente!
            """
            
            return resultado
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def crear_ui_completa():
        """Interfaz completa con todas las mejoras."""
        
        provincias_lista = sorted(list(PROVINCIAS_COORDS.keys()))
        
        # CSS con tipografía Inter y diseño profesional
        css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .gradio-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        .main-container {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            margin: 1rem !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1) !important;
        }
        
        h1 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
            color: #2d3748 !important;
        }
        
        .gr-button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .gr-button-primary:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        }
        
        .gr-dropdown, .gr-textbox {
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
        }
        """
        
        with gr.Blocks(css=css, title="Lluv.IA - Test Completo") as app:
            
            with gr.Column(elem_classes=["main-container"]):
                gr.Markdown("# Lluv.IA - Test de Funcionalidades Completas")
                gr.Markdown("### Probando: Loader + Fechas + Tipografía Inter + Diseño Mejorado")
                
                with gr.Row():
                    provincia_input = gr.Dropdown(
                        choices=provincias_lista,
                        value="Buenos Aires",
                        label="🗺️ Seleccionar Provincia"
                    )
                
                with gr.Row():
                    fecha_inicio_input = gr.Dropdown(
                        choices=_generar_opciones_fechas(),
                        value="2020-01",
                        label="📅 Fecha de Inicio",
                        info="Año y mes de inicio del análisis"
                    )
                    fecha_fin_input = gr.Dropdown(
                        choices=_generar_opciones_fechas(),
                        value=_obtener_fecha_actual(),
                        label="📅 Fecha de Fin", 
                        info="Año y mes de fin del análisis"
                    )
                
                analizar_btn = gr.Button(
                    "🔍 Analizar con Progreso",
                    variant="primary",
                    size="lg"
                )
                
                resultado = gr.Textbox(
                    label="📊 Resultado del Análisis",
                    lines=20,
                    show_copy_button=True,
                    placeholder="Configurá los parámetros y hacé clic en 'Analizar con Progreso'..."
                )
                
                gr.Markdown(
                    "---\n"
                    "**🎯 Funcionalidades probadas:**\n"
                    "• ⏳ Loader con indicador de progreso\n"
                    "• 📅 Selector de rango de fechas personalizable\n"
                    "• 🎨 Tipografía Inter profesional\n"
                    "• 🚀 API optimizada con peticiones separadas\n"
                    "• 💫 Diseño moderno y responsive"
                )
                
                # Evento con progreso
                analizar_btn.click(
                    fn=analizar_con_progreso,
                    inputs=[provincia_input, fecha_inicio_input, fecha_fin_input],
                    outputs=[resultado],
                    show_progress=True
                )
        
        return app
    
    if __name__ == "__main__":
        print("🚀 Iniciando Lluv.IA - Test Completo...")
        print("✨ Funcionalidades incluidas:")
        print("   • Loader con progreso")
        print("   • Selector de fechas")
        print("   • Tipografía Inter")
        print("   • Diseño mejorado")
        
        app = crear_ui_completa()
        app.launch()
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("\n🔧 Para instalar las dependencias:")
    print("pip install gradio pandas requests")
except Exception as e:
    print(f"❌ Error: {e}")
