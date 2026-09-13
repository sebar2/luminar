"""
Suite de Pruebas Automatizadas para Luminar SaaS
Verifica:
1. Conexión y modelos de base de datos SQLite
2. Motor determinístico de costos nacionalizados para Uruguay
3. Licitaciones y cruce logístico de ARCE
4. Asesor técnico David Jiménez Vera
5. Auditoría del Jefe de Equipo
"""

import unittest
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(backend_dir)
sys.path.append(os.path.join(backend_dir, "services"))

from database import init_db, get_producto, get_config_importacion, get_todos_los_productos
from cost_engine import calcular_cotizacion
from services.arce_scraper import escanear_licitaciones_arce
from services.david_agent import generar_dictamen_tecnico, calcular_roi_energetico
from services.sales_strategist import construir_estrategia_aristoteles, ESTRATEGIAS_NICHO
from services.code_reviewer import auditar_ecosistema_completo

class TestLuminarSaaS(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_database_init_and_products(self):
        productos = get_todos_los_productos()
        self.assertGreaterEqual(len(productos), 5)
        prod = get_producto("TITAN-200W-IP66")
        self.assertIsNotNone(prod)
        self.assertEqual(prod["potencia_w"], 200.0)
        self.assertEqual(prod["stock_mvd"], 150)

    def test_config_importacion(self):
        cfg = get_config_importacion()
        self.assertEqual(cfg["arancel_aec_pct"], 0.16)
        self.assertEqual(cfg["tasa_consular_pct"], 0.05)
        self.assertEqual(cfg["flete_maritimo_usd_cbm"], 120.0)

    def test_cost_engine_local_stock(self):
        # 100 unidades de TITAN-200W-IP66 con 150 en stock Montevideo
        res = calcular_cotizacion("TITAN-200W-IP66", 100, modo_envio="local", dias_obra_limite=30)
        self.assertEqual(res["veredicto_viabilidad"], "VIABLE_PLAZA")
        self.assertEqual(res["semaforo"], "VERDE")
        self.assertGreater(res["precio_venta_unitario_usd"], res["costo_nacionalizado_unitario"])

    def test_cost_engine_inviable_deadline(self):
        # 300 unidades de TITAN-200W-IP66 (supera stock MVD de 150) con plazo de 5 días
        res = calcular_cotizacion("TITAN-200W-IP66", 300, modo_envio="local", dias_obra_limite=5)
        self.assertEqual(res["veredicto_viabilidad"], "INVIABLE")
        self.assertEqual(res["semaforo"], "ROJO")

    def test_arce_scraper(self):
        licitaciones = escanear_licitaciones_arce()
        self.assertGreaterEqual(len(licitaciones), 4)
        for lic in licitaciones:
            self.assertIn("analisis_logistico", lic)
            self.assertIn(lic["analisis_logistico"]["semaforo"], ["VERDE", "AMARILLO", "ROJO"])

    def test_david_agent(self):
        res = generar_dictamen_tecnico("Se requiere dimmer DALI-2 y bajo THD para licitación UTE")
        self.assertIn("Ing. David Jiménez Vera", res["agente"])
        self.assertTrue(len(res["topicos_evaluados"]) > 0)
        self.assertIn("estudio_luminico", res)
        self.assertIn("roi_energetico", res)
        self.assertGreater(res["estudio_luminico"]["lux_objetivo"], 0)
        self.assertGreater(res["roi_energetico"]["kwh_ahorro_anual"], 0)
        self.assertTrue(len(res["errores_competencia_detectados"]) >= 3)

    def test_sales_strategist_aristotle(self):
        # Probar generación de pitch en los 6 nichos (incluyendo barrios privados, canchas deportivas y residencias)
        for nicho in ["municipios", "industria", "real_estate", "barrios_privados", "canchas_deportivas", "residencias_premium"]:
            res = construir_estrategia_aristoteles(nicho, cliente_nombre="Cliente Test")
            self.assertIn("nicho_identificado", res)
            self.assertIn("logos", res)
            self.assertIn("ethos", res)
            self.assertIn("pathos", res)
            self.assertIn("frase_fuerza", res)
            self.assertIn("pitch_apertura", res)
            self.assertIn("pitch_completo", res)
            self.assertIn("propuesta_email", res)
            self.assertIn("speech_reunion", res)

    def test_pdf_generation_and_quote_persistence(self):
        from database import guardar_cotizacion_sebastian, get_cotizaciones_sebastian
        from services.pdf_generator import generar_pdf_cotizacion_cliente
        import json
        import time

        items = [
            {"sku": "TITAN-200W-IP66", "descripcion": "Campana LED Industrial 200W", "cantidad": 20, "precio_venta_unitario_usd": 110.0, "costo_unitario_usd": 65.0}
        ]
        
        num_cot = f"TEST-{int(time.time()*1000)}"
        pdf_bytes = generar_pdf_cotizacion_cliente(
            numero_cotizacion=num_cot,
            cliente_nombre="Test Club Deportivo",
            contacto_nombre="Gerente",
            contacto_email_tel="contacto@test.com",
            nicho_nombre="Canchas Deportivas",
            items=items,
            costo_envio_usd=150.0
        )
        self.assertGreater(len(pdf_bytes), 1000)

        cot_id = guardar_cotizacion_sebastian(
            numero_cotizacion=num_cot,
            cliente="Test Club Deportivo",
            contacto="Gerente",
            email_tel="contacto@test.com",
            nicho="Canchas Deportivas",
            fecha_creacion="2026-09-13",
            validez_dias=15,
            items_json=json.dumps(items),
            costo_real_total_usd=1300.0,
            precio_venta_subtotal_usd=2200.0,
            costo_envio_usd=150.0,
            iva_usd=517.0,
            precio_venta_total_iva_usd=2867.0,
            margen_proyecto_pct=40.9,
            comision_sebastian_usd=450.0,
            comision_pct=50.0,
            notas="Prueba unitaria"
        )
        self.assertIsNotNone(cot_id)
        cots = get_cotizaciones_sebastian()
        self.assertTrue(any(c["numero_cotizacion"] == num_cot for c in cots))

    def test_jefe_equipo_code_audit(self):
        reporte = auditar_ecosistema_completo()
        self.assertEqual(reporte["total_errores_sintaxis"], 0)
        self.assertEqual(reporte["total_riesgos_seguridad"], 0)
        self.assertEqual(reporte["dictamen_global"], "SISTEMA_OPTIMO_Y_SEGURO")

if __name__ == "__main__":
    unittest.main()
