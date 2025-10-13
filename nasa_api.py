import requests
import pandas as pd
import calendar

PROVINCIAS_COORDS = {
    "Buenos Aires":  (-39.0, -33.0, -65.0, -57.0),
    "Córdoba":       (-33.5, -31.0, -65.5, -63.0),
    "Santa Fe":      (-33.5, -28.0, -63.5, -59.0),
    "Mendoza":       (-36.0, -32.0, -69.5, -67.0),
    "Salta":         (-25.5, -22.0, -66.5, -63.0),
    "Misiones":      (-28.5, -25.5, -56.5, -53.5),
}

def obtener_datos_precipitacion(provincia: str) -> pd.DataFrame:
    """Obtiene datos de precipitación mensual desde NASA POWER."""
    if provincia not in PROVINCIAS_COORDS:
        raise ValueError(f"Provincia '{provincia}' no reconocida.")
    
    lat_min, lat_max, lon_min, lon_max = PROVINCIAS_COORDS[provincia]

    url = "https://power.larc.nasa.gov/api/temporal/monthly/regional"
    params = {
        "start": 1981,
        "end": 2025,
        "latitude-min": lat_min,
        "latitude-max": lat_max,
        "longitude-min": lon_min,
        "longitude-max": lon_max,
        "community": "ag",
        "parameters": "PRECTOTCORR",
        "format": "json",
        "units": "metric",
        "user": "valentin",
        "header": "true"
    }

    r = requests.get(url, params=params, timeout=30)
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error en la solicitud a NASA POWER: {e}") from e

    try:
        data = r.json()
    except ValueError as e:
        raise RuntimeError(f"Respuesta no JSON de NASA POWER: {r.text[:200]}") from e

    if not isinstance(data, dict):
        raise RuntimeError(f"Respuesta inesperada de NASA POWER (no es un objeto JSON): {type(data)}")

    props = data.get("properties")
    series = None

    if props is not None:
        parameter = props.get("parameter")
        if parameter is None:
            raise RuntimeError(f"La respuesta de NASA POWER no contiene 'parameter' dentro de 'properties'. Respuesta: {str(props)[:500]}")

        series = parameter.get("PRECTOTCORR")
    else:
        features = data.get("features")
        if isinstance(features, list) and len(features) > 0:
            agg = {}
            counts = {}
            for feat in features:
                p = feat.get("properties", {})
                param = p.get("parameter", {})
                s = param.get("PRECTOTCORR") if isinstance(param, dict) else None
                if isinstance(s, dict):
                    for date, val in s.items():
                        if val is None:
                            continue
                        agg[date] = agg.get(date, 0.0) + float(val)
                        counts[date] = counts.get(date, 0) + 1
            if agg:
                series = {d: (agg[d] / counts[d]) for d in agg}

    if series is None:
        raise RuntimeError(f"La serie 'PRECTOTCORR' no está presente en la respuesta de NASA POWER. Respuesta: {str(data)[:500]}")

    df = pd.DataFrame(list(series.items()), columns=["date", "precip_mm_day"])
    df["year"] = df["date"].str[:4].astype(int)
    df["month"] = df["date"].str[4:].astype(int)
    df = df[(df["month"] >= 1) & (df["month"] <= 12)].copy()
    df["days"] = df.apply(lambda r: calendar.monthrange(r["year"], r["month"])[1], axis=1)
    df["precip_mm_month"] = df["precip_mm_day"] * df["days"]
    df["ds"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str) + "-15")
    df["y"] = df["precip_mm_month"]
    return df[["ds", "y"]]
