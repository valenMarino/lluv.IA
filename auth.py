"""
Sistema de autenticación para Lluv.IA
Valida credenciales desde auth_config.json o variables de entorno
"""
import json
import os
import re
from typing import Optional, Tuple

def validar_password(password: str) -> Tuple[bool, str]:
    """
    Valida que la contraseña cumpla con los requisitos de seguridad:
    - Mínimo 10 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 número
    - Al menos 1 símbolo especial
    
    Returns:
        Tuple[bool, str]: (es_valida, mensaje_error)
    """
    if len(password) < 10:
        return False, "La contraseña debe tener al menos 10 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not re.search(r'[0-9]', password):
        return False, "La contraseña debe contener al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;\'`~]', password):
        return False, "La contraseña debe contener al menos un símbolo especial"
    
    return True, "Contraseña válida"

def cargar_usuarios() -> dict:
    """
    Carga usuarios desde auth_config.json o variables de entorno.
    Prioridad: Variables de entorno > archivo JSON
    
    Variables de entorno esperadas:
    - LLUVAI_AUTH_EMAIL
    - LLUVAI_AUTH_PASSWORD
    """
    usuarios = {}
    
    # Intentar cargar desde variables de entorno (para Hugging Face Spaces)
    env_email = os.getenv("LLUVAI_AUTH_EMAIL")
    env_password = os.getenv("LLUVAI_AUTH_PASSWORD")
    
    if env_email and env_password:
        usuarios[env_email] = env_password
        return usuarios
    
    # Fallback: cargar desde archivo JSON local
    try:
        with open('auth_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            for user in config.get('users', []):
                email = user.get('email')
                password = user.get('password')
                if email and password:
                    usuarios[email] = password
    except FileNotFoundError:
        print("⚠️ Advertencia: No se encontró auth_config.json. Usando credenciales por defecto.")
        # Credenciales por defecto (solo para desarrollo local)
        usuarios["admin@riego.com"] = "Admin@2024!"
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer auth_config.json: {e}")
    
    return usuarios

def autenticar(email: str, password: str) -> bool:
    """
    Verifica si las credenciales son válidas.
    
    Args:
        email: Email del usuario
        password: Contraseña del usuario
    
    Returns:
        bool: True si las credenciales son correctas
    """
    usuarios = cargar_usuarios()
    
    # Verificar si el email existe y la contraseña coincide
    if email in usuarios and usuarios[email] == password:
        return True
    
    return False

def obtener_funcion_auth():
    """
    Retorna una función compatible con Gradio auth.
    
    Returns:
        callable: Función que recibe (username, password) y retorna bool
    """
    def auth_fn(username: str, password: str) -> bool:
        return autenticar(username, password)
    
    return auth_fn
