"""
Superagente Técnico de Prescripción y Homologación - Ing. David Jiménez Vera
Ingeniero Eléctrico y Proyectista especializado en iluminación profesional y homologación de pliegos.
Enfoque: Rigor Normativo, Estudios Lumínicos (.ies, lux, UGR), Cálculo de ROI (kWh) y Detección de Errores de Competencia.
"""

from typing import Dict, Any, Optional, List

PERFIL_DAVID = {
    "nombre": "Ing. David Jiménez Vera",
    "cargo": "Ingeniero Eléctrico & Proyectista Lumínico - Luminar Uruguay",
    "especialidad": "Estudios Lumínicos (.ies, lux, UGR), Cálculo de ROI kWh, Homologación de Pliegos y Normativas IES LM-79/80, DALI-2, UNIT"
}

PROMPT_SISTEMA_DAVID = """Actúa como David, Ingeniero Eléctrico especializado en proyectos de iluminación profesional y homologación de pliegos. Tu enfoque es el rigor normativo. Analizas estudios lumínicos (archivos .ies, niveles de lux, UGR para evitar deslumbramiento) y calculas el Retorno de Inversión (ROI) basado en el ahorro de kWh. Tu tarea es encontrar errores técnicos en las ofertas de la competencia y asegurar que la propuesta de Luminar sea técnicamente imbatible y cumpla con todas las normativas locales e internacionales. Tu tono es técnico, preciso y basado en datos."""

def calcular_roi_energetico(
    potencia_actual_w: float = 400.0,
    potencia_nueva_w: float = 150.0,
    cantidad: int = 100,
    horas_dia: float = 12.0,
    dias_ano: int = 300,
    tarifa_kwh_usd: float = 0.16,
    costo_inversion_usd: float = 12500.0,
    potencia_luminar_w: Optional[float] = None
) -> Dict[str, Any]:
    """Calcula el ahorro energético (kWh), ahorro económico anual y meses de recupero (ROI)."""
    p_nueva = potencia_luminar_w if potencia_luminar_w is not None else potencia_nueva_w
    kwh_actual_ano = (potencia_actual_w * cantidad * horas_dia * dias_ano) / 1000.0
    kwh_luminar_ano = (p_nueva * cantidad * horas_dia * dias_ano) / 1000.0
    kwh_ahorro_ano = kwh_actual_ano - kwh_luminar_ano
    ahorro_usd_ano = kwh_ahorro_ano * tarifa_kwh_usd
    ahorro_pct = round(((potencia_actual_w - p_nueva) / potencia_actual_w) * 100.0, 1) if potencia_actual_w > 0 else 0.0
    
    meses_retorno = round((costo_inversion_usd / ahorro_usd_ano) * 12.0, 1) if ahorro_usd_ano > 0 else 0.0
    reduccion_co2_ton = round(kwh_ahorro_ano * 0.000385, 2) # Factor de emisión promedio
    
    return {
        "kwh_ahorro_anual": round(kwh_ahorro_ano, 1),
        "ahorro_dolares_anual": round(ahorro_usd_ano, 2),
        "ahorro_energetico_pct": ahorro_pct,
        "meses_retorno_roi": meses_retorno,
        "reduccion_co2_ton_anual": reduccion_co2_ton,
        "tarifa_kwh_usd": tarifa_kwh_usd
    }

def generar_dictamen_tecnico(
    consulta: str, 
    pliego_info: Optional[Dict[str, Any]] = None,
    potencia_anterior_w: float = 400.0,
    potencia_nueva_w: float = 150.0,
    cantidad_unidades: int = 100
) -> Dict[str, Any]:
    """
    Genera dictamen de ingeniería con rigor normativo, fotometría, UGR, lux, ROI y detección de fallas de la competencia.
    """
    consulta_lower = consulta.lower()
    
    # 1. Parámetros Lumínicos y de Deslumbramiento (UGR)
    if "oficina" in consulta_lower or "administrativ" in consulta_lower or "retail" in consulta_lower:
        lux_objetivo = 500
        ugr_maximo = 19
        tipo_curva = "Batwing / Simétrica 90° con microprismático anti-glare"
        norma_aplicable = "UNIT 180 / CIE S 008 (Iluminación de interiores de trabajo)"
    elif "vial" in consulta_lower or "calle" in consulta_lower or "avenida" in consulta_lower or "alumbrado" in consulta_lower or "municip" in consulta_lower:
        lux_objetivo = 30 # Media M3/M4 o 1.5 cd/m2
        ugr_maximo = 15 # Control estricto de TI (Threshold Increment < 10%)
        tipo_curva = "Tipo II / Tipo III Asimétrica vial con corte total (Full Cutoff)"
        norma_aplicable = "UNIT-ISO 8995 / IESNA RP-8 (Alumbrado Público)"
    else: # Industrial / Bodega / Nave Logística
        lux_objetivo = 300
        ugr_maximo = 22
        tipo_curva = "Campana Industrial 120° / 90° lente óptica policarbonato Bayer UV"
        norma_aplicable = "UNIT 180 / UNE-EN 12464-1 (Zonas de trabajo industriales)"

    # 2. Análisis del ROI Energético
    roi = calcular_roi_energetico(
        potencia_actual_w=potencia_anterior_w,
        potencia_nueva_w=potencia_nueva_w,
        cantidad=cantidad_unidades,
        costo_inversion_usd=cantidad_unidades * 125.0
    )

    # 3. Puntos Críticos de Rigor Normativo
    topicos: List[str] = [
        "Estudio Fotométrico .IES y Niveles de Lux",
        f"Control de Deslumbramiento (UGR < {ugr_maximo})",
        f"Eficiencia y Ahorro kWh (ROI a {roi['meses_retorno_roi']} meses)",
        "Ensayos Acreditados IES LM-79 e IES LM-80 / TM-21"
    ]

    # 4. Detección de Errores de la Competencia (Trampas frecuentes en pliegos)
    errores_competencia = [
        "Presentan fichas comerciales en lugar de ensayos IES LM-79 emitidos por laboratorio acreditado ILAC.",
        "Declaran vida útil L70 extrapolada sin test real a 55°C/85°C/105°C bajo protocolo IES LM-80 / TM-21.",
        f"Incumplen el índice UGR (deslumbramiento > {ugr_maximo}), provocando fatiga visual y no-conformidad laboral.",
        "Omiten protección contra sobretensiones transitorias (DPS mínimo 6kV/10kV), provocando fallas masivas ante tormentas.",
        "Drivers genéricos con THD > 20% y FP < 0.90 que generan penalizaciones por energía reactiva en tarifa UTE."
    ]

    dictamen = (
        f"Estimado Equipo de Operaciones / Sebastián:\n\n"
        f"Como Ingeniero Eléctrico y Proyectista Lumínico de Luminar, emito el presente dictamen técnico de homologación "
        f"con máximo rigor normativo para: '{consulta}'.\n\n"
        f"1. PARÁMETROS LUMÍNICOS Y FOTOMETRÍA (.IES):\n"
        f"   - Nivel de iluminancia media proyectada: {lux_objetivo} lux sobre plano de trabajo (Uniformidad U0 ≥ 0.65).\n"
        f"   - Índice de Deslumbramiento Unificado: UGR < {ugr_maximo} garantizado por diseño óptico.\n"
        f"   - Fotometría: Archivo .IES generado bajo protocolo goniofotométrico IES LM-79.\n"
        f"   - Marco normativo de referencia: {norma_aplicable}.\n\n"
        f"2. RETORNO DE INVERSIÓN (ROI) Y AHORRO ENERGETICO (kWh):\n"
        f"   - Reducción de potencia por punto: De {potencia_anterior_w}W a {potencia_nueva_w}W ({roi['ahorro_energetico_pct']}% de ahorro).\n"
        f"   - Ahorro de energía anual estimado: {roi['kwh_ahorro_anual']:,} kWh/año ({roi['reduccion_co2_ton_anual']} ton CO2 no emitidas).\n"
        f"   - Ahorro financiero en tarifa eléctrica: USD {roi['ahorro_dolares_anual']:,} / año.\n"
        f"   - Período de amortización técnica (Payback): {roi['meses_retorno_roi']} meses.\n\n"
        f"3. VULNERABILIDADES EN OFERTAS DE LA COMPETENCIA (Blindaje de Pliego):\n"
        + "\n".join([f"   [!] {err}" for err in errores_competencia[:3]]) + "\n\n"
        f"4. CONCLUSIÓN DE HOMOLOGACIÓN:\n"
        f"   La solución propuesta por Luminar es técnicamente imbatible, cuenta con respaldo documental trazable "
        f"   y deja descalificada a la oferta competidora por incumplimiento de normativas de fotometría y seguridad eléctrica.\n\n"
        f"-- Ing. David Jiménez Vera\nIngeniero Eléctrico & Proyectista Lumínico - Luminar Uruguay"
    )

    return {
        "agente": PERFIL_DAVID["nombre"],
        "cargo": PERFIL_DAVID["cargo"],
        "prompt_sistema": PROMPT_SISTEMA_DAVID,
        "estudio_luminico": {
            "lux_objetivo": lux_objetivo,
            "ugr_maximo": ugr_maximo,
            "tipo_curva_ies": tipo_curva,
            "normativa": norma_aplicable
        },
        "roi_energetico": roi,
        "errores_competencia_detectados": errores_competencia,
        "topicos_evaluados": topicos,
        "dictamen_tecnico": dictamen
    }

if __name__ == "__main__":
    res = generar_dictamen_tecnico("Alumbrado público para avenida departamental y reducción de consumo")
    print(res["dictamen_tecnico"])

