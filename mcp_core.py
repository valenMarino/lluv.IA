import os
from typing import Any, Dict, Optional, List

class MCPContext:
    """Minimal MCP-like shared context to coordinate agents.
    Stores arbitrary keys with get/set and allows simple namespacing.
    """
    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def ensure_namespace(self, ns: str) -> Dict[str, Any]:
        if ns not in self._store or not isinstance(self._store.get(ns), dict):
            self._store[ns] = {}
        return self._store[ns]

class BaseAgent:
    """Base class for agents using the shared MCPContext."""
    def __init__(self, context: MCPContext) -> None:
        self.context = context

    def name(self) -> str:
        return self.__class__.__name__

    def call(self, *args, **kwargs):
        raise NotImplementedError("Agent must implement call()")

# Lightweight LLM client via Hugging Face Hub (no heavy local models)
try:
    from huggingface_hub import InferenceClient
except Exception:  # keep optional
    InferenceClient = None  # type: ignore

# Optional OpenAI clients (support new and legacy SDKs)
OpenAIClientNew = None
OpenAIClientLegacy = None
try:
    from openai import OpenAI as OpenAIClientNew  # type: ignore
except Exception:
    OpenAIClientNew = None  # type: ignore
try:
    import openai as OpenAIClientLegacy  # type: ignore
except Exception:
    OpenAIClientLegacy = None  # type: ignore

class LLM:
    """Small wrapper around Hugging Face Inference API.
    If HF token or InferenceClient is not available, falls back to a rule-based response.
    """
    def __init__(self, model: str = "google/flan-t5-base", temperature: float = 0.2, max_new_tokens: int = 256):
        self.model = model
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.client: Optional[InferenceClient] = None

        # OpenAI setup (preferred if key is set)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._openai_client = None
        self._openai_mode = None  # 'new' or 'legacy'
        if self.openai_key:
            if OpenAIClientNew is not None:
                try:
                    self._openai_client = OpenAIClientNew(api_key=self.openai_key)
                    self._openai_mode = 'new'
                except Exception:
                    self._openai_client = None
            if self._openai_client is None and OpenAIClientLegacy is not None:
                try:
                    OpenAIClientLegacy.api_key = self.openai_key
                    self._openai_client = OpenAIClientLegacy
                    self._openai_mode = 'legacy'
                except Exception:
                    self._openai_client = None

        # Hugging Face setup (fallback if no OpenAI)
        if self._openai_client is None and InferenceClient is not None:
            try:
                self.client = InferenceClient(model=self.model, token=self.token)
            except Exception:
                self.client = None

    def generate(self, prompt: str) -> str:
        # Prefer OpenAI if configured
        if self._openai_client is not None and self._openai_mode == 'new':
            try:
                resp = self._openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": "Eres un asesor agroclimático. Responde en español, claro y conciso."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_new_tokens,
                )
                if resp and resp.choices:
                    return (resp.choices[0].message.content or "").strip()
            except Exception:
                pass
        elif self._openai_client is not None and self._openai_mode == 'legacy':
            try:
                resp = self._openai_client.ChatCompletion.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": "Eres un asesor agroclimático. Responde en español, claro y conciso."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_new_tokens,
                )
                if resp and resp.choices:
                    msg = resp.choices[0].get('message')
                    if isinstance(msg, dict):
                        return (msg.get('content') or "").strip()
                    # Some legacy SDKs return objects
                    try:
                        return (resp.choices[0].message['content'] or "").strip()
                    except Exception:
                        pass
            except Exception:
                pass

        # Else use Hugging Face inference if available
        if self.client is not None:
            try:
                # Try causal LM endpoint first
                out = self.client.text_generation(
                    prompt,
                    temperature=self.temperature,
                    max_new_tokens=self.max_new_tokens,
                    return_full_text=False,
                    do_sample=self.temperature > 0,
                )
                return out
            except Exception:
                # Try seq2seq endpoint (e.g., T5/FLAN)
                try:
                    out = self.client.text2text(
                        prompt,
                        temperature=self.temperature,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=self.temperature > 0,
                    )
                    # text2text returns list[dict] in some backends; normalize
                    if isinstance(out, list) and out:
                        maybe = out[0]
                        if isinstance(maybe, dict) and 'generated_text' in maybe:
                            return str(maybe['generated_text'])
                    return str(out)
                except Exception:
                    pass
        # Fallback: return empty to allow caller to compose a natural answer
        return ""

    def backend(self) -> str:
        if self._openai_client is not None and self._openai_mode == 'new':
            return f"openai:{self.openai_model}"
        if self._openai_client is not None and self._openai_mode == 'legacy':
            return f"openai-legacy:{self.openai_model}"
        if self.client is not None:
            return f"hf:{self.model}"
        return "none"
    
    def is_openai_active(self) -> bool:
        """Verifica si OpenAI está activo y configurado."""
        return self._openai_client is not None


# Optional Qdrant client
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except Exception:
    QdrantClient = None  # type: ignore


class QdrantRetriever:
    """Cliente para búsqueda vectorial en Qdrant Cloud.
    Solo se usa cuando OpenAI está activo.
    """
    def __init__(self, collection_name: str = "recomendador-de-riego"):
        self.collection_name = collection_name
        self.client: Optional[Any] = None
        self._openai_client = None
        # Usar el mismo modelo de embeddings que se usó para crear la colección
        self._embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        
        # Configuración desde variables de entorno
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Inicializar cliente Qdrant si está disponible
        if QdrantClient is not None and qdrant_url and qdrant_api_key:
            try:
                self.client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                )
            except Exception as e:
                print(f"⚠️ No se pudo conectar a Qdrant: {e}")
                self.client = None
        
        # Inicializar cliente OpenAI para embeddings
        if openai_api_key and OpenAIClientNew is not None:
            try:
                self._openai_client = OpenAIClientNew(api_key=openai_api_key)
            except Exception:
                self._openai_client = None
    
    def is_available(self) -> bool:
        """Verifica si Qdrant está disponible y configurado."""
        return self.client is not None and self._openai_client is not None
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Genera embedding usando OpenAI."""
        if self._openai_client is None:
            return None
        
        try:
            response = self._openai_client.embeddings.create(
                model=self._embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"⚠️ Error generando embedding: {e}")
            return None
    
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Busca documentos relevantes en Qdrant basándose en la consulta.
        
        Args:
            query: Texto de consulta del usuario
            limit: Número máximo de resultados a retornar
            
        Returns:
            Lista de documentos relevantes con su contenido y score
        """
        if not self.is_available():
            return []
        
        # Generar embedding de la consulta
        query_vector = self._get_embedding(query)
        if query_vector is None:
            return []
        
        try:
            # Buscar en Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            # Formatear resultados
            results = []
            for hit in search_result:
                results.append({
                    "content": hit.payload.get("text", ""),
                    "metadata": hit.payload.get("metadata", {}),
                    "score": hit.score
                })
            
            return results
        except Exception as e:
            print(f"⚠️ Error buscando en Qdrant: {e}")
            return []
    
    def get_context(self, query: str, limit: int = 3) -> str:
        """Obtiene contexto relevante de Qdrant formateado como texto.
        
        Args:
            query: Texto de consulta del usuario
            limit: Número máximo de resultados
            
        Returns:
            Contexto formateado como string
        """
        results = self.search(query, limit)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Contexto {i}] {result['content']}")
        
        return "\n\n".join(context_parts)
