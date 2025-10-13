# 🌾 Lluv.IA – Predicción Inteligente de Precipitaciones

Proyecto de IA aplicado al sector agro, que analiza y predice la precipitación mensual histórica (1981–2025) en distintas provincias argentinas, usando datos reales de la API de NASA POWER.

## 🚀 Tecnologías utilizadas
- **Python**
- **Prophet** (modelo de predicción temporal)
- **Gradio** (interfaz gráfica)
- **NASA POWER API** (fuente de datos)
- **Pandas / Plotly** (análisis y visualización)

## 📦 Estructura del proyecto
- `nasa_api.py` → conexión y procesamiento de datos desde NASA
- `forecast_model.py` → entrenamiento y predicción con Prophet
- `ui.py` → interfaz Gradio
- `main.py` → punto de entrada del sistema
- `utils.py` → funciones auxiliares (conversión, gráficos, etc.)

## 🧠 Objetivo
Analizar tendencias de lluvia y predecir riesgos de sequía o exceso hídrico, ayudando a productores agrícolas a planificar mejor sus campañas.

---
