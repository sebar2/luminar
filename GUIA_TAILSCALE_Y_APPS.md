# 🚀 Guía de Conexión: Tailscale VPN, APK Móvil y WebApp de Escritorio

Esta guía detalla paso a paso cómo usar **Luminar B2B Operations** de forma 100% segura y privada tanto desde tu **celular Android** como desde tu **notebook**, comunicándose con tu PC servidora a través de **Tailscale VPN**.

---

## 1. ¿Cómo funciona la arquitectura con Tailscale?

Tailscale crea una red privada (VPN punto a punto o "mesh") encriptada mediante WireGuard.
- No necesitas abrir puertos en tu router (port forwarding).
- No expones tu IP pública ni tus servicios a internet.
- Cada dispositivo recibe una IP privada fija dentro de Tailscale (rango `100.x.y.z`).

---

## 2. Preparación de la PC Servidora (donde corre Luminar)

1. **Abrir Tailscale en la PC:**
   - Asegúrate de que la aplicación Tailscale esté iniciada y conectada.
   - Haz clic en el icono de Tailscale (en la barra de tareas de Windows) y copia tu **IP de Tailscale** (ejemplo: `pon tu ip aqui` o `100.x.y.z`).
2. **Iniciar Luminar:**
   - Ejecuta: `luminar\luminar-saas\iniciar_luminar.bat`.
   - Ahora Streamlit y FastAPI escuchan en `0.0.0.0`, por lo que aceptan conexiones desde Tailscale.

---

## 3. Uso en el Celular Android (Instalación del APK)

El APK nativo ya está compilado y listo para instalar en:
📂 `luminar/Luminar-v1.0.apk`

### Pasos de instalación:
1. **Pasar el APK al celular:**
   - Puedes enviártelo por WhatsApp Web, subirlo a Google Drive, o conectando el celular por USB.
2. **Instalar el APK:**
   - Abre el archivo `Luminar-v1.0.apk` en tu celular. Si Android te pide permisos para "Instalar aplicaciones desconocidas", concédeselos.
3. **Conectar Tailscale en el celular:**
   - Descarga e instala **Tailscale** desde Google Play Store en el celular.
   - Inicia sesión con la misma cuenta que en tu PC y activa la conexión VPN.
4. **Abrir Luminar B2B:**
   - Al abrir la app, toca el botón **"IP VPN"** arriba a la derecha (o en la pantalla de reconexión si no conecta automáticamente).
   - Escribe la IP de Tailscale de tu PC: `http://100.x.y.z:8501`.
   - Presiona **"Guardar y Conectar"**.
   - ¡Listo! La app se conectará de inmediato a tu servidor con WebView acelerado por hardware, modo oscuro nativo y botón de recarga.

---

## 4. Uso en la Notebook (Modo WebApp de Escritorio)

Tienes dos formas de usarlo en la notebook:

### Opción A: Mediante el lanzador directo (Recomendado)
1. Conecta la notebook a Tailscale con tu cuenta.
2. Copia la carpeta `luminar` o el archivo `abrir_luminar_webapp.bat` a tu notebook.
3. Haz doble clic en `abrir_luminar_webapp.bat`.
   - La primera vez te pedirá la IP de Tailscale de la PC servidora (`100.x.y.z`).
   - Se abrirá automáticamente en Google Chrome o Microsoft Edge en **modo aplicación independiente** (sin pestañas, sin barra de URL, con su propio icono en la barra de tareas).

### Opción B: Instalación nativa desde el navegador (PWA)
1. Abre Google Chrome o Microsoft Edge en la notebook.
2. Navega a `http://100.x.y.z:8501`.
3. En la barra de direcciones o en el menú de los 3 puntos:
   - En Edge: Haz clic en el icono de la barra de direcciones o Menú `...` > **Aplicaciones** > **Instalar Luminar B2B**.
   - En Chrome: Haz clic en Menú `...` > **Guardar y compartir** > **Instalar página como aplicación**.
4. Se creará un acceso directo en tu escritorio y menú inicio de Windows como cualquier programa nativo.

---

## 5. Resumen de Archivos Clave

| Archivo | Función |
| :--- | :--- |
| `Luminar-v1.0.apk` | Archivo APK instalable para tu celular Android |
| `abrir_luminar_webapp.bat` | Lanzador de escritorio para notebook (ventana limpia sin navegador) |
| `compilar_apk.bat` | Recompila el APK en 1 clic si haces cambios en el código Android |
| `iniciar_luminar.bat` | Inicia Backend FastAPI y Frontend Streamlit configurado para Tailscale |
| `luminar-mobile/` | Código fuente completo del proyecto Android (Kotlin + Jetpack Compose) |
