"""
API Principal y Router Ultraliviano - Luminar B2B SaaS
Orquesta en milisegundos las intenciones del usuario hacia los módulos especializados:
- Cotizador determinístico y fletes
- Radar de compras estatales (ARCE)
- Asesor técnico de prescripción (Ing. David Jiménez Vera)
- Guardián del código y auditoría (Jefe de Equipo)
- Despacho de pre-reservas a depósito
"""

import os
import sys

# Asegurar path de imports locales
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from database import (
    init_db, get_todos_los_productos, get_producto, get_connection,
    upsert_producto, get_todos_los_clientes, actualizar_estado_cliente
)
from cost_engine import calcular_cotizacion
from services.arce_scraper import escanear_licitaciones_arce
from services.ollama_client import parsear_pliego_local
from services.david_agent import generar_dictamen_tecnico
from services.sales_strategist import construir_estrategia_aristoteles, ESTRATEGIAS_NICHO
from services.code_reviewer import auditar_ecosistema_completo

# Inicializar base de datos al arrancar
init_db()

app = FastAPI(
    title="Luminar B2B Core API",
    description="Sistema central de cotización inteligente, radar de licitaciones y prescripción técnica.",
    version="1.0.0"
)

# Permitir CORS para conexión desde frontend local o Tailscale
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos Pydantic ---

class CotizacionRequest(BaseModel):
    sku: str = Field(..., example="TITAN-200W-IP66")
    cantidad: int = Field(..., gt=0, example=120)
    modo_envio: str = Field(default="local", example="local")  # "local", "aereo", "maritimo"
    margen_comercial: Optional[float] = Field(default=0.35, ge=0.01, le=0.99, example=0.35)
    dias_obra_limite: Optional[int] = Field(default=None, example=30)

class DavidConsultaRequest(BaseModel):
    consulta: str = Field(..., example="El pliego exige 150W con driver DALI-2 y factor de potencia > 0.95")
    contexto_pliego: Optional[str] = None
    potencia_anterior_w: Optional[float] = Field(default=400.0)
    potencia_nueva_w: Optional[float] = Field(default=150.0)
    cantidad_unidades: Optional[int] = Field(default=100)

class EstrategiaVentasRequest(BaseModel):
    nicho: str = Field(default="industria", example="municipios")  # "municipios", "industria", "real_estate"
    cliente_nombre: str = Field(default="Cliente B2B", example="Intendencia de Canelones")
    consulta_tecnica: Optional[str] = Field(default="Alumbrado y eficiencia energética")

class ReservaRequest(BaseModel):
    sku: str = Field(..., example="TITAN-200W-IP66")
    cantidad: int = Field(..., gt=0, example=120)
    cliente: str = Field(..., example="Constructora del Plata")
    horas_reserva: int = Field(default=72, example=72)

class ParsearPliegoRequest(BaseModel):
    texto_pliego: str

class ActualizarEstadoClienteRequest(BaseModel):
    estado_pipeline: str = Field(..., example="En negociación / Muestra enviada")

class ProductoSyncRequest(BaseModel):
    sku: str = Field(..., example="TITAN-200W-IP66")
    descripcion: str = Field(..., example="Campana Industrial LED 200W IP66")
    potencia_w: float = Field(default=200.0)
    flujo_lm: float = Field(default=30000.0)
    ip_ik: str = Field(default="IP66/IK08")
    costo_fob_usd: float = Field(..., example=45.0)
    stock_mvd: int = Field(default=0, example=150)
    stock_fabrica: int = Field(default=0, example=1000)
    peso_kg: float = Field(default=3.5)
    cbm: float = Field(default=0.03)

# --- Endpoints ---

@app.get("/")
def read_root():
    return {
        "sistema": "Luminar B2B Operations",
        "version": "1.0.0",
        "estado": "Operativo",
        "documentacion": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok", "backend": "FastAPI", "db": "SQLite luminar_core.db"}

@app.get("/api/productos")
def listar_productos():
    """Retorna el catálogo completo con stock en plaza Montevideo y fábrica."""
    return get_todos_los_productos()

@app.post("/api/productos/sync")
def sincronizar_producto(req: ProductoSyncRequest):
    """
    Endpoint para sincronización por API con el software de la empresa (ERP / Sistema de Stock).
    Permite cargar o actualizar un producto, stock plaza MVD, stock fábrica y precio FOB.
    """
    producto = upsert_producto(
        sku=req.sku,
        descripcion=req.descripcion,
        potencia_w=req.potencia_w,
        flujo_lm=req.flujo_lm,
        ip_ik=req.ip_ik,
        costo_fob_usd=req.costo_fob_usd,
        stock_mvd=req.stock_mvd,
        stock_fabrica=req.stock_fabrica,
        peso_kg=req.peso_kg,
        cbm=req.cbm
    )
    return {"status": "SINCRONIZADO", "producto": producto}

@app.get("/api/clientes")
def listar_clientes(segmento: Optional[str] = None, estado: Optional[str] = None):
    """Retorna la cartera completa de clientes corporativos con filtros de segmento y pipeline."""
    return get_todos_los_clientes(segmento=segmento, estado=estado)

@app.put("/api/clientes/{cliente_id}/estado")
def mover_cliente_pipeline(cliente_id: int, req: ActualizarEstadoClienteRequest):
    """Mueve un cliente en el pipeline de ventas (ej: 'No contactado' -> 'Contactado / Propuesta Enviada')."""
    ok = actualizar_estado_cliente(cliente_id, req.estado_pipeline)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return {"status": "ACTUALIZADO", "cliente_id": cliente_id, "nuevo_estado": req.estado_pipeline}

@app.post("/api/cotizar")
def cotizar(req: CotizacionRequest):
    """
    Calcula en milisegundos costo nacionalizado, tributos aduaneros (AEC 16% + Tasa Consular 5%)
    y viabilidad logística según plazos.
    """
    try:
        resultado = calcular_cotizacion(
            sku=req.sku,
            cantidad=req.cantidad,
            modo_envio=req.modo_envio,
            margen_comercial=req.margen_comercial,
            dias_obra_limite=req.dias_obra_limite
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en motor de costos: {str(e)}")

@app.get("/api/arce/radar")
def radar_licitaciones():
    """Rastrea licitaciones de comprasestatales.gub.uy y cruza viabilidad con stock."""
    return escanear_licitaciones_arce()

@app.post("/api/arce/parsear")
async def parsear_pliego(req: ParsearPliegoRequest):
    """Extrae campos técnicos de un pliego vía Ollama local (Qwen 7B) a costo $0."""
    return await parsear_pliego_local(req.texto_pliego)

@app.post("/api/david/consultar")
def consultar_asesor_tecnico(req: DavidConsultaRequest):
    """Consulta al Ing. David Jiménez Vera para respaldo fotométrico (.ies), lux, UGR, ROI kWh y normativas IES."""
    return generar_dictamen_tecnico(
        consulta=req.consulta,
        pliego_info={"contexto": req.contexto_pliego},
        potencia_anterior_w=req.potencia_anterior_w or 400.0,
        potencia_nueva_w=req.potencia_nueva_w or 150.0,
        cantidad_unidades=req.cantidad_unidades or 100
    )

@app.post("/api/consultoria/estrategia-ventas")
def generar_estrategia_comercial(req: EstrategiaVentasRequest):
    """
    El Estratega de Ventas (Retórica de Aristóteles):
    Traduce el dictamen y los vatios/lúmenes del Ing. David en argumentos de Logos, Ethos y Pathos
    con enfoque de prospección adaptado a Gobiernos Municipales, Plantas Industriales o Real Estate.
    """
    dictamen_david = generar_dictamen_tecnico(req.consulta_tecnica)
    return construir_estrategia_aristoteles(
        nicho_clave=req.nicho,
        dictamen_david=dictamen_david,
        cliente_nombre=req.cliente_nombre
    )

@app.post("/api/reserva/crear")
def crear_pre_reserva(req: ReservaRequest):
    """
    Genera pre-reserva preventiva de SKU por 72 hs y redacta el correo transaccional
    para el encargado de depósito de Luminar.
    """
    prod = get_producto(req.sku)
    if not prod:
        raise HTTPException(status_code=404, detail="SKU no encontrado.")

    # Guardar en base de datos
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO alertas_reserva (sku, cantidad, cliente, plazo_reserva_horas, estado)
    VALUES (?, ?, ?, ?, 'ACTIVA')
    """, (req.sku, req.cantidad, req.cliente, req.horas_reserva))
    conn.commit()
    conn.close()

    # Redacción de correo transaccional
    email_asunto = f"[PRE-RESERVA PREVENTIVA LICITACIÓN] Bloqueo {req.cantidad}u {req.sku} - Cotización {req.cliente}"
    email_cuerpo = (
        f"Para: deposito@luminar.com.uy\n"
        f"Asunto: {email_asunto}\n\n"
        f"Estimados:\n"
        f"Favor retener temporalmente {req.cantidad} unidades del SKU '{req.sku}' ({prod['descripcion']}) "
        f"para el cliente {req.cliente}.\n"
        f"Plazo de reserva preventiva: {req.horas_reserva} horas hábiles mientras se adjudica la licitación u obra.\n"
        f"No despachar este lote sin validación comercial previa.\n\n"
        f"Atte,\nDirección Comercial Luminar Uruguay"
    )

    return {
        "status": "RESERVA_BLOQUEADA",
        "sku": req.sku,
        "cantidad": req.cantidad,
        "cliente": req.cliente,
        "horas_reserva": req.horas_reserva,
        "email_transaccional": {
            "asunto": email_asunto,
            "cuerpo": email_cuerpo
        }
    }

@app.get("/api/jefe-equipo/auditoria")
def auditoria_jefe_equipo():
    """
    El Jefe de Equipo ejecuta la auditoría estática y el control de códigos
    de todos los submódulos del ecosistema.
    """
    return auditar_ecosistema_completo()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
