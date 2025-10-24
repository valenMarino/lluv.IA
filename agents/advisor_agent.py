import re
from typing import Any, Dict, List, Optional, Tuple
from mcp_core import BaseAgent, MCPContext, LLM
from .data_agent import DataAgent
from .analysis_agent import AnalysisAgent
import datetime
import unicodedata

class AdvisorAgent(BaseAgent):
    def __init__(self, context: MCPContext, model: str = "google/flan-t5-base") -> None:
        super().__init__(context)
        self.llm = LLM(model=model)
        self.data_agent = DataAgent(context)
        self.analysis_agent = AnalysisAgent(context)

    def call(self, message: str) -> str:
        intent, args = self._parse_intent(message)
        respuesta_contexto = self._answer_with_context(intent, args)
        # Si no hay cliente LLM disponible, respondemos desde el reporte si existe; sino respuesta natural.
        if getattr(self.llm, 'client', None) is None and getattr(self.llm, '_openai_client', None) is None:
            try:
                rep = self.context.get("reporte_detallado")
            except Exception:
                rep = None
            if isinstance(rep, str) and rep.strip():
                return self._compose_from_report(message, rep)
            return self._compose_answer(respuesta_contexto)
        # Caso con LLM: usar un prompt breve sin eco del usuario
        prompt = self._build_prompt(message, respuesta_contexto)
        salida = self.llm.generate(prompt)
        # Si por alguna razón el LLM no devuelve texto útil, usar respuesta compuesta
        if not salida or len(str(salida).strip()) == 0:
            try:
                rep = self.context.get("reporte_detallado")
            except Exception:
                rep = None
            if isinstance(rep, str) and rep.strip():
                return self._compose_from_report(message, rep)
            return self._compose_answer(respuesta_contexto)
        # Evitar respuestas que repitan instrucciones/prompts
        if self._looks_like_instruction(salida) or self._references_prompt(salida):
            try:
                rep = self.context.get("reporte_detallado")
            except Exception:
                rep = None
            if isinstance(rep, str) and rep.strip():
                return self._compose_from_report(message, rep)
            return self._compose_answer(respuesta_contexto)
        return salida

    def _answer_with_context(self, intent: str, args: Dict[str, Any]) -> Dict[str, Any]:
        hoy = datetime.date.today()
        default_inicio = f"1981-01"
        default_fin = f"{hoy.year}-{hoy.month:02d}"
        if intent == "trend_province":
            provincia = args.get("provincia")
            fecha_inicio = args.get("fecha_inicio") or default_inicio
            fecha_fin = args.get("fecha_fin") or default_fin
            df = self.data_agent.call(provincia, fecha_inicio, fecha_fin)
            resumen = self.analysis_agent.call(provincia, df)
            return {"tipo": intent, "provincia": provincia, "resumen": resumen}
        if intent == "max_rain_province":
            year = args.get("year")
            datos = self.data_agent.ensure_all()
            mejor = self.analysis_agent.provincia_con_mas_lluvia(datos, year=year)
            return {"tipo": intent, "year": year, "mejor": mejor}
        return {"tipo": "desconocido"}

    def _parse_intent(self, message: str) -> Tuple[str, Dict[str, Any]]:
        m = message.lower()
        prov = self._extract_province(m)
        year = self._extract_year(m)
        if ("tendenc" in m or "trend" in m) and prov:
            return ("trend_province", {"provincia": prov})
        if ("más lluvi" in m or "mas lluvi" in m or "most rain" in m):
            return ("max_rain_province", {"year": year})
        if prov:
            return ("trend_province", {"provincia": prov})
        return ("unknown", {})

    def _extract_province(self, text: str) -> Optional[str]:
        from nasa_api import PROVINCIAS_COORDS
        def _normalize(s: str) -> str:
            # Eliminar acentos y normalizar a minúsculas
            s = unicodedata.normalize('NFD', s)
            s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
            return s.lower()
        nt = _normalize(text)
        for p in PROVINCIAS_COORDS.keys():
            if _normalize(p) in nt:
                return p
        return None

    def _extract_year(self, text: str) -> Optional[int]:
        years = re.findall(r"(19\d{2}|20\d{2})", text)
        if years:
            try:
                return int(years[-1])
            except Exception:
                return None
        return None

    def _build_prompt(self, user_message: str, ctx: Dict[str, Any]) -> str:
        # Si existe un reporte detallado en el contexto compartido, usarlo como fuente principal
        try:
            reporte = self.context.get("reporte_detallado")
        except Exception:
            reporte = None
        if isinstance(reporte, str) and len(reporte.strip()) > 0:
            return (
                "Responde en español, breve (2-4 frases) y orientado al agro, usando EXCLUSIVAMENTE "
                "la información del siguiente 'Reporte Climático Detallado'. No repitas el texto "
                "literal, sintetiza y da recomendación práctica. No des información si todavia no tenes el reporte."
                "No des información de otra cosa que no tenga que ver con clima, agro o el reporte."
                f"Reporte:\n{reporte}\n\n"
                f"Pregunta del usuario: {user_message}"
            )
        if ctx.get("tipo") == "trend_province":
            prov = ctx.get("provincia")
            resumen = ctx.get("resumen", {})
            tend = resumen.get("tendencia_precipitaciones", {})
            est = resumen.get("estadisticas", {})
            prom = None
            try:
                prom = est.get("precipitacion", {}).get("promedio_mensual")
            except Exception:
                prom = None
            return (
                f"Redacta una respuesta breve (2-4 frases) en español para público agro. "
                f"Tema: tendencia de precipitaciones en {prov}. "
                f"Datos: tendencia={tend.get('descripcion')}, pendiente={tend.get('pendiente')}, "
                f"promedio_mensual={prom}. Añade una recomendación práctica."
            )
        if ctx.get("tipo") == "max_rain_province":
            mejor = ctx.get("mejor")
            year = ctx.get("year")
            if mejor:
                periodo = f" en {year}" if year else " (series histórica)"
                return (
                    f"Resume en español (2-4 frases): provincia con mayor precipitación{periodo}: "
                    f"{mejor['provincia']} con {mejor['total_mm']:.1f} mm acumulados. Añade una recomendación agrícola."
                )
            return "No se pudo determinar la provincia con más lluvia. Pide aclaraciones o sugiere alternativas."
        return "No hay datos suficientes en el contexto. Pide precisión (provincia y fechas) o sugiere una consulta válida."

    def _compose_answer(self, ctx: Dict[str, Any]) -> str:
        # Genera respuestas naturales sin depender del LLM
        if ctx.get("tipo") == "trend_province":
            prov = ctx.get("provincia")
            resumen = ctx.get("resumen", {})
            tend = resumen.get("tendencia_precipitaciones", {})
            est = resumen.get("estadisticas", {})
            prom = None
            try:
                prom = est.get("precipitacion", {}).get("promedio_mensual")
            except Exception:
                prom = None
            prom_txt = f" El promedio mensual histórico ronda {prom:.1f} mm." if isinstance(prom, (int, float)) and prom is not None else ""
            consejo = " Recomendación: ajustar el manejo de agua y monitorear pronósticos semanales para decisiones de siembra." \
                if tend.get('descripcion') == 'Bajista' else \
                " Recomendación: considerar prácticas de drenaje y control de enfermedades asociadas a exceso de humedad."
            return f"En {prov}, la tendencia de precipitaciones es {tend.get('descripcion').lower()} (pendiente {tend.get('pendiente'):.4f})." + prom_txt + consejo
        if ctx.get("tipo") == "max_rain_province":
            mejor = ctx.get("mejor")
            year = ctx.get("year")
            if mejor:
                periodo = f" en {year}" if year else " en la serie histórica"
                return (
                    f"La provincia con mayor precipitación{periodo} es {mejor['provincia']} con "
                    f"{mejor['total_mm']:.1f} mm acumulados. Sugerencia: priorizar cultivos tolerantes a humedad y asegurar buen drenaje."
                )
            return "No pude determinar cuál fue la provincia con más lluvias; indicá el año o intentá nuevamente."
        return "Indicá provincia y (opcionalmente) un rango de fechas para analizar la tendencia de lluvias."

    def _compose_from_report(self, user_message: str, reporte: str) -> str:
        # Extrae secciones clave del reporte y arma 2-4 frases concisas
        try:
            lines = [l.strip() for l in (reporte or "").splitlines()]
        except Exception:
            lines = []
        pred_prom = pred_max = pred_min = tendencia = None
        alerta = None
        # Buscar sección de Predicción Futura
        in_pred = False
        for l in lines:
            if l.upper().startswith("🔮") or "PREDICCIÓN FUTURA" in l.upper():
                in_pred = True
                continue
            if in_pred and l.startswith("⚠"):
                in_pred = False
            if in_pred:
                m1 = re.search(r"promedio\s+predich[oa]:\s*([0-9]+\.?[0-9]*)\s*mm", l, re.IGNORECASE)
                if m1:
                    try:
                        pred_prom = float(m1.group(1))
                    except Exception:
                        pass
                m2 = re.search(r"[Mm]áximo\s+predich[oa]:\s*([0-9]+\.?[0-9]*)\s*mm", l)
                if m2:
                    try:
                        pred_max = float(m2.group(1))
                    except Exception:
                        pass
                m3 = re.search(r"[Mm]ínimo\s+predich[oa]:\s*([0-9]+\.?[0-9]*)\s*mm", l)
                if m3:
                    try:
                        pred_min = float(m3.group(1))
                    except Exception:
                        pass
                if "tendencia" in l.lower():
                    tendencia = l.split(":", 1)[-1].strip()
        # Buscar primera alerta/recomendación
        in_alert = False
        for l in lines:
            if l.startswith("⚠") or "ALERTAS" in l.upper():
                in_alert = True
                continue
            if in_alert and l:
                alerta = l
                break
        partes = []
        if tendencia:
            partes.append(f"Tendencia prevista: {tendencia}.")
        if pred_prom is not None:
            partes.append(f"Promedio esperado ~{pred_prom:.1f} mm/mes")
        if pred_max is not None and pred_min is not None:
            partes.append(f"Rango {pred_min:.1f}-{pred_max:.1f} mm/mes")
        if alerta:
            partes.append(f"Recomendación: {alerta}")
        if not partes:
            # Si no se pudo extraer, devolver resumen acotado del reporte
            resumen = " ".join(lines[:6])[:280]
            return f"Según el reporte: {resumen}"
        return " ".join(partes)

    def _looks_like_instruction(self, text: str) -> bool:
        t = (text or "").strip().lower()
        patterns = [
            "redacta una respuesta",
            "responde en español",
            "usuario pregunta",
            "contexto:",
            "añade una recomendación",
            "anade una recomendación",
            "promedio_mensual=",
            "tendencia=",
        ]
        return any(p in t for p in patterns)

    def _references_prompt(self, text: str) -> bool:
        # Detecta si el modelo devolvió parte literal del prompt
        t = (text or "").strip().lower()
        return "usuario pregunta" in t or "contexto" in t
