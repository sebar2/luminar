"""
Cliente de Conexión a Subagentes Locales en Ollama (RTX 3080 - Costo USD 0)
Extrae campos técnicos estructurados de pliegos de licitación en JSON estricto.
Incluye mecanismo de contingencia heurística en caso de que Ollama no esté iniciado.
"""

import httpx
import json
import re
from typing import Dict, Any

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO_DEFAULT = "qwen2.5:7b"

PROMPT_SISTEMA_PARSER = """Eres un extractor de datos de pliegos de compra pública en Uruguay.
Tu única función es extraer campos estructurados en formato JSON estricto sin preámbulos ni explicaciones.
JSON Schema requerido:
{
  "organismo": string,
  "objeto": string,
  "cantidad_total": integer,
  "potencia_w": string o null,
  "ip_requerido": string o null,
  "fecha_entrega_limite": "YYYY-MM-DD" o null,
  "dias_plazo_entrega": integer o null,
  "exige_stock_nacional": boolean
}
"""

async def parsear_pliego_local(texto_pliego: str, modelo: str = MODELO_DEFAULT) -> Dict[str, Any]:
    """
    Envía el texto del pliego a Ollama local para parseo JSON sin costo de tokens.
    Si Ollama no está activo en localhost:11434, aplica fallback heurístico determinístico.
    """
    prompt = f"{PROMPT_SISTEMA_PARSER}\nTexto del Pliego:\n\"\"\"\n{texto_pliego[:3500]}\n\"\"\""
    
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                raw_json = data.get("response", "{}")
                return json.loads(raw_json)
    except Exception:
        # Fallback heurístico en caso de que Ollama no esté corriendo en segundo plano
        return extraer_pliego_fallback(texto_pliego)

    return extraer_pliego_fallback(texto_pliego)

def extraer_pliego_fallback(texto: str) -> Dict[str, Any]:
    """Extractor determinístico basado en expresiones regulares para cuando Ollama está offline."""
    texto_lower = texto.lower()
    
    # Organismo
    organismo = "Organismo Público UY"
    if "ute" in texto_lower:
        organismo = "UTE (Administración Nacional de Usinas y Trasmisiones Eléctricas)"
    elif "canelones" in texto_lower:
        organismo = "Intendencia de Canelones"
    elif "montevideo" in texto_lower:
        organismo = "Intendencia de Montevideo"
    elif "mtop" in texto_lower:
        organismo = "MTOP"
    elif "anp" in texto_lower:
        organismo = "ANP (Administración Nacional de Puertos)"

    # Cantidad
    match_cant = re.search(r'(\d+)\s*(?:unidades|campanas|luminarias|piezas|proyectores|u\b)', texto_lower)
    cantidad = int(match_cant.group(1)) if match_cant else 100

    # Potencia
    match_pot = re.search(r'(\d{2,4}\s*w)', texto_lower)
    potencia = match_pot.group(1).upper() if match_pot else "200W"

    # Protección IP
    match_ip = re.search(r'(ip\s*\d{2})', texto_lower)
    ip_req = match_ip.group(1).upper().replace(" ", "") if match_ip else "IP66"

    # Plazo entrega en días
    match_dias = re.search(r'(\d+)\s*(?:días|dias)\s*(?:de plazo|corridos|hábiles)?', texto_lower)
    dias = int(match_dias.group(1)) if match_dias else 30

    return {
        "organismo": organismo,
        "objeto": f"Suministro de {cantidad} luminarias {potencia} {ip_req}",
        "cantidad_total": cantidad,
        "potencia_w": potencia,
        "ip_requerido": ip_req,
        "fecha_entrega_limite": None,
        "dias_plazo_entrega": dias,
        "exige_stock_nacional": "inmediata" in texto_lower or "en plaza" in texto_lower,
        "fuente_extraccion": "heuristica_fallback"
    }
