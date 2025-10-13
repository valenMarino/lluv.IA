from prophet import Prophet
import pandas as pd

def predecir_precipitacion(df: pd.DataFrame) -> pd.DataFrame:
    """Entrena modelo Prophet y genera predicción a 24 meses."""
    modelo = Prophet(yearly_seasonality=True)
    modelo.fit(df)
    futuro = modelo.make_future_dataframe(periods=24, freq='M')
    forecast = modelo.predict(futuro)
    return forecast
