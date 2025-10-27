# Integración con Qdrant DB

## Descripción

La aplicación ahora incluye integración con Qdrant Cloud para búsqueda vectorial de contexto relevante. Esta funcionalidad **solo se activa cuando OpenAI está configurado**, ya que utiliza los embeddings de OpenAI para realizar búsquedas semánticas en la base de datos vectorial.

## Requisitos

1. **OpenAI API Key**: Necesaria para generar embeddings y usar el chat con IA
2. **Qdrant Cloud**: Cluster en la nube con una colección de datos climáticos/agrícolas
3. **Qdrant API Key**: Credenciales de acceso a tu cluster

## Configuración

### 1. Variables de Entorno

#### Opción A: Desarrollo Local (archivo .env)

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# OpenAI (obligatorio para usar Qdrant)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Qdrant Cloud (opcional)
QDRANT_URL=https://tu-cluster.qdrant.io:6333
QDRANT_API_KEY=tu_api_key_aqui

# Modelo de embeddings (debe coincidir con el usado en Qdrant)
EMBEDDING_MODEL=text-embedding-3-large
```

**Importante**: El `EMBEDDING_MODEL` debe ser el mismo que usaste para crear los vectores en Qdrant:
- `text-embedding-3-small` → 1536 dimensiones
- `text-embedding-3-large` → 3072 dimensiones (por defecto)

Si usas archivo `.env`, instala también:
```bash
pip install python-dotenv
```

#### Opción B: Hugging Face Spaces

En Hugging Face Spaces, configura los secretos en la configuración del Space:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (opcional, por defecto: gpt-4o-mini)
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `EMBEDDING_MODEL` (opcional, por defecto: text-embedding-3-large)

Las variables ya estarán disponibles automáticamente, no necesitas `python-dotenv`.

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `qdrant-client>=1.7.0` - Cliente de Qdrant

**Nota**: `python-dotenv` es opcional y solo necesario para desarrollo local con archivo `.env`.

### 3. Carga de Variables

El archivo `app.py` detecta automáticamente el entorno:

```python
# Intenta cargar .env si está disponible (desarrollo local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Si no está instalado, usa variables del sistema (Hugging Face Spaces)
    pass
```

Esto permite que la aplicación funcione en ambos entornos sin modificaciones.

## Funcionamiento

### Flujo de Búsqueda

1. **Detección de OpenAI**: Al iniciar el chat, el sistema verifica si OpenAI está activo
2. **Inicialización de Qdrant**: Si OpenAI está presente, se intenta conectar a Qdrant
3. **Búsqueda Vectorial**: Cuando el usuario envía un mensaje:
   - Se genera un embedding del mensaje usando OpenAI (modelo configurable, por defecto `text-embedding-3-large`)
   - Se buscan los 3 documentos más relevantes en Qdrant
   - El contexto se inyecta en el prompt del LLM
4. **Respuesta Enriquecida**: El modelo responde usando tanto el reporte climático como el contexto de Qdrant

### Estructura de la Colección

La colección en Qdrant debe tener la siguiente estructura:

```python
{
    "text": "Contenido del documento",
    "metadata": {
        "source": "fuente_del_documento",
        "tipo": "recomendacion_riego|info_climatica|etc",
        # ... otros metadatos
    }
}
```

## Comportamiento sin Qdrant

Si Qdrant no está configurado o no está disponible:

- ✅ La aplicación funciona normalmente
- ✅ El chat usa solo el reporte climático generado
- ⚠️ No se obtiene contexto adicional de la base de conocimientos
- 📝 Se muestra un mensaje en consola: "⚠️ Qdrant no disponible"

## Comportamiento sin OpenAI

Si OpenAI no está configurado:

- ✅ La aplicación funciona con Hugging Face
- ❌ Qdrant NO se inicializa (requiere OpenAI para embeddings)
- ✅ El chat funciona con modelos de Hugging Face

## Logs y Debugging

El sistema imprime mensajes informativos en consola:

```
✅ Qdrant conectado y disponible para búsqueda vectorial
📚 Contexto de Qdrant obtenido (1234 caracteres)
⚠️ Qdrant no disponible (verifica QDRANT_URL y QDRANT_API_KEY)
⚠️ Error buscando en Qdrant: [mensaje de error]
```

## Código Relevante

### Archivos Modificados

1. **`mcp_core.py`**: 
   - Clase `QdrantRetriever` para búsqueda vectorial
   - Método `is_openai_active()` en clase `LLM`

2. **`ui.py`**:
   - Función `_chat_respond` actualizada para usar Qdrant
   - Estado `qdrant_state` para mantener la conexión

3. **`agents/advisor_agent.py`**:
   - Método `_build_prompt` actualizado para incluir contexto de Qdrant

4. **`requirements.txt`**:
   - Dependencia `qdrant-client>=1.7.0`

## Ejemplo de Uso

```python
# En tu código Python
from mcp_core import QdrantRetriever

# Inicializar (requiere variables de entorno)
retriever = QdrantRetriever(collection_name="recomendador-de-riego")

# Verificar disponibilidad
if retriever.is_available():
    # Buscar contexto
    context = retriever.get_context("¿Cómo regar en época de sequía?", limit=3)
    print(context)
```

## Troubleshooting

### Error: "No se pudo conectar a Qdrant"

- Verifica que `QDRANT_URL` y `QDRANT_API_KEY` estén correctamente configuradas
- Asegúrate de que tu cluster de Qdrant esté activo
- Verifica la conectividad de red

### Error: "Error generando embedding"

- Verifica que `OPENAI_API_KEY` sea válida
- Revisa tu cuota de API de OpenAI
- Asegúrate de tener créditos disponibles

### Qdrant no se inicializa

- Verifica que OpenAI esté configurado primero
- Revisa los logs en consola para mensajes de error
- Asegúrate de que `qdrant-client` esté instalado

## Seguridad

- ⚠️ **Nunca** commitees el archivo `.env` al repositorio
- ✅ Usa `.env.example` como plantilla
- ✅ Mantén tus API keys seguras y rotadas regularmente
- ✅ Usa variables de entorno en producción
