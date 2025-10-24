from typing import Dict, Any, Optional, Tuple
from mcp_core import BaseAgent, MCPContext
from nasa_api import obtener_datos_meteorologicos, PROVINCIAS_COORDS
import pandas as pd

class DataAgent(BaseAgent):
    """Obtiene datos de NASA POWER por provincia y rango de fechas.
    Guarda en el contexto bajo la clave 'data' con índice (provincia, inicio, fin).
    """
    def __init__(self, context: MCPContext) -> None:
        super().__init__(context)
        self.cache = self.context.ensure_namespace('data')

    def _key(self, provincia: str, fecha_inicio: Optional[str], fecha_fin: Optional[str]) -> Tuple[str, Optional[str], Optional[str]]:
        return (provincia, fecha_inicio, fecha_fin)

    def call(self, provincia: str, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> pd.DataFrame:
        if provincia not in PROVINCIAS_COORDS:
            raise ValueError(f"Provincia no reconocida: {provincia}")
        key = self._key(provincia, fecha_inicio, fecha_fin)
        if key in self.cache:
            return self.cache[key]
        df = obtener_datos_meteorologicos(provincia, fecha_inicio, fecha_fin)
        # Normalizar tipos
        if not pd.api.types.is_datetime64_any_dtype(df['ds']):
            df['ds'] = pd.to_datetime(df['ds'])
        self.cache[key] = df
        return df

    def ensure_all(self, provincias: Optional[list] = None, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        provincias = provincias or list(PROVINCIAS_COORDS.keys())
        result: Dict[str, pd.DataFrame] = {}
        for p in provincias:
            result[p] = self.call(p, fecha_inicio, fecha_fin)
        return result
