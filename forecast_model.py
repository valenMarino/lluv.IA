import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

try:
    from prophet import Prophet  # type: ignore
    _PROPHET_AVAILABLE = True
except Exception:
    # Prophet puede no estar instalado o fallar al importar por dependencias (pystan/cmdstanpy)
    _PROPHET_AVAILABLE = False

logger = logging.getLogger(__name__)

def predecir_precipitacion(df: pd.DataFrame) -> pd.DataFrame:
    """Genera predicción de precipitaciones a 24 meses usando Prophet si está disponible.

    Fallback: modelo simple (tendencia lineal + promedio mensual) si hay pocos datos (<12)
    o si Prophet no está disponible.
    """
    # Normalizar columnas esperadas
    if 'ds' not in df.columns or 'y' not in df.columns:
        logger.warning("predecir_precipitacion: columnas faltantes; se esperaban ['ds','y'].")
        return pd.DataFrame(columns=['ds', 'yhat', 'yhat_lower', 'yhat_upper'])

    data = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(data['ds']):
        data['ds'] = pd.to_datetime(data['ds'])

    # Fallback temprano si datos insuficientes
    if data.empty or len(data) < 12 or not _PROPHET_AVAILABLE:
        motivo = []
        if data.empty:
            motivo.append('data.empty')
        if len(data) < 12:
            motivo.append(f'datos_insuficientes({len(data)})')
        if not _PROPHET_AVAILABLE:
            motivo.append('prophet_no_disponible')
        logger.info("predecir_precipitacion: usando fallback simple (%s)", ",".join(motivo))
        last_date = data['ds'].max() if not data.empty else datetime.now()
        future_dates = pd.date_range(start=last_date, periods=25, freq='M')[1:]
        mean_y = data['y'].mean() if not data.empty else 0.0
        forecast = pd.DataFrame({
            'ds': future_dates,
            'yhat': [mean_y] * 24,
            'yhat_lower': [max(0.0, mean_y * 0.7)] * 24,
            'yhat_upper': [max(0.0, mean_y * 1.3)] * 24
        })
        return forecast

    # Intento con Prophet
    try:
        # Prophet maneja estacionalidad anual por defecto; los datos son mensuales
        model = Prophet(yearly_seasonality=True,
                        weekly_seasonality=False,
                        daily_seasonality=False,
                        seasonality_mode='additive')
        model.fit(data[['ds', 'y']])

        # Generar 24 meses futuros (fin de mes)
        future = model.make_future_dataframe(periods=24, freq='M', include_history=False)
        fcst = model.predict(future)

        forecast = fcst[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        # Aseguramos no-negatividad para precipitación
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)
        logger.info("predecir_precipitacion: Prophet utilizado con %d observaciones y 24 meses futuros.", len(data))
        return forecast
    except Exception as e:
        # Si Prophet falla por cualquier motivo, usar el fallback simple
        logger.exception("predecir_precipitacion: error con Prophet; usando fallback simple. Detalle: %s", e)
        df_sorted = data.sort_values('ds').copy()
        df_sorted['month'] = df_sorted['ds'].dt.month
        monthly_avg = df_sorted.groupby('month')['y'].mean()
        x = np.arange(len(df_sorted))
        y_vals = df_sorted['y'].values
        trend_slope = np.polyfit(x, y_vals, 1)[0] if len(y_vals) > 1 else 0.0

        last_date = df_sorted['ds'].max()
        future_dates = pd.date_range(start=last_date, periods=25, freq='M')[1:]

        predictions = []
        for i, future_date in enumerate(future_dates):
            month = future_date.month
            base_value = monthly_avg.get(month, df_sorted['y'].mean())
            predicted_value = max(0.0, base_value + trend_slope * (i + 1))
            predictions.append(predicted_value)

        std_dev = df_sorted['y'].std() if len(df_sorted) > 1 else (df_sorted['y'].mean() * 0.2 if len(df_sorted) else 0.0)
        lower_bound = [max(0.0, pred - 1.5 * (std_dev if not np.isnan(std_dev) else 0.0)) for pred in predictions]
        upper_bound = [pred + 1.5 * (std_dev if not np.isnan(std_dev) else 0.0) for pred in predictions]

        forecast = pd.DataFrame({
            'ds': future_dates,
            'yhat': predictions,
            'yhat_lower': lower_bound,
            'yhat_upper': upper_bound
        })
        return forecast
