import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def predecir_precipitacion(df: pd.DataFrame) -> pd.DataFrame:
    """Genera predicción simple basada en tendencias históricas a 24 meses."""
    if df.empty or len(df) < 12:
        # Si no hay suficientes datos, crear predicción básica
        last_date = df['ds'].max() if not df.empty else datetime.now()
        future_dates = pd.date_range(start=last_date, periods=25, freq='M')[1:]
        forecast = pd.DataFrame({
            'ds': future_dates,
            'yhat': [df['y'].mean() if not df.empty else 0] * 24,
            'yhat_lower': [df['y'].mean() * 0.7 if not df.empty else 0] * 24,
            'yhat_upper': [df['y'].mean() * 1.3 if not df.empty else 0] * 24
        })
        return forecast
    
    # Calcular tendencia y estacionalidad básica
    df_sorted = df.sort_values('ds').copy()
    df_sorted['month'] = df_sorted['ds'].dt.month
    
    # Calcular promedio mensual histórico
    monthly_avg = df_sorted.groupby('month')['y'].mean()
    
    # Calcular tendencia lineal simple
    x = np.arange(len(df_sorted))
    y = df_sorted['y'].values
    if len(y) > 1:
        trend_slope = np.polyfit(x, y, 1)[0]
    else:
        trend_slope = 0
    
    # Generar fechas futuras
    last_date = df_sorted['ds'].max()
    future_dates = pd.date_range(start=last_date, periods=25, freq='M')[1:]
    
    # Crear predicciones
    predictions = []
    for i, future_date in enumerate(future_dates):
        month = future_date.month
        base_value = monthly_avg[month]
        
        # Aplicar tendencia
        trend_adjustment = trend_slope * (i + 1)
        predicted_value = base_value + trend_adjustment
        
        # Asegurar que no sea negativo
        predicted_value = max(0, predicted_value)
        
        predictions.append(predicted_value)
    
    # Crear intervalos de confianza simples
    std_dev = df_sorted['y'].std() if len(df_sorted) > 1 else df_sorted['y'].mean() * 0.2
    lower_bound = [max(0, pred - 1.5 * std_dev) for pred in predictions]
    upper_bound = [pred + 1.5 * std_dev for pred in predictions]
    
    forecast = pd.DataFrame({
        'ds': future_dates,
        'yhat': predictions,
        'yhat_lower': lower_bound,
        'yhat_upper': upper_bound
    })
    
    return forecast
