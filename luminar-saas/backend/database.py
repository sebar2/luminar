"""
Base de Datos Local SQLite para Luminar Uruguay
Gestiona catálogo de productos, parámetros aduaneros uruguayos, licitaciones ARCE,
pre-reservas y cartera de clientes (CRM con Pipeline).
"""

import sqlite3
import os
import csv
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "luminar_core.db")
CLIENTES_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Clientes_Luminar_Limpio.csv")
)

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa las tablas en SQLite e inserta valores y catálogo base si no existen."""
    conn = get_connection()
    cur = conn.cursor()

    # 1. Tabla de Productos y Stock
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        sku TEXT PRIMARY KEY,
        descripcion TEXT,
        potencia_w REAL,
        flujo_lm REAL,
        ip_ik TEXT,
        costo_fob_usd REAL,
        stock_mvd INTEGER DEFAULT 0,
        stock_fabrica INTEGER DEFAULT 0,
        peso_kg REAL,
        cbm REAL
    )
    """)

    # 2. Parámetros de Importación Uruguay
    cur.execute("""
    CREATE TABLE IF NOT EXISTS config_importacion (
        id INTEGER PRIMARY KEY,
        flete_maritimo_usd_cbm REAL DEFAULT 120.0,
        flete_aereo_usd_kg REAL DEFAULT 8.5,
        seguro_pct REAL DEFAULT 0.005,
        arancel_aec_pct REAL DEFAULT 0.16,
        tasa_consular_pct REAL DEFAULT 0.05,
        gastos_puerto_despacho_usd REAL DEFAULT 650.0,
        margen_comercial_pct REAL DEFAULT 0.35
    )
    """)

    # 3. Registro de Licitaciones ARCE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS licitaciones_arce (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_licitacion TEXT,
        organismo TEXT,
        objeto TEXT,
        cantidad_total INTEGER,
        potencia_w TEXT,
        ip_requerido TEXT,
        fecha_entrega_limite TEXT,
        fecha_apertura TEXT,
        estado_viabilidad TEXT,
        pliego_url TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. Alertas y Pre-reservas de Stock
    cur.execute("""
    CREATE TABLE IF NOT EXISTS alertas_reserva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT,
        cantidad INTEGER,
        cliente TEXT,
        plazo_reserva_horas INTEGER DEFAULT 72,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado TEXT DEFAULT 'ACTIVA'
    )
    """)

    # 5. CRM de Clientes y Pipeline
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_apellido TEXT,
        cargo TEXT,
        empresa TEXT,
        vinculo TEXT,
        contacto_web_email TEXT,
        notas_dolor TEXT,
        segmento TEXT,
        estado_pipeline TEXT DEFAULT 'No contactado',
        fecha_proximo_paso TEXT,
        mensaje_sugerido TEXT
    )
    """)

    # 6. Cotizaciones Formales y Registro de Comisiones de Sebastián
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cotizaciones_sebastian (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_cotizacion TEXT UNIQUE,
        cliente TEXT NOT NULL,
        rut TEXT DEFAULT '',
        contacto TEXT,
        email_tel TEXT,
        nicho TEXT,
        moneda TEXT DEFAULT 'USD',
        tipo_cambio REAL DEFAULT 41.50,
        fecha_creacion TEXT,
        validez_dias INTEGER DEFAULT 15,
        items_json TEXT,
        costo_real_total_usd REAL,
        precio_venta_subtotal_usd REAL,
        costo_envio_usd REAL,
        iva_usd REAL,
        precio_venta_total_iva_usd REAL,
        margen_proyecto_pct REAL,
        comision_sebastian_usd REAL,
        comision_pct REAL,
        notas TEXT,
        estado TEXT DEFAULT 'EMITIDA'
    )
    """)

    # Verificar migración de columnas rut, moneda, tipo_cambio si la tabla ya existía
    cur.execute("PRAGMA table_info(cotizaciones_sebastian)")
    cols_existentes = [col[1] for col in cur.fetchall()]
    if "rut" not in cols_existentes:
        cur.execute("ALTER TABLE cotizaciones_sebastian ADD COLUMN rut TEXT DEFAULT ''")
    if "moneda" not in cols_existentes:
        cur.execute("ALTER TABLE cotizaciones_sebastian ADD COLUMN moneda TEXT DEFAULT 'USD'")
    if "tipo_cambio" not in cols_existentes:
        cur.execute("ALTER TABLE cotizaciones_sebastian ADD COLUMN tipo_cambio REAL DEFAULT 41.50")

    # Configuración de importación por defecto
    cur.execute("SELECT COUNT(*) FROM config_importacion")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO config_importacion (
            id, flete_maritimo_usd_cbm, flete_aereo_usd_kg, seguro_pct,
            arancel_aec_pct, tasa_consular_pct, gastos_puerto_despacho_usd, margen_comercial_pct
        ) VALUES (1, 120.0, 8.5, 0.005, 0.16, 0.05, 650.0, 0.35)
        """)

    # Catálogo inicial de productos
    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        productos_base = [
            ("TITAN-200W-IP66", "Campana Industrial LED 200W IP66 IK08 DALI-2", 200.0, 30000.0, "IP66/IK08", 45.0, 150, 1200, 3.8, 0.035),
            ("TITAN-150W-IP65", "Campana Industrial LED 150W IP65 IK08 LM-80", 150.0, 22500.0, "IP65/IK08", 36.0, 80, 800, 3.2, 0.028),
            ("SLIM-LINEAL-60W", "Perfilería LED Lineal Suspendida 60W UGR<19", 60.0, 7200.0, "IP40/IK06", 24.5, 45, 600, 2.1, 0.018),
            ("STREET-LED-100W", "Luminaria Alumbrado Público Vial 100W 5000K", 100.0, 14000.0, "IP66/IK09", 52.0, 200, 1500, 4.5, 0.042),
            ("ESTANCA-LED-40W", "Luminaria Estanca 40W Grado Alimenticio Policarbonato", 40.0, 4800.0, "IP66/IK10", 18.0, 320, 2500, 1.4, 0.012)
        ]
        cur.executemany("""
        INSERT INTO productos (
            sku, descripcion, potencia_w, flujo_lm, ip_ik, costo_fob_usd,
            stock_mvd, stock_fabrica, peso_kg, cbm
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, productos_base)

    # Cargar clientes desde el CSV limpio si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM clientes")
    if cur.fetchone()[0] == 0 and os.path.exists(CLIENTES_CSV_PATH):
        importar_clientes_desde_csv(CLIENTES_CSV_PATH, conn)

    conn.commit()
    conn.close()

def importar_clientes_desde_csv(csv_path: str, conn: Optional[sqlite3.Connection] = None):
    """Importa o sincroniza los clientes desde el archivo CSV limpio a SQLite."""
    cerrar_al_terminar = False
    if conn is None:
        conn = get_connection()
        cerrar_al_terminar = True

    cur = conn.cursor()
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = []
        for row in reader:
            filas.append((
                row.get("Nombre y Apellido", "").strip(),
                row.get("Cargo", "").strip(),
                row.get("Empresa", "").strip(),
                row.get("Vínculo / Contacto", "").strip(),
                row.get("Tel / Web / Email", "").strip(),
                row.get("Estado / Notas", "").strip(),
                row.get("Segmento / Tipo de Cliente", "").strip(),
                row.get("Estado de Contacto", "No contactado").strip() or "No contactado",
                row.get("Fecha Próximo Paso", "").strip(),
                row.get("Mensaje Sugerido", "").strip()
            ))

        cur.executemany("""
        INSERT INTO clientes (
            nombre_apellido, cargo, empresa, vinculo, contacto_web_email,
            notas_dolor, segmento, estado_pipeline, fecha_proximo_paso, mensaje_sugerido
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, filas)

    conn.commit()
    if cerrar_al_terminar:
        conn.close()

def get_config_importacion() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM config_importacion WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "flete_maritimo_usd_cbm": 120.0,
        "flete_aereo_usd_kg": 8.5,
        "seguro_pct": 0.005,
        "arancel_aec_pct": 0.16,
        "tasa_consular_pct": 0.05,
        "gastos_puerto_despacho_usd": 650.0,
        "margen_comercial_pct": 0.35
    }

def get_producto(sku: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE sku = ?", (sku,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_todos_los_productos() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos ORDER BY sku ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def upsert_producto(
    sku: str,
    descripcion: str,
    potencia_w: float,
    flujo_lm: float,
    ip_ik: str,
    costo_fob_usd: float,
    stock_mvd: int,
    stock_fabrica: int,
    peso_kg: float,
    cbm: float
) -> Dict[str, Any]:
    """Inserta o actualiza un producto (permite sincronización por API o carga Excel/CSV)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO productos (
        sku, descripcion, potencia_w, flujo_lm, ip_ik, costo_fob_usd,
        stock_mvd, stock_fabrica, peso_kg, cbm
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(sku) DO UPDATE SET
        descripcion = excluded.descripcion,
        potencia_w = excluded.potencia_w,
        flujo_lm = excluded.flujo_lm,
        ip_ik = excluded.ip_ik,
        costo_fob_usd = excluded.costo_fob_usd,
        stock_mvd = excluded.stock_mvd,
        stock_fabrica = excluded.stock_fabrica,
        peso_kg = excluded.peso_kg,
        cbm = excluded.cbm
    """, (sku, descripcion, potencia_w, flujo_lm, ip_ik, costo_fob_usd, stock_mvd, stock_fabrica, peso_kg, cbm))
    conn.commit()
    conn.close()
    return get_producto(sku)

def get_todos_los_clientes(segmento: Optional[str] = None, estado: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM clientes WHERE 1=1"
    params = []
    if segmento:
        query += " AND segmento = ?"
        params.append(segmento)
    if estado:
        query += " AND estado_pipeline = ?"
        params.append(estado)
    query += " ORDER BY empresa ASC"
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def actualizar_estado_cliente(cliente_id: int, nuevo_estado: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE clientes SET estado_pipeline = ? WHERE id = ?", (nuevo_estado, cliente_id))
    conn.commit()
    afectados = cur.rowcount
    conn.close()
    return afectados > 0

def agregar_licitacion_a_pipeline(lic: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agrega o actualiza una licitación de ARCE en la tabla de clientes / pipeline CRM,
    calculando la probabilidad de éxito según la viabilidad logística.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    id_arce = lic.get("id_arce", "ARCE-LIC")
    organismo = lic.get("organismo", "Organismo Estatal")
    titulo = lic.get("titulo", "")
    sku = lic.get("sku_sugerido", "TITAN-200W-IP66")
    cant = lic.get("cantidad", 100)
    url_pliego = lic.get("url_pliego", "https://comprasestatales.gub.uy")
    fecha_apertura = lic.get("fecha_apertura", "A confirmar")
    
    analisis = lic.get("analisis_logistico", {})
    veredicto = analisis.get("veredicto", "VIABLE")
    motivo = analisis.get("motivo", "")
    
    # Cálculo de probabilidad estimada según disponibilidad y plazos
    if veredicto == "VIABLE_PLAZA":
        probabilidad = "90% (Muy Alta - Entrega Inmediata MVD)"
        estado_ini = "Propuesta / Cotización Activa"
    elif veredicto == "VIABLE_MARITIMO":
        probabilidad = "75% (Alta - Margen y Plazo Óptimos)"
        estado_ini = "Propuesta / Cotización Activa"
    elif veredicto == "VIABLE_AEREO":
        probabilidad = "60% (Media - Plazo Ajustado Courier)"
        estado_ini = "En negociación / Muestra enviada"
    else:
        probabilidad = "25% (Baja - Inviable por Plazo Estricto)"
        estado_ini = "Standby / Proyecto Futuro"

    empresa_nombre = f"[{organismo}] {titulo[:65]}"
    notas = (
        f"Licitación ID: {id_arce} | Probabilidad Éxito: {probabilidad}\n"
        f"Producto sugerido: {sku} x {cant} u.\n"
        f"Apertura ofertas: {fecha_apertura}.\n"
        f"Viabilidad Logística: {veredicto} - {motivo}"
    )
    mensaje = (
        f"Presentación formal para llamado {id_arce} ({organismo}). "
        f"Oferta con luminarias Luminar, catálogo técnico, curvas .ies y entrega asegurada."
    )

    # Verificar si ya existe por vínculo único
    cur.execute("SELECT id FROM clientes WHERE vinculo = ?", (f"ARCE:{id_arce}",))
    existente = cur.fetchone()
    
    if existente:
        cliente_id = existente[0]
        cur.execute("""
        UPDATE clientes SET
            notas_dolor = ?,
            estado_pipeline = ?,
            fecha_proximo_paso = ?
        WHERE id = ?
        """, (notas, estado_ini, fecha_apertura, cliente_id))
    else:
        cur.execute("""
        INSERT INTO clientes (
            nombre_apellido, cargo, empresa, vinculo, contacto_web_email,
            notas_dolor, segmento, estado_pipeline, fecha_proximo_paso, mensaje_sugerido
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Comisión Asesora de Compras",
            f"Licitación {id_arce}",
            empresa_nombre,
            f"ARCE:{id_arce}",
            url_pliego,
            notas,
            "Licitaciones Públicas & Compras Estatales",
            estado_ini,
            fecha_apertura,
            mensaje
        ))
        cliente_id = cur.lastrowid

    conn.commit()
    conn.close()
    
    return {
        "cliente_id": cliente_id,
        "empresa": empresa_nombre,
        "probabilidad": probabilidad,
        "estado": estado_ini
    }

# =========================================================================
# GESTIÓN DE COTIZACIONES Y COMISIONES DE SEBASTIÁN
# =========================================================================

def guardar_cotizacion_sebastian(
    numero_cotizacion: str,
    cliente: str,
    contacto: str,
    email_tel: str,
    nicho: str,
    fecha_creacion: str,
    validez_dias: int,
    items_json: str,
    costo_real_total_usd: float,
    precio_venta_subtotal_usd: float,
    costo_envio_usd: float,
    iva_usd: float,
    precio_venta_total_iva_usd: float,
    margen_proyecto_pct: float,
    comision_sebastian_usd: float,
    comision_pct: float,
    notas: str = "",
    estado: str = "EMITIDA",
    rut: str = "",
    moneda: str = "USD",
    tipo_cambio: float = 41.50
) -> int:
    """Registra una cotización formal con separación estricta de costo real vs precio cliente y comisión acordada."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
    INSERT INTO cotizaciones_sebastian (
        numero_cotizacion, cliente, rut, contacto, email_tel, nicho, moneda, tipo_cambio,
        fecha_creacion, validez_dias, items_json, costo_real_total_usd, precio_venta_subtotal_usd,
        costo_envio_usd, iva_usd, precio_venta_total_iva_usd, margen_proyecto_pct,
        comision_sebastian_usd, comision_pct, notas, estado
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        numero_cotizacion, cliente, rut, contacto, email_tel, nicho, moneda, tipo_cambio,
        fecha_creacion, validez_dias, items_json, costo_real_total_usd, precio_venta_subtotal_usd,
        costo_envio_usd, iva_usd, precio_venta_total_iva_usd, margen_proyecto_pct,
        comision_sebastian_usd, comision_pct, notas, estado
    ))
    
    cot_id = cur.lastrowid
    conn.commit()
    conn.close()
    return cot_id

def get_cotizaciones_sebastian() -> List[Dict[str, Any]]:
    """Obtiene el historial completo de cotizaciones emitidas por Sebastián con cálculo de comisiones."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cotizaciones_sebastian ORDER BY id DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def actualizar_estado_cotizacion(cotizacion_id: int, nuevo_estado: str) -> bool:
    """Actualiza el estado comercial de una cotización (EMITIDA, NEGOCIACIÓN, COBRADA/GANADA, PERDIDA)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE cotizaciones_sebastian SET estado = ? WHERE id = ?", (nuevo_estado, cotizacion_id))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
    print("Base de datos luminar_core.db inicializada con catálogo, clientes y cotizaciones de Sebastián.")
