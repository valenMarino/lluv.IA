from ui import crear_ui
from auth import obtener_funcion_auth
import os

if __name__ == "__main__":
    app = crear_ui()
    
    # Configuración de autenticación
    # Por defecto, Gradio pide login en cada nueva sesión/navegador/IP
    # No guarda cookies persistentes, así que cada acceso nuevo requiere login
    app.launch(
        auth=obtener_funcion_auth(),
        auth_message="Ingresá tus credenciales",
        share=False,  # No compartir públicamente por defecto
        inbrowser=True,  # Abrir automáticamente en navegador
        server_name="0.0.0.0" if os.getenv("SPACE_ID") else "127.0.0.1",  # Para Hugging Face
        server_port=7860
    )