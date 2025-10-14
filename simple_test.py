"""
Versión de prueba de Lluv.IA con API mejorada
Prueba las peticiones separadas a NASA POWER
"""

try:
    import gradio as gr
    from nasa_api import PROVINCIAS_COORDS, obtener_datos_precipitacion
    
    def analizar_con_api(provincia):
        """Función que prueba la API real"""
        try:
            print(f"🔄 Obteniendo datos de {provincia}...")
            df = obtener_datos_precipitacion(provincia)
            
            if df.empty:
                return f"⚠️ No se obtuvieron datos para {provincia}"
            
            promedio = df['y'].mean()
            total_registros = len(df)
            fecha_inicio = df['ds'].min().strftime('%Y-%m')
            fecha_fin = df['ds'].max().strftime('%Y-%m')
            
            resultado = f"""✅ Datos obtenidos exitosamente para {provincia}
            
📊 RESUMEN:
• Total de registros: {total_registros}
• Período: {fecha_inicio} a {fecha_fin}
• Precipitación promedio: {promedio:.1f} mm/mes
• Precipitación anual estimada: {promedio * 12:.1f} mm/año

🎉 ¡La API con peticiones separadas funciona correctamente!
            """
            
            return resultado
            
        except Exception as e:
            return f"❌ Error al obtener datos de {provincia}: {str(e)}"
    
    def crear_ui_test():
        """Interfaz de prueba con API real"""
        
        provincias_lista = sorted(list(PROVINCIAS_COORDS.keys()))
        
        # CSS mejorado
        css = """
        .gradio-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .main-container {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            margin: 1rem !important;
        }
        """
        
        with gr.Blocks(css=css, title="Lluv.IA - Test API") as app:
            
            with gr.Column(elem_classes=["main-container"]):
                gr.Markdown("# Lluv.IA - Test de API Mejorada")
                gr.Markdown("### Probando peticiones separadas a NASA POWER")
                
                provincia_input = gr.Dropdown(
                    choices=provincias_lista,
                    value="Buenos Aires",
                    label="🗺️ Seleccionar Provincia",
                    info="Elegí una provincia para probar la API"
                )
                
                analizar_btn = gr.Button(
                    "🔍 Probar API",
                    variant="primary",
                    size="lg"
                )
                
                resultado = gr.Textbox(
                    label="📊 Resultado del Test",
                    lines=12,
                    show_copy_button=True,
                    placeholder="Seleccioná una provincia y hacé clic en 'Probar API'..."
                )
                
                gr.Markdown(
                    "---\n"
                    "**Nota:** Este test hace peticiones reales a NASA POWER API\n"
                    "Puede tardar unos segundos en obtener los datos"
                )
                
                analizar_btn.click(
                    fn=analizar_con_api,
                    inputs=[provincia_input],
                    outputs=[resultado]
                )
        
        return app
    
    if __name__ == "__main__":
        print("🚀 Iniciando Lluv.IA - Test de API...")
        app = crear_ui_test()
        app.launch()
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("\n🔧 Para instalar las dependencias:")
    print("1. Ejecutar: pip install gradio pandas requests")
    print("2. O usar: setup_quick.bat")
except Exception as e:
    print(f"❌ Error: {e}")
