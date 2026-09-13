"""
Motor Matemático de Costo Nacionalizado para Uruguay - Luminar
Calcula en milisegundos costos CIF, aranceles aduaneros uruguayos (AEC + Tasa Consular),
gastos portuarios, fletes y plazos de entrega según origen de mercadería.
"""

from typing import Dict, Any, Optional
from database import get_producto, get_config_importacion

def calcular_cotizacion(
    sku: str,
    cantidad: int,
    modo_envio: str = "local",  # "local", "aereo", "maritimo"
    margen_comercial: Optional[float] = None,
    dias_obra_limite: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calcula el costo nacionalizado, precio de venta sugerido y viabilidad logística.
    """
    producto = get_producto(sku)
    if not producto:
        raise ValueError(f"SKU '{sku}' no encontrado en el catálogo de Luminar.")

    config = get_config_importacion()
    margen = margen_comercial if margen_comercial is not None else config["margen_comercial_pct"]

    costo_fob_unitario = producto["costo_fob_usd"]
    fob_total = costo_fob_unitario * cantidad
    peso_total_kg = producto["peso_kg"] * cantidad
    cbm_total = producto["cbm"] * cantidad

    flete_internacional = 0.0
    plazo_entrega = ""
    es_importacion = False

    if modo_envio == "local":
        if producto["stock_mvd"] >= cantidad:
            plazo_entrega = "24 a 48 hs (Stock Montevideo disponible)"
            es_importacion = False
            # En stock local el costo base histórico ya está nacionalizado
            costo_nacionalizado_unitario = costo_fob_unitario * 1.35
            costo_total = costo_nacionalizado_unitario * cantidad
        else:
            # Si se pide local pero no hay stock suficiente, sugerir aéreo o mixto
            plazo_entrega = f"Stock MVD parcial ({producto['stock_mvd']}/{cantidad} u). Requiere importación para saldo."
            es_importacion = True
            modo_envio = "aereo"  # Fallback a aéreo para evaluar costo

    if modo_envio == "aereo":
        es_importacion = True
        flete_internacional = peso_total_kg * config["flete_aereo_usd_kg"]
        plazo_entrega = "10 a 14 días hábiles (Courier / Vía Aérea)"
    elif modo_envio == "maritimo":
        es_importacion = True
        # Mínimo 1 CBM para carga consolidada marítima
        cbm_cobrado = max(1.0, cbm_total)
        flete_internacional = cbm_cobrado * config["flete_maritimo_usd_cbm"]
        plazo_entrega = "45 a 55 días corridos (Contenedor Marítimo)"

    if es_importacion:
        seguro = (fob_total + flete_internacional) * config["seguro_pct"]
        cif = fob_total + flete_internacional + seguro
        aranceles_aduaneros = cif * (config["arancel_aec_pct"] + config["tasa_consular_pct"])
        # Gastos locales portuarios (Montecon/TCU + honorarios despachante prorrateados)
        gastos_locales = config["gastos_puerto_despacho_usd"] * (1.0 if modo_envio == "maritimo" else 0.4)
        costo_total = cif + aranceles_aduaneros + gastos_locales
        costo_nacionalizado_unitario = costo_total / cantidad

    # Cálculo de Precio de Venta según Margen: Precio = Costo / (1 - Margen)
    if margen >= 1.0:
        margen = 0.99
    precio_venta_total = costo_total / (1.0 - margen)
    precio_venta_unitario = precio_venta_total / cantidad

    # Evaluación de viabilidad de licitación o entrega de obra
    veredicto = "VIABLE"
    color_semaforo = "VERDE"
    motivo_viabilidad = "Plazo y disponibilidad óptimos."

    if dias_obra_limite is not None:
        if producto["stock_mvd"] >= cantidad:
            veredicto = "VIABLE_PLAZA"
            color_semaforo = "VERDE"
            motivo_viabilidad = f"Cubre 100% con stock Montevideo ({producto['stock_mvd']} u disponibles en plaza)."
        elif dias_obra_limite >= 50:
            veredicto = "VIABLE_MARITIMO"
            color_semaforo = "VERDE"
            motivo_viabilidad = f"Plazo de {dias_obra_limite} días permite importación marítima optimizando costo."
        elif 15 <= dias_obra_limite < 50:
            veredicto = "VIABLE_AEREO"
            color_semaforo = "AMARILLO"
            motivo_viabilidad = f"Plazo ajustado ({dias_obra_limite} días). Requiere envío aéreo o despacho prioritario."
        else:
            veredicto = "INVIABLE"
            color_semaforo = "ROJO"
            motivo_viabilidad = f"Inviable: el plazo oficial ({dias_obra_limite} días) es menor al tiempo logístico de importación y el stock local es insuficiente."

    return {
        "sku": sku,
        "descripcion": producto["descripcion"],
        "cantidad": cantidad,
        "modo_envio": modo_envio,
        "stock_mvd_disponible": producto["stock_mvd"],
        "costo_fob_unitario": round(costo_fob_unitario, 2),
        "flete_internacional_usd": round(flete_internacional, 2),
        "costo_nacionalizado_unitario": round(costo_nacionalizado_unitario, 2),
        "costo_total_usd": round(costo_total, 2),
        "precio_venta_unitario_usd": round(precio_venta_unitario, 2),
        "precio_venta_total_usd": round(precio_venta_total, 2),
        "margen_aplicado_pct": round(margen * 100, 1),
        "plazo_entrega": plazo_entrega,
        "veredicto_viabilidad": veredicto,
        "semaforo": color_semaforo,
        "motivo_viabilidad": motivo_viabilidad
    }

if __name__ == "__main__":
    # Test rápido de cálculo
    res = calcular_cotizacion("TITAN-200W-IP66", 120, modo_envio="local", dias_obra_limite=30)
    print("Prueba Cotización Local:", res)
    res_aereo = calcular_cotizacion("TITAN-200W-IP66", 200, modo_envio="aereo", dias_obra_limite=20)
    print("Prueba Cotización Aéreo:", res_aereo)
