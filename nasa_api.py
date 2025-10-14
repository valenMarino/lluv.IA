import requests
import pandas as pd
import calendar

PROVINCIAS_COORDS = {
    # Región Pampeana
    "Buenos Aires":     (-39.0, -33.0, -65.0, -57.0),
    "Córdoba":          (-33.5, -31.0, -65.5, -63.0),
    "Santa Fe":         (-33.5, -28.0, -63.5, -59.0),
    "Entre Ríos":       (-33.8, -30.1, -60.8, -57.8),
    "La Pampa":         (-38.9, -35.0, -68.3, -63.5),
    
    # Región Noroeste (NOA)
    "Salta":            (-25.5, -22.0, -66.5, -63.0),
    "Jujuy":            (-24.6, -21.8, -67.2, -64.3),
    "Tucumán":          (-27.9, -26.0, -66.2, -64.4),
    "Santiago del Estero": (-29.9, -25.8, -65.5, -61.2),
    "Catamarca":        (-29.4, -25.2, -69.0, -65.2),
    "La Rioja":         (-31.4, -28.8, -69.8, -66.2),
    
    # Región Noreste (NEA)
    "Misiones":         (-28.5, -25.5, -56.5, -53.5),
    "Corrientes":       (-30.8, -27.3, -59.8, -55.7),
    "Chaco":            (-27.6, -24.1, -63.2, -58.9),
    "Formosa":          (-26.9, -22.9, -62.4, -57.6),
    
    # Región Cuyo
    "Mendoza":          (-37.6, -32.0, -70.3, -66.9),
    "San Juan":         (-32.5, -28.8, -70.1, -66.8),
    "San Luis":         (-34.3, -32.1, -67.5, -64.2),
    
    # Región Patagónica
    "Neuquén":          (-41.1, -36.0, -71.9, -68.0),
    "Río Negro":        (-42.0, -37.5, -71.9, -62.8),
    "Chubut":           (-46.4, -42.0, -73.6, -65.1),
    "Santa Cruz":       (-52.4, -46.4, -73.6, -65.6),
    "Tierra del Fuego": (-55.1, -52.4, -68.6, -63.8),
    
    # Ciudad Autónoma
    "CABA":             (-34.7, -34.5, -58.6, -58.3),
}

def _hacer_solicitud_nasa(params: dict) -> dict:
    """Realiza solicitud HTTP a la API de NASA POWER."""
    url = "https://power.larc.nasa.gov/api/temporal/monthly/regional"
    r = requests.get(url, params=params, timeout=30)
    
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error en la solicitud a NASA POWER: {e}") from e
    
    try:
        return r.json()
    except ValueError as e:
        raise RuntimeError(f"Respuesta no JSON de NASA POWER: {r.text[:200]}") from e

def _extraer_series_parametro(data: dict, parametro: str) -> dict:
    """Extrae serie de datos de un parámetro específico."""
    if not isinstance(data, dict):
        raise RuntimeError(f"Respuesta inesperada de NASA POWER: {type(data)}")
    
    # Intentar extraer desde properties
    props = data.get("properties")
    if props is not None:
        parameter = props.get("parameter")
        if parameter and parametro in parameter:
            return parameter[parametro]
    
    # Intentar extraer desde features (respuesta regional)
    features = data.get("features")
    if isinstance(features, list) and len(features) > 0:
        return _promediar_features(features, parametro)
    
    raise RuntimeError(f"No se encontró el parámetro '{parametro}' en la respuesta")

def _promediar_features(features: list, parametro: str) -> dict:
    """Promedia valores de múltiples features para un parámetro."""
    agg = {}
    counts = {}
    
    for feat in features:
        p = feat.get("properties", {})
        param = p.get("parameter", {})
        s = param.get(parametro) if isinstance(param, dict) else None
        
        if isinstance(s, dict):
            for date, val in s.items():
                if val is not None:
                    agg[date] = agg.get(date, 0.0) + float(val)
                    counts[date] = counts.get(date, 0) + 1
    
    return {d: (agg[d] / counts[d]) for d in agg if counts[d] > 0}

def _procesar_datos_climaticos_separados(parametros_datos: dict) -> pd.DataFrame:
    """Procesa datos climáticos obtenidos por separado."""
    # Usar precipitación como base (es el más importante)
    precipitacion_data = parametros_datos.get('PRECTOTCORR', {})
    
    if not precipitacion_data:
        raise RuntimeError("No se pudieron obtener datos de precipitación")
    
    # Crear DataFrame base con fechas de precipitación
    fechas = list(precipitacion_data.keys())
    df = pd.DataFrame({'date': fechas})
    
    # Mapear nombres de parámetros
    mapeo_parametros = {
        'PRECTOTCORR': 'precipitacion',
        'T2M': 'temperatura', 
        'RH2M': 'humedad',
        'T2M_MAX': 'temp_max',
        'T2M_MIN': 'temp_min'
    }
    
    # Agregar cada parámetro disponible
    for param_api, param_nombre in mapeo_parametros.items():
        serie = parametros_datos.get(param_api, {})
        df[param_nombre] = [serie.get(fecha, None) for fecha in fechas]
    
    # Procesar fechas y calcular precipitación mensual
    df["year"] = df["date"].str[:4].astype(int)
    df["month"] = df["date"].str[4:].astype(int)
    df = df[(df["month"] >= 1) & (df["month"] <= 12)].copy()
    
    # Solo calcular días y precipitación mensual si tenemos datos de precipitación
    if 'precipitacion' in df.columns and df['precipitacion'].notna().any():
        df["days"] = df.apply(lambda r: calendar.monthrange(r["year"], r["month"])[1], axis=1)
        df["precip_mm_month"] = df["precipitacion"] * df["days"]
        df["y"] = df["precip_mm_month"]
    else:
        df["y"] = 0  # Valor por defecto
    
    df["ds"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str) + "-15")
    
    return df

def obtener_datos_meteorologicos(provincia: str, fecha_inicio: str = None, fecha_fin: str = None) -> pd.DataFrame:
    """Obtiene datos meteorológicos completos desde NASA POWER con peticiones separadas."""
    if provincia not in PROVINCIAS_COORDS:
        raise ValueError(f"Provincia '{provincia}' no reconocida.")
    
    lat_min, lat_max, lon_min, lon_max = PROVINCIAS_COORDS[provincia]
    
    # Procesar fechas
    if fecha_inicio:
        año_inicio = int(fecha_inicio.split('-')[0])
    else:
        año_inicio = 1981
        
    if fecha_fin:
        año_fin = int(fecha_fin.split('-')[0])
    else:
        año_fin = 2025
    
    # Parámetros base para todas las peticiones
    base_params = {
        "start": año_inicio,
        "end": año_fin,
        "latitude-min": lat_min,
        "latitude-max": lat_max,
        "longitude-min": lon_min,
        "longitude-max": lon_max,
        "community": "ag",
        "format": "json",
        "units": "metric",
        "user": "valentin",
        "header": "true"
    }
    
    # Hacer peticiones separadas para cada parámetro
    parametros_datos = {}
    parametros_lista = ["PRECTOTCORR", "T2M", "RH2M", "T2M_MAX", "T2M_MIN"]
    
    for parametro in parametros_lista:
        try:
            params = base_params.copy()
            params["parameters"] = parametro
            
            data = _hacer_solicitud_nasa(params)
            serie = _extraer_series_parametro(data, parametro)
            parametros_datos[parametro] = serie
            
        except Exception as e:
            print(f"⚠️ Error obteniendo {parametro}: {e}")
            # Si falla un parámetro, continuamos con los otros
            parametros_datos[parametro] = {}
    
    return _procesar_datos_climaticos_separados(parametros_datos)

def obtener_datos_precipitacion(provincia: str, fecha_inicio: str = None, fecha_fin: str = None) -> pd.DataFrame:
    """Obtiene solo datos de precipitación para compatibilidad."""
    df_completo = obtener_datos_meteorologicos(provincia, fecha_inicio, fecha_fin)
    return df_completo[["ds", "y"]]
