"""
Consultor de Ventas y Estrategia B2B - El Estratega (Retórica de Aristóteles)
Traduce los lúmenes, vatios y fotometrías del Ing. David Jiménez Vera
en argumentos de persuasión de alto impacto: Logos (Lógica), Ethos (Autoridad) y Pathos (Emoción).
"""

from typing import Dict, Any, Optional

PROMPT_SISTEMA_ESTRATEGA = """Actúa como un experto en persuasión B2B utilizando la retórica de Aristóteles. Tu función es procesar los datos técnicos de David y aplicar:
1. Logos (Lógica): Usa los datos de ahorro energético y durabilidad de David para demostrar que Luminar es la opción financiera más inteligente.
2. Ethos (Autoridad): Posiciona a David y a Luminar como los únicos expertos homologados capaces de garantizar la seguridad jurídica y técnica.
3. Pathos (Emoción): Conecta la iluminación con el bienestar de los trabajadores, la seguridad ciudadana o el prestigio de la institución. Tu tono es elocuente, persuasivo y estratégico."""

ESTRATEGIAS_NICHO = {
    "municipios": {
        "nombre": "Gobiernos Municipales (Alumbrado Público)",
        "enfoque_david": "Reducción de contaminación lumínica (curvas Full Cutoff), optimización de kWh para aliviar las arcas públicas y cumplimiento IESNA RP-8 / UNIT-ISO.",
        "logos": "Reducción directa del gasto corriente municipal en alumbrado público. Cada peso ahorrado en la factura de energía es un fondo reasignable a obras visibles para el contribuyente.",
        "ethos": "Cumplimiento estricto del pliego y blindaje legal frente al Tribunal de Cuentas. Luminar entrega trazabilidad de laboratorio acreditado, eliminando riesgos de impugnación o fallas prematuras.",
        "pathos": "Seguridad ciudadana y orgullo barrial. Espacios públicos vivos donde las familias transitan con tranquilidad al anochecer. 'Una ciudad bien iluminada es una ciudad que confía en sus líderes'.",
        "pitch_apertura": "Sr. Intendente / Director de Obras: No venimos a venderle lámparas; venimos a convertir avenidas oscuras en corredores de seguridad ciudadana mientras reducimos en más de un 60% el consumo municipal con respaldo técnico certificado.",
        "frase_fuerza": "Una ciudad bien iluminada es una ciudad que confía en sus líderes."
    },
    "industria": {
        "nombre": "Plantas Industriales y Logísticas",
        "enfoque_david": "Estudios de uniformidad (U0 >= 0.60) y control de deslumbramiento (UGR < 22). Certificación de niveles de lux para auditorías de salud ocupacional y prevención de multas.",
        "logos": "Retorno de inversión (Payback) acelerado y eliminación de costos por paradas imprevistas de mantenimiento gracias a drivers con vida útil L80B10 > 50.000 horas.",
        "ethos": "Blindaje normativo total frente a auditorías de la Inspección General del Trabajo. Certificación fotométrica firmada por el Ing. David Jiménez Vera que garantiza el cumplimiento de UNIT 180.",
        "pathos": "Bienestar, agudeza visual y dignidad laboral para los operarios. Cero fatiga visual y reducción radical de la tasa de accidentes en turnos nocturnos. 'Evite multas y aumente el rendimiento de sus operarios mediante una atmósfera de precisión'.",
        "pitch_apertura": "Gerente de Operaciones / Planta: Iluminar con luminarias genéricas cuesta accidentes, bajas laborales y multas del ministerio. Con el estudio fotométrico de Luminar usted blinda la seguridad de sus operarios y recupera la inversión en meses.",
        "frase_fuerza": "Evite multas y aumente el rendimiento de sus operarios mediante una atmósfera de precisión."
    },
    "real_estate": {
        "nombre": "Desarrolladores de Real Estate Corporativo",
        "enfoque_david": "Homologación bajo estándares de eficiencia para créditos LEED / EDGE, protocolos DALI-2 integrables a sistemas BMS inteligentes y curvas arquitectónicas de bajo impacto estético.",
        "logos": "Mayor tasa interna de retorno (TIR) del desarrollo y disminución de gastos comunes (OPEX), incrementando el atractivo financiero para inquilinos corporativos multinacionales.",
        "ethos": "Prestigio institucional respaldado por la firma del Ing. David Jiménez Vera. Luminar posiciona el activo inmobiliario en el escalafón Clase A de Montevideo.",
        "pathos": "Exclusividad, diseño y status. Una atmósfera arquitectónica que transmite solidez, modernidad y compromiso sustentable. 'Luminar no solo ilumina, eleva el valor de mercado de su propiedad'.",
        "pitch_apertura": "Desarrollador / Estudio de Arquitectura: Un edificio corporativo se cotiza por la experiencia que proyecta y su eficiencia energética. Con nuestra prescripción técnica, su proyecto califica a certificaciones sustentables y eleva su valor por metro cuadrado.",
        "frase_fuerza": "Luminar no solo ilumina, eleva el valor de mercado de su propiedad."
    },
    "barrios_privados": {
        "nombre": "Barrios Privados & Urbanizaciones Cerradas",
        "enfoque_david": "Curvas fotométricas asimétricas Bug Rating G0/U0 para cero contaminación lumínica hacia las residencias, temperatura cálida 3000K para integración paisajística y ópticas perimetrales de seguridad continua.",
        "logos": "Bajas expensas comunes gracias a luminarias LED con driver programable dimmable de medianoche. Cero recambio de focos quemados por más de 10 años (L80B10 > 60.000h).",
        "ethos": "Estudio fotométrico que garantiza no encandilar dormitorios ni desvirtuar el masterplan paisajístico, homologado bajo directrices de Dark Sky y normativas residenciales.",
        "pathos": "Tranquilidad, elegancia y vida de comunidad. Los copropietarios e hijos caminan y juegan de noche con total serenidad y distinción visual. 'La seguridad perimetral y la armonía paisajística definen el verdadero valor de su comunidad'.",
        "pitch_apertura": "Comisión de Vecinos / Administrador de Barrio Privado: Un barrio cerrado de categoría no puede tener farolas encandilantes que arruinen la vista nocturna ni zonas en penumbra que generen inseguridad. Les acercamos un proyecto lumínico de alta gama que revaloriza los lotes y baja las expensas.",
        "frase_fuerza": "La seguridad perimetral y la armonía paisajística definen el verdadero valor de su comunidad."
    },
    "canchas_deportivas": {
        "nombre": "Canchas Deportivas & Complejos de Alto Rendimiento (Pádel, Fútbol, Tenis)",
        "enfoque_david": "Estudio lumínico clase I y II (300 - 500 lux promedio en plano horizontal y vertical), uniformidad Uh >= 0.70, proyectores asimétricos anti-deslumbramiento sin efecto estroboscópico (Flicker < 1% para transmisión y video cámara lenta).",
        "logos": "Consumo eléctrico reducido a un tercio frente a proyectores de halogenuro metálico de 400W/1000W. Encendido instantáneo sin esperar 15 minutos de calentamiento, permitiendo alquilar horas pico sin interrupciones.",
        "ethos": "Cumplimiento de las normativas de federaciones deportivas internacionales (FIP, FIFA, ITF) con reporte fotométrico punto a punto firmado por el Ing. David Jiménez Vera.",
        "pathos": "La emoción del juego sin sombras engañosas ni encandilamiento en globos o remates. Los jugadores eligen su complejo porque la visión de la pelota es perfecta. 'El deportista no perdona un punto ciego; juegue con iluminación de nivel profesional'.",
        "pitch_apertura": "Propietario / Director del Complejo Deportivo: Los jugadores eligen canchas donde no queden ciegos al mirar arriba en un remate o saque. Con nuestros proyectores deportivos garantizamos 400+ lux parejos, encendido al instante y un 65% menos en la factura de luz.",
        "frase_fuerza": "El deportista no perdona un punto ciego; juegue con iluminación de nivel profesional."
    },
    "residencias_premium": {
        "nombre": "Residencias Premium & Casas de Arquitectura",
        "enfoque_david": "Índice de reproducción cromática CRI >= 92 para resaltar texturas naturales (maderas, hormigón visto, mármol), ópticas de apertura focalizada (15°, 24°, 38°), control DALI / Casambi para escenas lumínicas y temperatura 2700K / 3000K warm white.",
        "logos": "Inversión durable de libre mantenimiento que protege el mobiliario y las obras de arte al no emitir radiación UV ni infrarroja, con una eficiencia lumínica de más de 120 lm/W.",
        "ethos": "Acompañamiento directo al estudio de arquitectura en la etapa de anteproyecto para integrar perfiles embutidos invisibles y simulación 3D en DIALux.",
        "pathos": "Confort hogareño, calidez emocional y sofisticación. Una casa que abraza al habitante al caer el sol mediante juegos de luces y sombras que destacan la arquitectura. 'La verdadera arquitectura no se mira, se siente a través de su luz'.",
        "pitch_apertura": "Estudio de Arquitectura / Propietario: Diseñaron una obra de autor única; no permitan que una iluminación fría o genérica le quite calidez a los materiales nobles. Integramos luminarias arquitectónicas de alto CRI que realzan cada detalle con la máxima elegancia.",
        "frase_fuerza": "La verdadera arquitectura no se mira, se siente a través de su luz."
    }
}

def construir_estrategia_aristoteles(
    nicho_clave: str,
    dictamen_david: Optional[Dict[str, Any]] = None,
    cliente_nombre: str = "Cliente Corporativo",
    proyecto_descripcion: str = "",
    contexto_comercial: str = ""
) -> Dict[str, Any]:
    """
    Genera el pitch y la estrategia de persuasión B2B estructurada según Aristóteles (Logos, Ethos, Pathos)
    sincronizada con los datos técnicos de David y el contexto comercial del usuario.
    Genera además:
    1. Propuesta formal ejecutiva para Email.
    2. Speech verbal para llamada o reunión presencial.
    """
    nicho_data = ESTRATEGIAS_NICHO.get(nicho_clave.lower(), ESTRATEGIAS_NICHO["industria"])
    
    # Extraer datos de David si están disponibles
    ahorro_usd = "USD 16,000 / año"
    payback = "14 meses"
    kwh_ahorro = "100,000 kWh/año"
    lux_nivel = "300 lux"
    ugr_nivel = "UGR < 22"
    
    if dictamen_david:
        if "roi_energetico" in dictamen_david:
            roi = dictamen_david["roi_energetico"]
            ahorro_usd = f"USD {roi.get('ahorro_dolares_anual', 16000):,} / año"
            payback = f"{roi.get('meses_retorno_roi', 14)} meses"
            kwh_ahorro = f"{roi.get('kwh_ahorro_anual', 100000):,} kWh/año"
        if "estudio_luminico" in dictamen_david:
            est = dictamen_david["estudio_luminico"]
            lux_nivel = f"{est.get('lux_objetivo', 300)} lux"
            ugr_nivel = f"UGR < {est.get('ugr_maximo', 22)}"

    nota_comercial = f"\nObjetivo estratégico informado: {contexto_comercial.strip()}" if contexto_comercial.strip() else ""

    discurso_logos = (
        f"[LOGOS - Racionalidad Financiera]\n"
        f"La inversión se paga sola: {ahorro_usd} en ahorro operativo eléctrico ({kwh_ahorro}), "
        f"con un período de amortización técnica de solo {payback}. Cada dólar invertido en Luminar "
        f"genera un flujo de caja positivo inmediato frente a tecnologías obsoletas o genéricas de baja eficiencia.{nota_comercial}"
    )
    
    discurso_ethos = (
        f"[ETHOS - Autoridad & Seguridad Jurídica]\n"
        f"{nicho_data['ethos']}\n"
        f"El Ing. David Jiménez Vera respalda cada punto de luz con estudios fotométricos goniofotométricos (.IES), "
        f"garantizando {lux_nivel} y {ugr_nivel} bajo ensayos LM-79/80 de laboratorios acreditados, "
        f"brindando inmunidad total ante reclamos técnicos, auditorías de UTE o inspecciones de seguridad laboral."
    )
    
    discurso_pathos = (
        f"[PATHOS - Emoción & Trascendencia]\n"
        f"{nicho_data['pathos']}\n"
        f"No estamos simplemente instalando artefactos de iluminación: estamos construyendo una atmósfera "
        f"que protege vidas, genera confianza y proyecta el liderazgo de su institución."
    )
    
    # 1. Propuesta Formal por Email (Redacción Ejecutiva B2B)
    email_asunto = f"Propuesta de Eficiencia Lumínica y Blindaje Técnico para {cliente_nombre} - Luminar Uruguay"
    email_cuerpo = (
        f"Estimados representantes de {cliente_nombre},\n\n"
        f"Es un placer contactarlos desde la Dirección Comercial y Técnica de Luminar Uruguay.\n\n"
        f"A partir del relevamiento de sus instalaciones y requerimientos técnicos, nuestro Departamento de Ingeniería "
        f"—encabezado por el Ing. David Jiménez Vera— ha emitido un informe preliminar con indicadores concluyentes para su proyecto:\n\n"
        f"• Eficiencia Energética: Proyección de ahorro operativo de {ahorro_usd} ({kwh_ahorro}), con un período de retorno de inversión de apenas {payback}.\n"
        f"• Confort y Seguridad Normativa: Cumplimiento estricto de {lux_nivel} y control anti-deslumbramiento ({ugr_nivel}), respaldado por curvas fotométricas goniofotométricas (.IES) bajo protocolo IES LM-79/LM-80.\n"
        f"• Seguridad Jurídica y Técnica: Certificación de producto para blindar la instalación frente a auditorías y evitar penalizaciones de tarifa reactiva ante UTE.\n\n"
        f"Como sostenemos en nuestra labor cotidiana: \"{nicho_data['frase_fuerza']}\".\n\n"
        f"Nos gustaría poner a su disposición una sesión de 15 minutos (virtual o presencial) con el Ing. David Jiménez Vera "
        f"para acercarles la simulación fotométrica completa y coordinar la entrega de muestras técnicas sin costo.\n\n"
        f"Agradeciendo desde ya su valioso tiempo, quedamos a su entera disposición.\n\n"
        f"Atentamente,\n\n"
        f"Sebastián | Intelligence & Operations B2B\n"
        f"Consultoría Lumínica & Proyectos de Eficiencia\n"
        f"Montevideo, Uruguay"
    )

    # 2. Speech para Llamada Telefónica o Reunión Presencial
    speech_reunion = (
        f"GUION DE LLAMADA O REUNIÓN COMERCIAL ({cliente_nombre.upper()} - {nicho_data['nombre'].upper()}):\n\n"
        f"1. GANCHO DE APERTURA (Primeros 30 segundos):\n"
        f"   \"Hola [Nombre del Interlocutor], gracias por recibirnos. Vengo directo al grano: en Luminar no vendemos simplemente luminarias LED, "
        f"venimos a presentarle un plan donde sus instalaciones ahorran {ahorro_usd} al año y usted blinda la seguridad de su comitente. "
        f"{nicho_data['pitch_apertura']}\"\n\n"
        f"2. ARGUMENTO RACIONAL (Logos - El Negocio):\n"
        f"   \"Mire los números: estamos reemplazando equipos ineficientes por tecnología de alta eficacia lumínica. "
        f"El proyecto se amortiza en {payback}. Cada mes que se posterga la decisión, su institución está perdiendo dinero en la factura eléctrica de UTE.\"\n\n"
        f"3. ARGUMENTO DE AUTORIDAD (Ethos - La Confianza):\n"
        f"   \"En el mercado hay ofertas baratas de importación genérica, pero cuando UTE o la Inspección de Trabajo auditan, no tienen respaldo. "
        f"Nuestro Proyectista Lumínico, el Ing. David Jiménez Vera, entrega el estudio .IES firmado y ensayos de laboratorio acreditado. "
        f"Garantizamos {lux_nivel} y {ugr_nivel}. Con nosotros tienen cero riesgo de impugnaciones o multas.\"\n\n"
        f"4. ARGUMENTO EMOCIONAL (Pathos - La Visión):\n"
        f"   \"{nicho_data['frase_fuerza']}. Sea por la seguridad de los ciudadanos o el bienestar y rendimiento de sus operarios, "
        f"esta obra es la que consolida el prestigio de su gestión.\"\n\n"
        f"5. CIERRE Y LLAMADO A LA ACCIÓN (Next Step):\n"
        f"   \"¿Le parece bien que este jueves el Ing. David Jiménez Vera le presente la memoria técnica en 15 minutos para que la aprueben con su equipo técnico?\""
    )

    pitch_completo = (
        f"PROPUESTA ESTRATÉGICA PARA: {cliente_nombre.upper()}\n"
        f"Segmento: {nicho_data['nombre']}\n"
        f"Lema de Cierre: '{nicho_data['frase_fuerza']}'\n\n"
        f"---\n\n"
        f"1. APERTURA DE ALTO IMPACTO:\n\"{nicho_data['pitch_apertura']}\"\n\n"
        f"2. PILAR LOGOS (Demostración Económica):\n{discurso_logos}\n\n"
        f"3. PILAR ETHOS (Blindaje de Autoridad):\n{discurso_ethos}\n\n"
        f"4. PILAR PATHOS (Conexión Humana & Liderazgo):\n{discurso_pathos}\n\n"
        f"5. CIERRE ESTRATÉGICO:\n"
        f"\"Le proponemos coordinar una reunión de 15 minutos con el Ing. David Jiménez Vera para presentarle el estudio .IES "
        f"personalizado para su infraestructura y validar las cifras de ahorro antes de firmar cualquier pliego.\""
    )

    return {
        "nicho_identificado": nicho_data["nombre"],
        "frase_fuerza": nicho_data["frase_fuerza"],
        "logos": discurso_logos,
        "ethos": discurso_ethos,
        "pathos": discurso_pathos,
        "pitch_apertura": nicho_data["pitch_apertura"],
        "pitch_completo": pitch_completo,
        "propuesta_email": {
            "asunto": email_asunto,
            "cuerpo": email_cuerpo
        },
        "speech_reunion": speech_reunion,
        "prompt_sistema": PROMPT_SISTEMA_ESTRATEGA
    }

if __name__ == "__main__":
    res = construir_estrategia_aristoteles("municipios", cliente_nombre="Intendencia de Canelones")
    print(res["propuesta_email"]["asunto"])
    print(res["speech_reunion"][:200])

