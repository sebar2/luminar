# ⚡ Luminar B2B Operations

Plataforma integral de **Inteligencia y Operaciones Multi-Agente** para el sector B2B y compras públicas en Uruguay. Diseñada bajo una arquitectura híbrida que combina **SaaS Web**, **WebApp de escritorio para notebooks** y una **App Nativa Android (APK)**, todo conectado de forma privada y cifrada mediante **Tailscale Mesh VPN**.

---

## 🏗️ Arquitectura del Sistema

```
                    ┌──────────────────────────────────────────────┐
                    │            PC Servidora (Luminar)            │
                    │   FastAPI (8000)  +   Streamlit (8501)       │
                    │   Multi-Agent Hub +   Base de Datos SQLite   │
                    │         Tailscale IP: 100.x.y.z              │
                    └───────────────────────┬──────────────────────┘
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               │         Tailscale VPN Privada (Cifrado WireGuard)       │
               ▼                                                         ▼
┌──────────────────────────────┐                         ┌──────────────────────────────┐
│       Notebook / Laptop      │                         │     Dispositivo Móvil        │
│   WebApp de Escritorio       │                         │    App Nativa Android (APK)  │
│ Ventana Standalone Chrome/Edge│                         │  Kotlin + Jetpack Compose    │
│  (abrir_luminar_webapp.bat)  │                         │    (Luminar-v1.0.apk)        │
└──────────────────────────────┘                         └──────────────────────────────┘
```

---

## 📦 Módulos y Capacidades

### 1. ⚡ Consola Ejecutiva y Dashboard de Superagente
- Panel de control unificado con métricas en tiempo real de clientes, productos y licitaciones activas.
- Stream de actividad en vivo mostrando la comunicación entre agentes inteligentes.

### 2. 🏛️ Inteligencia de Licitaciones Públicas (ARCE)
- Escaneo y scraping automatizado de llamados y compras estatales en Uruguay.
- Análisis de pliegos técnicos mediante IA para dictaminar viabilidad técnica y márgenes operativos.

### 3. 💼 Estratega Comercial y CRM B2B
- Pipeline de prospectos clasificados por nicho (Supermercados, Hospitales, Hotelería, Industria).
- Generación de estrategias basadas en el modelo *Retórica de Aristóteles* (Ethos, Pathos, Logos).
- Creación de dossiers comerciales personalizados para tomadores de decisiones.

### 4. 💰 Motor Financiero y Generador de Cotizaciones
- Cotización en tiempo real del dólar oficial BROU vía API con contingencia automática.
- Simulación de costos directos, indirectos, fletes y márgenes brutos.
- Exportación instantánea de presupuestos oficiales en formato PDF listos para enviar al cliente.

### 5. 🛡️ Supervisor de Ciberseguridad y Auditoría
- Monitor de puertos de red, latencia de servicios y verificación de integridad de bases de datos.
- Respaldo dinámico en SQLite y auditoría de accesibilidad conforme a estándares WCAG 2.1.

---

## 📂 Estructura del Repositorio

```text
luminar/
├── README.md                     # Documentación principal del ecosistema
├── GUIA_TAILSCALE_Y_APPS.md      # Guía detallada paso a paso de conexión VPN
├── MATRIZ-COMERCIAL.md           # Definición de nichos y propuestas de valor
├── DAVID_JIMENEZ_VERA.md         # Ficha ejecutiva de dirección comercial
│
├── Luminar-v1.0.apk              # 📱 APK Android compilado y listo para instalar
├── compilar_apk.bat              # Script para recompilar el APK en 1 clic
├── abrir_luminar_webapp.bat      # 💻 Lanzador WebApp de escritorio para la notebook
│
├── luminar-saas/                 # 🌐 Plataforma Web (Backend + Frontend)
│   ├── iniciar_luminar.bat       # Lanzador principal del servidor
│   ├── backend/                  # Servidor de Datos y Agentes (FastAPI)
│   │   ├── main.py               # Entrypoint API REST y WebSockets
│   │   ├── database.py           # Conector SQLite y modelos relacionales
│   │   ├── cost_engine.py        # Algoritmos de cálculo de márgenes y costos
│   │   └── services/             # Lógica de agentes (David, Arce, PDF, Seguridad)
│   └── frontend/                 # Interfaz de Usuario (Streamlit)
│       ├── app.py                # Aplicación reactiva de alta performance
│       └── .streamlit/config.toml# Configuración de red (0.0.0.0, CORS, temas)
│
└── luminar-mobile/               # 📱 Proyecto Android Studio (Kotlin + Compose)
    ├── gradlew.bat               # Gradle wrapper
    └── app/                      # Código fuente de la app móvil
        ├── src/main/AndroidManifest.xml
        └── src/main/java/com/example/luminarmobile/
            ├── MainActivity.kt   # WebView nativo, selector de IP VPN y reconexión
            └── theme/            # Paleta de colores oficial Luminar (Navy/Slate)
```

---

## 🚀 Puesta en Marcha

### 1. Iniciar el Servidor en la PC Principal
En la PC donde se alojan los datos:
```cmd
cd luminar-saas
iniciar_luminar.bat
```
Esto levantará:
- **Backend FastAPI:** `http://localhost:8000` (Documentación interactiva en `/docs`)
- **Frontend Streamlit:** `http://localhost:8501` (Aceptando conexiones en `0.0.0.0`)

---

## 🌐 Conexión Remota con Tailscale VPN

Tailscale permite que tu **Notebook** y tu **Celular** se conecten de forma segura a la PC servidora sin abrir puertos en tu router ni exponer tu IP pública:

1. Instala **Tailscale** en tu PC, Notebook y Celular e inicia sesión con la misma cuenta.
2. Copia la IP de Tailscale de tu PC servidora (por ejemplo: `pon tu ip aqui` o `100.x.y.z`).

### 📱 En el Celular (Android APK):
1. Instala en tu celular el archivo `Luminar-v1.0.apk`.
2. Activa la VPN en la app de Tailscale del celular.
3. Abre **Luminar B2B**, toca en **"IP VPN"** e ingresa la dirección:
   ```text
   http://100.x.y.z:8501
   ```
4. Presiona **Guardar y Conectar**. La app recordará la configuración y se conectará automáticamente.

### 💻 En la Notebook (WebApp de Escritorio):
1. Conecta la notebook a Tailscale.
2. Ejecuta el archivo:
   ```cmd
   abrir_luminar_webapp.bat
   ```
3. Ingresa la IP de Tailscale la primera vez. Se abrirá una ventana de aplicación independiente (modo standalone) sin barra de navegador ni pestañas, exactamente como un software nativo.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLite3, ReportLab (PDFs).
- **Frontend Web:** Streamlit, Pandas, Web Components, CSS3 Moderno (WCAG 2.1 AA).
- **App Móvil:** Android SDK 36, Kotlin 2.2, Jetpack Compose, Android WebView con aceleración por hardware.
- **Red y Ciberseguridad:** Tailscale Mesh VPN (WireGuard), cifrado punto a punto.

---

## 👤 Autor
## Licencia / Copyright

Copyright (c) 2026 Sebastián Rodríguez. Todos los derechos reservados.

Este código fuente es propietario. No se permite la copia, descarga, modificación, distribución ni uso de este código sin el permiso explícito por escrito del autor.
