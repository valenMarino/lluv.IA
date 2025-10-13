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

    r = requests.get(url, params=params)
    data = r.json()
    series = data["properties"]["parameter"]["PRECTOTCORR"]

    df = pd.DataFrame(list(series.items()), columns=["date", "precip_mm_day"])
    df["year"] = df["date"].str[:4].astype(int)
    df["month"] = df["date"].str[4:].astype(int)
    df["days"] = df.apply(lambda r: calendar.monthrange(r["year"], r["month"])[1], axis=1)
    df["precip_mm_month"] = df["precip_mm_day"] * df["days"]
    df["ds"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str) + "-15")
    df["y"] = df["precip_mm_month"]
    return df[["ds", "y"]]
