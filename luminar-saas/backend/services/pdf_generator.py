# -*- coding: utf-8 -*-
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generar_pdf_cotizacion_cliente(
    numero_cotizacion: str,
    cliente_nombre: str,
    contacto_nombre: str,
    contacto_email_tel: str,
    nicho_nombre: str,
    items: List[Dict[str, Any]],
    costo_envio_usd: float,
    moneda: str = "USD",
    tipo_cambio_brou: float = 41.50,
    cliente_rut: str = "",
    validez_dias: int = 15,
    notas_comerciales: str = "",
    terminos_entrega: str = "Inmediata para stock plaza Montevideo / 10-14 dias aereo / 45 dias maritimo",
    garantia: str = "3 a 5 anos de garantia oficial con reposicion directa y certificacion fotometrica LM-79/LM-80"
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0F172A")
    c_secondary = colors.HexColor("#2563EB")
    c_slate = colors.HexColor("#475569")
    c_light_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=c_primary
    )
    meta_style = ParagraphStyle(
        'DocMeta', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=c_slate
    )
    meta_bold = ParagraphStyle(
        'DocMetaBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=c_primary
    )
    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.white, alignment=TA_CENTER
    )
    table_cell_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10.5, textColor=c_primary
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=c_primary
    )
    table_cell_right = ParagraphStyle(
        'TableCellRight', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10.5, textColor=c_primary, alignment=TA_RIGHT
    )
    table_cell_right_bold = ParagraphStyle(
        'TableCellRightBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=c_primary, alignment=TA_RIGHT
    )
    terms_style = ParagraphStyle(
        'TermsText', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=c_slate
    )

    elements = []

    curr_sym = "USD $" if moneda.upper() == "USD" else "$ UYU "
    ref_tc = f"<br/><font size=7.5 color='#64748B'>Tipo Cambio BROU: 1 USD = {tipo_cambio_brou:.2f} UYU</font>" if moneda.upper() == "UYU" else ""

    header_data = [
        [
            Paragraph("<b>INTELLIGENCE &amp; OPERATIONS</b><br/><font size=9 color='#2563EB'>PROYECTOS &amp; INGENIERIA LUMINICA B2B</font><br/><font size=8 color='#64748B'>Montevideo, Uruguay | Presupuesto Tecnico Homologado</font>", title_style),
            Paragraph(f"<b>PRESUPUESTO FORMAL ({moneda})</b><br/><font size=9 color='#0F172A'><b>Nro:</b> {numero_cotizacion}</font><br/><font size=8 color='#475569'><b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}<br/><b>Validez:</b> {validez_dias} dias corridos{ref_tc}</font>", meta_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[3.8 * inch, 3.2 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=2, spaceAfter=8))

    rut_display = f"<br/><font size=8 color='#2563EB'><b>RUT:</b> {cliente_rut}</font>" if cliente_rut.strip() else ""
    cliente_info_data = [
        [
            Paragraph("<b>CLIENTE / EMPRESA:</b>", meta_bold),
            Paragraph(f"{cliente_nombre}{rut_display}", meta_style),
            Paragraph("<b>SEGMENTO / PROYECTO:</b>", meta_bold),
            Paragraph(nicho_nombre, meta_style)
        ],
        [
            Paragraph("<b>ATENCION / CONTACTO:</b>", meta_bold),
            Paragraph(contacto_nombre if contacto_nombre else "Direccion de Obras / Compras", meta_style),
            Paragraph("<b>CONTACTO / EMAIL:</b>", meta_bold),
            Paragraph(contacto_email_tel if contacto_email_tel else "En archivo comercial", meta_style)
        ]
    ]
    cliente_table = Table(cliente_info_data, colWidths=[1.5 * inch, 2.2 * inch, 1.6 * inch, 1.7 * inch])
    cliente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 10))

    headers = [
        Paragraph("Item / SKU", table_header_style),
        Paragraph("Descripcion Tecnica y Especificacion", table_header_style),
        Paragraph("Cant.", table_header_style),
        Paragraph(f"P. Unit ({moneda})", table_header_style),
        Paragraph(f"Subtotal ({moneda})", table_header_style)
    ]
    
    rows = [headers]
    subtotal_productos = 0.0

    for idx, it in enumerate(items, 1):
        cant = int(it.get("cantidad", 1))
        # Si la cotización se emite en UYU, convertir o tomar precio en UYU
        if moneda.upper() == "UYU":
            p_unit = float(it.get("precio_venta_unitario_uyu", float(it.get("precio_venta_unitario_usd", 0.0)) * tipo_cambio_brou))
        else:
            p_unit = float(it.get("precio_venta_unitario_usd", 0.0))

        sub_it = cant * p_unit
        subtotal_productos += sub_it

        desc_p = f"<b>{it.get('descripcion', it.get('sku', ''))}</b>"
        if it.get("especificaciones"):
            desc_p += f"<br/><font size=7 color='#64748B'>{it['especificaciones']}</font>"

        row = [
            Paragraph(f"<b>{idx}.</b> {it.get('sku', '')}", table_cell_bold),
            Paragraph(desc_p, table_cell_style),
            Paragraph(str(cant), table_cell_style),
            Paragraph(f"{curr_sym}{p_unit:,.2f}", table_cell_right),
            Paragraph(f"{curr_sym}{sub_it:,.2f}", table_cell_right_bold)
        ]
        rows.append(row)

    items_table = Table(rows, colWidths=[1.1 * inch, 3.3 * inch, 0.6 * inch, 1.0 * inch, 1.0 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 8))

    flete_monto = float(costo_envio_usd) if moneda.upper() == "USD" else float(costo_envio_usd) * tipo_cambio_brou
    subtotal_con_envio = subtotal_productos + flete_monto
    iva_calculado = subtotal_con_envio * 0.22
    total_general_iva = subtotal_con_envio + iva_calculado

    totales_data = [
        [
            "", "",
            Paragraph(f"Subtotal Equipamiento Lumínico ({moneda}):", table_cell_right),
            Paragraph(f"{curr_sym}{subtotal_productos:,.2f}", table_cell_right)
        ],
        [
            "", "",
            Paragraph(f"Envío, Flete y Logística en Obra ({moneda}):", table_cell_right),
            Paragraph(f"{curr_sym}{flete_monto:,.2f}", table_cell_right)
        ],
        [
            "", "",
            Paragraph(f"<b>Subtotal Gravado ({moneda}):</b>", table_cell_right),
            Paragraph(f"<b>{curr_sym}{subtotal_con_envio:,.2f}</b>", table_cell_right_bold)
        ],
        [
            "", "",
            Paragraph("IVA (22% Uruguay):", table_cell_right),
            Paragraph(f"{curr_sym}{iva_calculado:,.2f}", table_cell_right)
        ],
        [
            "", "",
            Paragraph(f"<font size=9.5 color='#0F172A'><b>TOTAL FINAL ({moneda} - IVA INC.):</b></font>", table_cell_right),
            Paragraph(f"<font size=10.5 color='#2563EB'><b>{curr_sym}{total_general_iva:,.2f}</b></font>", table_cell_right_bold)
        ]
    ]

    totales_table = Table(totales_data, colWidths=[2.0 * inch, 2.0 * inch, 1.8 * inch, 1.2 * inch])
    totales_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (2, 2), (3, 2), 0.5, c_border),
        ('LINEABOVE', (2, 4), (3, 4), 1.5, c_primary),
        ('BACKGROUND', (2, 4), (3, 4), c_light_bg),
    ]))
    elements.append(totales_table)
    elements.append(Spacer(1, 10))

    nota_mon = f"Valores en Pesos Uruguayos ($ UYU) a tipo de cambio BROU {tipo_cambio_brou:.2f} UYU/USD." if moneda.upper() == "UYU" else "Valores expresados en Dólares Estadounidenses (USD)."
    terminos_box = [
        [
            Paragraph("<b>CONDICIONES COMERCIALES Y LOGISTICA DE ENTREGA:</b>", meta_bold)
        ],
        [
            Paragraph(
                f"• <b>Forma de Pago:</b> Transferencia bancaria en {moneda}. Anticipo de inicio y saldo contra entrega / avance convenido.<br/>"
                f"• <b>Plazo y Logistica:</b> {terminos_entrega}. Entrega coordinada en obra.<br/>"
                f"• <b>Garantia Oficial:</b> {garantia}.<br/>"
                f"• <b>Respaldo de Ingenieria:</b> Incluye memoria de calculo luminico fotometrico (.IES) y trazabilidad de laboratorio para respaldo de pliego y auditorias.<br/>"
                f"• <b>Observaciones:</b> {nota_mon} {notas_comerciales if notas_comerciales else 'Mantiene precios durante el periodo de validez.'}",
                terms_style
            )
        ]
    ]
    terminos_table = Table(terminos_box, colWidths=[7.0 * inch])
    terminos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    elements.append(terminos_table)
    elements.append(Spacer(1, 14))

    firma_data = [
        [
            Paragraph("<b>Emitido por:</b><br/><b>Sebastian</b><br/>Intelligence &amp; Operations B2B<br/><font size=7.5 color='#64748B'>Consultoria Luminica &amp; Proyectos</font>", meta_style),
            Paragraph("<b>Aprobacion Tecnica:</b><br/><b>Ing. David Jimenez Vera</b><br/>Ingenieria Electrica &amp; Fotometria<br/><font size=7.5 color='#64748B'>Homologacion IESNA / UNIT-ISO</font>", meta_style),
            Paragraph("<b>Conformidad del Cliente:</b><br/><br/>____________________________<br/><font size=7.5 color='#64748B'>Firma, Aclaracion y Rut / Fecha</font>", meta_style)
        ]
    ]
    firma_table = Table(firma_data, colWidths=[2.3 * inch, 2.3 * inch, 2.4 * inch])
    firma_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(KeepTogether(firma_table))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
