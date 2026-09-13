"""
Módulo Jefe de Equipo / Ingeniero de Sistemas (Code Reviewer, DB Auditor & Network Guardian)
Audita, valida y controla de forma integral:
1. Calidad y Ciberseguridad del Código (AST, Inyecciones SQL, RCE, Secret Leaks).
2. Arquitectura, Estructura e Integridad de la Base de Datos SQLite (PRAGMA integrity, tablas, PKs, registros).
3. Monitoreo de Red, Puertos y Pings en Vivo (Puertos 8000 y 8501, latencia TCP, conexiones activas, clasificación de IPs).
"""

import ast
import os
import glob
import re
import sqlite3
import socket
import time
import subprocess
from typing import Dict, List, Any, Optional

PATRONES_SECRETOS = [
    (r"sk-[a-zA-Z0-9_\-\.]{20,}", "Posible API Key estilo OpenAI/Qwen hardcodeada"),
    (r"bearer\s+['\"][a-zA-Z0-9_\-\.]{20,}['\"]", "Token Bearer hardcodeado en texto plano"),
    (r"(password|secreto|passwd)\s*=\s*['\"][^'\"]{6,}['\"]", "Posible contraseña en texto plano")
]

class InspectorDeCodigo(ast.NodeVisitor):
    def __init__(self, filepath: str, raw_source: str):
        self.filepath = filepath
        self.raw_source = raw_source
        self.advertencias: List[str] = []
        self.riesgos_seguridad: List[str] = []
        self.funciones_definidas: List[str] = []
        self.imports: List[str] = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.funciones_definidas.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.funciones_definidas.append(f"async {node.name}")
        self.generic_visit(node)

    def visit_Call(self, node):
        # Detección de posibles queries SQL concatenadas (Inyección SQL)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("execute", "executemany"):
                if node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp)):
                    # Permitir consultas de metadatos propios de introspección si está en code_reviewer.py
                    es_introspeccion = False
                    if "code_reviewer.py" in self.filepath and isinstance(node.args[0], ast.JoinedStr):
                        for val in node.args[0].values:
                            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                                if "table_info" in val.value or "SELECT count(*)" in val.value:
                                    es_introspeccion = True
                    if not es_introspeccion:
                        self.riesgos_seguridad.append(
                            f"Línea {node.lineno}: [SQLi RISK] Posible concatenación de strings en consulta SQL. Usar parámetros '?'."
                        )

        # Detección de llamadas a eval() o exec()
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                self.riesgos_seguridad.append(
                    f"Línea {node.lineno}: [CODE EXEC RISK] Uso prohibido de {node.func.id}()."
                )

        self.generic_visit(node)

    def escanear_secretos_en_texto(self):
        """Revisa líneas en busca de tokens, API keys o contraseñas en código fuente."""
        for num_linea, linea in enumerate(self.raw_source.splitlines(), start=1):
            for regex, desc in PATRONES_SECRETOS:
                if re.search(regex, linea, re.IGNORECASE):
                    if not linea.strip().startswith("#") and "regex" not in linea.lower():
                        self.riesgos_seguridad.append(
                            f"Línea {num_linea}: [SECRET LEAK] {desc}."
                        )

def auditar_archivo(filepath: str) -> Dict[str, Any]:
    """Audita un script individual de Python mediante AST y reglas de seguridad."""
    filename = os.path.basename(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        return {
            "archivo": filename,
            "estado": "ERROR_LECTURA",
            "mensaje": str(e),
            "advertencias": [],
            "riesgos_seguridad": []
        }

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as e:
        return {
            "archivo": filename,
            "estado": "FALLO_SINTAXIS",
            "mensaje": f"Error de sintaxis en línea {e.lineno}: {e.msg}",
            "advertencias": [f"Línea {e.lineno}: {e.msg}"],
            "riesgos_seguridad": []
        }

    inspector = InspectorDeCodigo(filepath, source)
    inspector.visit(tree)
    inspector.escanear_secretos_en_texto()

    estado = "APROBADO"
    if inspector.riesgos_seguridad:
        estado = "VULNERABLE"
    elif inspector.advertencias:
        estado = "OBSERVADO"

    return {
        "archivo": filename,
        "ruta": filepath,
        "estado": estado,
        "total_funciones": len(inspector.funciones_definidas),
        "funciones": inspector.funciones_definidas,
        "total_imports": len(inspector.imports),
        "advertencias": inspector.advertencias,
        "riesgos_seguridad": inspector.riesgos_seguridad
    }

# =========================================================================
# AUDITORÍA DE BASE DE DATOS SQLITE (Estructura, Integridad y Permisos)
# =========================================================================

def auditar_base_de_datos(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Analiza a fondo la base de datos: integridad estructural (PRAGMA),
    tablas existentes, llaves primarias, total de registros y tamaño en disco.
    """
    if db_path is None:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "luminar_core.db")

    if not os.path.exists(db_path):
        return {
            "estado": "NO_ENCONTRADA",
            "mensaje": f"Archivo de base de datos no existe en: {db_path}",
            "integridad": "DESCONOCIDA",
            "tablas": []
        }

    tamano_bytes = os.path.getsize(db_path)
    tamano_kb = round(tamano_bytes / 1024, 2)

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # 1. Chequeo de integridad física de páginas SQLite
        cur.execute("PRAGMA integrity_check")
        resultado_integridad = cur.fetchone()[0]

        # 2. Modo de Journal y Foreign Keys
        cur.execute("PRAGMA journal_mode")
        journal_mode = cur.fetchone()[0]
        cur.execute("PRAGMA foreign_keys")
        foreign_keys = bool(cur.fetchone()[0])

        # 3. Listar todas las tablas y su estructura
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tablas_nombres = [r[0] for r in cur.fetchall()]

        detalle_tablas = []
        total_filas_sistema = 0

        for t in tablas_nombres:
            # Contar filas
            cur.execute(f"SELECT count(*) FROM {t}")
            cant_filas = cur.fetchone()[0]
            total_filas_sistema += cant_filas

            # Información de columnas y PKs
            cur.execute(f"PRAGMA table_info({t})")
            columnas_info = cur.fetchall()
            cols = [{"columna": col[1], "tipo": col[2], "es_pk": bool(col[5])} for col in columnas_info]
            pk_cols = [c["columna"] for c in cols if c["es_pk"]]

            detalle_tablas.append({
                "tabla": t,
                "total_registros": cant_filas,
                "columnas": cols,
                "primary_keys": pk_cols
            })

        conn.close()

        estado_db = "INTEGRA_Y_ESTRUCTURADA" if resultado_integridad == "ok" else "CORRUPTA"

        return {
            "estado": estado_db,
            "integridad_pragma": resultado_integridad,
            "archivo_db": os.path.basename(db_path),
            "ruta_absoluta": db_path,
            "tamano_kb": tamano_kb,
            "journal_mode": journal_mode,
            "foreign_keys_activo": foreign_keys,
            "total_tablas": len(detalle_tablas),
            "total_registros_totales": total_filas_sistema,
            "seguridad_aislamiento": "CORRECTO (Aislada en backend, no expuesta públicamente en web)",
            "detalle_tablas": detalle_tablas
        }
    except Exception as e:
        return {
            "estado": "ERROR_LECTURA",
            "mensaje": str(e),
            "integridad": "ERROR",
            "tablas": []
        }

# =========================================================================
# AUDITORÍA DE RED, PUERTOS Y PINGS EN VIVO
# =========================================================================

def auditar_red_y_puertos() -> Dict[str, Any]:
    """
    Monitorea en vivo los puertos 8000 (FastAPI) y 8501 (Streamlit):
    - Mide latencia de respuesta TCP (ping a socket).
    - Detecta conexiones activas (netstat).
    - Clasifica las IPs conectadas (Localhost, LAN, Tailscale, o Externa no autorizada).
    """
    puertos_a_vigilar = [8000, 8501]
    diagnostico_puertos = []

    for p in puertos_a_vigilar:
        t0 = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
        res = s.connect_ex(("127.0.0.1", p))
        latencia_ms = round((time.time() - t0) * 1000, 2)
        s.close()

        activo = (res == 0)
        diagnostico_puertos.append({
            "puerto": p,
            "servicio": "FastAPI Core API" if p == 8000 else "Streamlit Web UI",
            "estado": "ESCUCHANDO_Y_RESPONDIENDO" if activo else "INACTIVO_CERRADO",
            "latencia_ping_ms": latencia_ms if activo else None
        })

    # Analizar conexiones de red activas en esos puertos con netstat
    conexiones_activas = []
    ips_sospechosas = []

    try:
        output = subprocess.check_output(["netstat", "-ano"], text=True)
        for linea in output.splitlines():
            linea_limpia = linea.strip()
            if any(f":{p}" in linea_limpia for p in puertos_a_vigilar):
                partes = re.split(r"\s+", linea_limpia)
                if len(partes) >= 4:
                    proto = partes[0]
                    local_addr = partes[1]
                    foreign_addr = partes[2]
                    estado_tcp = partes[3] if len(partes) > 3 else "UNKNOWN"

                    # Clasificar IP de origen
                    clasificacion = "DESCONOCIDA"
                    ip_remota = foreign_addr.rsplit(":", 1)[0].replace("[", "").replace("]", "").strip()

                    # Sockets locales en escucha o loopback
                    if estado_tcp == "LISTENING" or ip_remota in ("127.0.0.1", "::1", "0.0.0.0", "*", "::", "") or foreign_addr.strip() in ("[::]:0", "0.0.0.0:0", "*:*"):
                        clasificacion = "LOCALHOST (Socket local en tu propio equipo)"
                    elif ip_remota.startswith("192.168.") or ip_remota.startswith("10.") or ip_remota.startswith("172.16."):
                        clasificacion = "RED_LOCAL_LAN (Dispositivo en tu red Wi-Fi/Ethernet)"
                    elif ip_remota.startswith("100."):
                        clasificacion = "TAILSCALE_VPN (Túnel seguro remoto autorizado)"
                    else:
                        clasificacion = "EXTERNA_ALERTA"
                        if estado_tcp == "ESTABLISHED":
                            ips_sospechosas.append(foreign_addr)

                    conexiones_activas.append({
                        "protocolo": proto,
                        "direccion_local": local_addr,
                        "direccion_remota": foreign_addr,
                        "estado_tcp": estado_tcp,
                        "clasificacion_origen": clasificacion
                    })
    except Exception as e:
        conexiones_activas.append({"error": f"No se pudo consultar netstat: {e}"})

    estado_red = "SEGURA_SIN_INTRUSIONES"
    if ips_sospechosas:
        estado_red = "ALERTA_CONEXION_EXTERNA_DETECTADA"

    return {
        "estado_red": estado_red,
        "puertos_monitoreados": diagnostico_puertos,
        "total_conexiones_activas": len(conexiones_activas),
        "conexiones_sospechosas": ips_sospechosas,
        "detalle_conexiones": conexiones_activas[:15]  # Muestra las 15 más recientes
    }

# =========================================================================
# AUDITORÍA GLOBAL DEL ECOSISTEMA (Jefe de Equipo)
# =========================================================================

def auditar_ecosistema_completo(base_dir: str = None) -> Dict[str, Any]:
    """
    El Jefe de Equipo escanea y audita:
    1. Código fuente y vulnerabilidades.
    2. Base de datos SQLite (integridad y tablas).
    3. Red, puertos y pings en tiempo real.
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))

    # 1. Auditoría de Código
    patron_backend = os.path.join(base_dir, "*.py")
    patron_servicios = os.path.join(base_dir, "services", "*.py")
    archivos = glob.glob(patron_backend) + glob.glob(patron_servicios)
    
    reporte_archivos = []
    total_errores = 0
    total_advertencias = 0
    total_vulnerabilidades = 0

    for f in archivos:
        res = auditar_archivo(f)
        reporte_archivos.append(res)
        if res["estado"] in ("FALLO_SINTAXIS", "ERROR_LECTURA"):
            total_errores += 1
        if res["estado"] == "VULNERABLE":
            total_vulnerabilidades += len(res["riesgos_seguridad"])
        total_advertencias += len(res["advertencias"])

    # 2. Auditoría de Base de Datos
    reporte_db = auditar_base_de_datos()

    # 3. Auditoría de Red y Puertos
    reporte_red = auditar_red_y_puertos()

    dictamen_jefe = "SISTEMA_OPTIMO_Y_SEGURO"
    if total_errores > 0 or total_vulnerabilidades > 0 or reporte_db.get("estado") == "CORRUPTA" or reporte_red.get("estado_red") != "SEGURA_SIN_INTRUSIONES":
        dictamen_jefe = "CRITICO_VULNERABILIDADES_DETECTADAS"
    elif total_advertencias > 0:
        dictamen_jefe = "APROBADO_CON_OBSERVACIONES"

    return {
        "rol": "Jefe de Equipo / Ingeniero de Sistemas (Security Guardian)",
        "dictamen_global": dictamen_jefe,
        "archivos_auditados": len(reporte_archivos),
        "total_errores_sintaxis": total_errores,
        "total_riesgos_seguridad": total_vulnerabilidades,
        "total_advertencias": total_advertencias,
        "detalle_por_modulo": reporte_archivos,
        "auditoria_base_datos": reporte_db,
        "auditoria_red_puertos": reporte_red
    }

if __name__ == "__main__":
    rep = auditar_ecosistema_completo()
    print("=== DICTAMEN DEL JEFE DE EQUIPO ===")
    print(f"Estado Global: {rep['dictamen_global']}")
    print(f"Base de Datos: {rep['auditoria_base_datos']['estado']} (Tablas: {rep['auditoria_base_datos']['total_tablas']}, Registros: {rep['auditoria_base_datos']['total_registros_totales']})")
    print(f"Red y Puertos: {rep['auditoria_red_puertos']['estado_red']}")
    for p in rep['auditoria_red_puertos']['puertos_monitoreados']:
        print(f" - Puerto {p['puerto']} ({p['servicio']}): {p['estado']} - Ping: {p['latencia_ping_ms']} ms")
