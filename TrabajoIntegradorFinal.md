# Trabajo Integrador Final — Recomendador de riego

**Última actualización:** 27/10/2025

---

## 1. Resumen

`Recomendador de riego` es un MVP desarrollado para el sector agropecuario que facilita la toma de decisiones sobre riego y manejo a partir de datos climáticos y modelos predictivos. El sistema:

- Descarga datos climáticos mensuales (NASA POWER) por provincia/punto.
  [https://power.larc.nasa.gov/api/pages/?urls.primaryName=Monthly%20%26%20Annual#/Data%20Requests/monthly_single_point_data_request_api_temporal_monthly_point_get]
- Genera series históricas y predicciones a 24 meses con Prophet.
  [https://facebook.github.io/prophet/]
- Produce informes automáticos (texto y gráficos interactivos).
- Ofrece un asistente conversacional (LLM) que utiliza el informe como contexto para entregar recomendaciones prácticas en español
  [https://huggingface.co/google/flan-t5-base]
  [https://platform.openai.com/docs/models/gpt-5-mini]
  
La interfaz de usuario de la demo está implementada con Gradio y permite seleccionar provincia y rango de fechas, visualizar históricos y predicciones, consultar un chat contextual y exportar reportes.

## 2. Declaración del MVP

Mi MVP permite que productores y técnicos agrónomos consulten historial y predicción de precipitaciones por provincia y obtengan recomendaciones prácticas de riego y manejo de forma rápida y accesible. Se apoya en datos oficiales (NASA POWER), en Prophet para forecasting y en un LLM para contextualizar y traducir el análisis en acciones concretas.

## 3. Problema y usuarios objetivo

- **Problema:** falta de acceso sencillo a predicciones climáticas interpretadas para la toma de decisiones operativas (riego, siembra, manejo de cultivo).
- **Usuarios:** productores pequeños/medianos, técnicos asesores.
- **Casos de uso:** planificación estacional, ajuste de riego, diagnóstico rápido desde oficina o campo.

## 4. Funcionalidades principales

- **Entrada:** selector de provincia y periodo (desde / hasta).
- **Obtención de datos:** consulta mensual de variables climáticas (precipitación, temperatura, etc.) desde NASA POWER.
- **Modelado:** ajuste y forecast con Prophet (horizonte 24 meses).
- **Salidas:**
	- Gráficos interactivos (histórico y predicción) y tablas resumen.
	- Informe textual automático con métricas clave, rangos y alertas.
	- Chat contextual (LLM) que responde preguntas prácticas basadas en el informe.
- **Arquitectura interna:** diseño modular por agentes (DataAgent, AnalysisAgent, AdvisorAgent) y la clase `LLM` que encapsula la lógica (OpenAI / Hugging Face).

## 5. Stack tecnológico (actual en el repositorio)

- **Interfaz:** Gradio
- **Lenguaje:** Python 3.10+
- **Series temporales:** Prophet (fbprophet / prophet)
- **Visualización:** Plotly
- **LLM:** Hugging Face Inference (`google/flan-t5-base` por defecto) o OpenAI (si `OPENAI_API_KEY` está presente)
- **Despliegue recomendado:** Hugging Face Spaces

## 6. Integración del LLM (breve técnico)

- **Clase central:** `mcp_core.LLM`
	- Prioridad de backends: OpenAI (`OPENAI_API_KEY`) → Hugging Face Inference (`HF_TOKEN`) → fallback.
	- Modelo HF por defecto: `google/flan-t5-base` (configurable).
- **AdvisorAgent:** construye prompts que contienen el informe y solicita respuestas en español con estructura orientada a recomendaciones (4–7 viñetas con acciones y riesgos).

## 7. Arquitectura (visión general)

```
UI (Gradio)
	↕
Agentes (AdvisorAgent, DataAgent, AnalysisAgent)
	↕
Servicios / Módulos:
- nasa_api.py       # descarga y parseo de datos
- forecast_model.py # wrapper Prophet y forecast
- mcp_core.py       # LLM wrapper y lógica de prompting
- agents/           # implementación de agentes
- gdrive_helper.py  # export a Drive / Docs
```

## 8. Ejemplo de prompt

```
Sos un experto en agricultura de precisión. Tenés el siguiente informe climático para la provincia X: [INFORME].
¿Qué recomendaciones prácticas de riego proponés para la próxima estación? Responde en 4-6 viñetas, indicando prioridades y riesgos.
```

## 9. Instalación y ejecución local (Windows / PowerShell)

**Requisitos:** Python 3.10+, Git

```powershell
git clone https://github.com/valenMarino/recomendador-de-riego
cd recomendador-de-riego

# crear y activar entorno
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# ejecutar la app (Gradio)
python main.py
# o: python app.py  # según entrypoint del repo
```

## 10. Variables de entorno relevantes

- `HF_TOKEN` / `HUGGINGFACEHUB_API_TOKEN` — token Hugging Face (opcional).
- `OPENAI_API_KEY` — clave OpenAI (opcional).
- `OPENAI_MODEL` — modelo OpenAI a usar (ej. `gpt-4o-mini`).
- `GDRIVE_SA_JSON` — ruta o JSON crudo de Service Account (opcional).
- `GDRIVE_OAUTH_JSON` — ruta o JSON de client_secrets (opcional).

## 11. Despliegue (resumen)

**Hugging Face Spaces (recomendado):** crear Space tipo Gradio, subir repo y configurar secrets.


## 13. Checklist de entrega

- [ si ] Código en GitHub (branch final)
- [ si ] `README.md` completo y claro (este documento)
- [ si ] App ejecutable localmente (probada)
- [ si ] App desplegada públicamente (HF Space o Docker con URL)
- [    ] Demo breve (video 2–3 min) o script de demostración

## 14. Ideas de mejora (post-entrega)

- Integrar RAG con documentos INTA/SENASA y vector store para respuestas citadas.

## 15. Autor y contacto

- Repo: [https://github.com/valenMarino/recomendador-de-riego]
