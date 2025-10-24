from typing import Dict, Any, Optional
from mcp_core import BaseAgent, MCPContext
import pandas as pd
import numpy as np

from utils import calcular_estadisticas_climaticas

class AnalysisAgent(BaseAgent):
    """Calcula tendencias y promedios de precipitaciones y comparativos entre provincias."""
    def __init__(self, context: MCPContext) -> None:
        super().__init__(context)
        self.ns_stats = self.context.ensure_namespace('analysis')

    def call(self, provincia: str, df: pd.DataFrame) -> Dict[str, Any]:
        key = provincia
        if key in self.ns_stats:
            return self.ns_stats[key]
        stats = calcular_estadisticas_climaticas(df)
        tendencia = self._tendencia_precipitaciones(df)
        acumulados = self._acumulado_por_anio(df)
        resumen = {
            'provincia': provincia,
            'tendencia_precipitaciones': tendencia,
            'acumulados_anuales': acumulados,
            'estadisticas': stats,
        }
        self.ns_stats[key] = resumen
        return resumen

    def _tendencia_precipitaciones(self, df: pd.DataFrame) -> Dict[str, Any]:
        d = df.dropna(subset=['ds', 'y']).copy()
        if d.empty:
            return {'pendiente': 0.0, 'descripcion': 'Sin datos suficientes'}
        # Convertir fechas a días desde el inicio para regresión lineal simple
        x = (d['ds'] - d['ds'].min()).dt.days.values.astype(float)
        y = d['y'].values.astype(float)
        if len(x) < 2:
            return {'pendiente': 0.0, 'descripcion': 'Serie muy corta'}
        slope = float(np.polyfit(x, y, 1)[0])
        if abs(slope) < 1e-6:
            desc = 'Lateral'
        else:
            desc = 'Alcista' if slope > 0 else 'Bajista'
        return {'pendiente': slope, 'descripcion': desc}

    def _acumulado_por_anio(self, df: pd.DataFrame) -> Dict[int, float]:
        d = df.dropna(subset=['ds', 'y']).copy()
        if d.empty:
            return {}
        d['year'] = d['ds'].dt.year
        totales = d.groupby('year')['y'].sum().to_dict()
        return {int(k): float(v) for k, v in totales.items()}

    def provincia_con_mas_lluvia(self, datos: Dict[str, pd.DataFrame], year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Devuelve la provincia con mayor precipitación acumulada en el año indicado o global."""
        mejor: Optional[Dict[str, Any]] = None
        for prov, df in datos.items():
            d = df.dropna(subset=['ds', 'y']).copy()
            if d.empty:
                continue
            if year is not None:
                d = d[d['ds'].dt.year == year]
            total = float(d['y'].sum()) if not d.empty else 0.0
            if (mejor is None) or (total > mejor['total_mm']):
                mejor = {'provincia': prov, 'total_mm': total}
        return mejor
