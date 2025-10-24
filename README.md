# Lluv.IA – Análisis Meteorológico Inteligente

**Plataforma integral de análisis climático** para el sector agropecuario argentino, que combina datos satelitales de NASA con inteligencia artificial para generar predicciones y análisis meteorológicos detallados.

## Características Principales

### 🗺️ **Cobertura Nacional Completa**
- **24 provincias argentinas** + CABA
- Datos históricos desde 1981 hasta 2025
- Análisis regional por coordenadas geográficas precisas

### **Análisis Meteorológico Integral**
- **Precipitaciones**: Histórico, predicciones y tendencias
- **Temperatura**: Promedio, máximas y mínimas
- **Humedad relativa**: Análisis de condiciones atmosféricas
- **Análisis estacional**: Comparativas por estaciones del año

### **Visualizaciones Avanzadas**
- Gráficos interactivos con **Plotly**
- Comparativos anuales de los últimos 5 años
- Intervalos de confianza en predicciones
- Interfaz moderna con tema oscuro optimizado

### **Inteligencia Artificial**
- Modelo **Prophet** (Facebook) para predicciones a 24 meses
- Análisis de tendencias y patrones estacionales
- Alertas automáticas de riesgo climático
- Recomendaciones agronómicas personalizadas

## Tecnologías Utilizadas
- **Python 3.8+**
- **Prophet** (modelo de predicción temporal)
- **Gradio 4.0+** (interfaz web moderna)
- **NASA POWER API** (datos satelitales)
- **Plotly** (visualizaciones interactivas)
- **Pandas** (procesamiento de datos)

## Estructura del Proyecto
```
lluv.IA/
├── nasa_api.py          # API NASA POWER + procesamiento de datos
├── forecast_model.py    # Modelos de predicción con Prophet
├── ui.py               # Interfaz Gradio moderna
├── utils.py            # Visualizaciones y análisis estadístico
├── main.py             # Punto de entrada
├── requirements.txt    # Dependencias del proyecto
└── README.md          # Documentación
```

## Funcionalidades

### **Reportes Climáticos Detallados**
- Resumen ejecutivo con métricas clave
- Análisis de variabilidad climática
- Comparaciones con promedios históricos
- Alertas de riesgo (sequía/exceso hídrico)

### **Predicciones Inteligentes**
- Proyecciones a 24 meses
- Intervalos de confianza del 80%
- Tendencias estacionales
- Clasificación de períodos (normal/húmedo/seco)

### **Cobertura Geográfica**
**Región Pampeana**: Buenos Aires, Córdoba, Santa Fe, Entre Ríos, La Pampa
**NOA**: Salta, Jujuy, Tucumán, Santiago del Estero, Catamarca, La Rioja  
**NEA**: Misiones, Corrientes, Chaco, Formosa
**Cuyo**: Mendoza, San Juan, San Luis
**Patagonia**: Neuquén, Río Negro, Chubut, Santa Cruz, Tierra del Fuego
**CABA**: Ciudad Autónoma de Buenos Aires

## Instalación y Uso

### Requisitos Previos
```bash
Python 3.8+
pip (gestor de paquetes)
```

### Instalación con Entorno Virtual (Recomendado)
```bash
# Clonar el repositorio
git clone [URL_DEL_REPO]
cd lluv.IA

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# Instalar dependencias en el entorno virtual
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

### Instalación Directa (Sin entorno virtual)
```bash
# Clonar el repositorio
git clone [URL_DEL_REPO]
cd lluv.IA

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

## Interfaz de Usuario

### **Diseño Moderno**
- Tema oscuro optimizado para uso prolongado
- Gradientes y efectos visuales modernos
- Tipografía clara y legible
- Responsive design

### **Experiencia de Usuario**
- Navegación intuitiva por pestañas
- Controles interactivos (checkboxes, dropdowns)
- Tooltips informativos
- Botón de copia para reportes

## Métricas y Análisis

### **Estadísticas Calculadas**
- Promedio anual y mensual de precipitaciones
- Coeficiente de variación climática
- Amplitud térmica
- Análisis estacional detallado

### **Sistema de Alertas**
- **🔴 Riesgo Alto**: Regiones áridas (<500mm/año)
- **🟡 Variabilidad Alta**: Clima impredecible (>50% CV)
- **🔵 Riesgo Hídrico**: Exceso de precipitaciones (>1500mm/año)

## Objetivo y Aplicaciones

### **Sector Agropecuario**
- Planificación de campañas agrícolas
- Selección de cultivos según el clima
- Optimización de sistemas de riego
- Prevención de pérdidas por eventos climáticos

### **Institucional**
- Políticas públicas agropecuarias
- Investigación climática
- Planificación territorial
- Gestión de riesgos

## Fuentes de Datos
- **NASA POWER**: Datos satelitales y de reanálisis
- **Resolución temporal**: Mensual (1981-2025)
- **Resolución espacial**: Regional por provincia
- **Parámetros**: PRECTOTCORR, T2M, RH2M, T2M_MAX, T2M_MIN

## Licencia
Este proyecto está desarrollado para el sector agropecuario argentino con fines educativos y de investigación.

---

