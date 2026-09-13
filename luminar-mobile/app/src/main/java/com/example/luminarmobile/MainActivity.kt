package com.example.luminarmobile

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.Bitmap
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import com.example.luminarmobile.theme.LuminarAmber
import com.example.luminarmobile.theme.LuminarBorder
import com.example.luminarmobile.theme.LuminarGreen
import com.example.luminarmobile.theme.LuminarMobileTheme
import com.example.luminarmobile.theme.LuminarMuted
import com.example.luminarmobile.theme.LuminarNavy
import com.example.luminarmobile.theme.LuminarRed
import com.example.luminarmobile.theme.LuminarSky
import com.example.luminarmobile.theme.LuminarSlate
import com.example.luminarmobile.theme.LuminarText

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            LuminarMobileTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = LuminarNavy
                ) {
                    LuminarApp(onFinish = { finish() })
                }
            }
        }
    }
}

private const val PREFS_NAME = "luminar_vpn_prefs"
private const val KEY_SERVER_URL = "server_url"
private const val DEFAULT_SERVER_URL = "http://pon-tu-ip-aqui:8501"

@SuppressLint("SetJavaScriptEnabled")
@Composable
fun LuminarApp(onFinish: () -> Unit) {
    val context = LocalContext.current
    val sharedPrefs = remember { context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE) }

    var serverUrl by remember {
        mutableStateOf(sharedPrefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL)
    }
    var isLoading by remember { mutableStateOf(true) }
    var progress by remember { mutableIntStateOf(0) }
    var hasError by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf("") }
    var showSettingsDialog by remember { mutableStateOf(false) }
    var webViewInstance by remember { mutableStateOf<WebView?>(null) }

    BackHandler(enabled = true) {
        val wv = webViewInstance
        if (wv != null && wv.canGoBack()) {
            wv.goBack()
        } else {
            onFinish()
        }
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        containerColor = LuminarNavy,
        topBar = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(LuminarSlate)
                    .statusBarsPadding()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    // Logo & App Name
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            text = "⚡",
                            fontSize = 18.sp,
                            modifier = Modifier.padding(end = 6.dp)
                        )
                        Column {
                            Text(
                                text = "Luminar B2B",
                                color = LuminarText,
                                fontWeight = FontWeight.Bold,
                                fontSize = 15.sp
                            )
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.clickable { showSettingsDialog = true }
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(7.dp)
                                        .clip(CircleShape)
                                        .background(
                                            when {
                                                hasError -> LuminarRed
                                                isLoading -> LuminarAmber
                                                else -> LuminarGreen
                                            }
                                        )
                                )
                                Spacer(modifier = Modifier.width(5.dp))
                                Text(
                                    text = serverUrl.removePrefix("http://").removePrefix("https://"),
                                    color = LuminarSky,
                                    fontSize = 11.sp,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            }
                        }
                    }

                    // Botones de acción rápida
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        // Botón Recargar
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(LuminarNavy)
                                .border(1.dp, LuminarBorder, RoundedCornerShape(8.dp))
                                .clickable {
                                    hasError = false
                                    webViewInstance?.reload()
                                }
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "Recargar",
                                color = LuminarText,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                        }

                        Spacer(modifier = Modifier.width(8.dp))

                        // Botón Ajustes IP
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(LuminarNavy)
                                .border(1.dp, LuminarBorder, RoundedCornerShape(8.dp))
                                .clickable { showSettingsDialog = true }
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "IP VPN",
                                color = LuminarSky,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }

                // Indicador de progreso
                if (isLoading && !hasError) {
                    LinearProgressIndicator(
                        progress = { progress / 100f },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(2.dp),
                        color = LuminarSky,
                        trackColor = LuminarSlate
                    )
                } else {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(1.dp)
                            .background(LuminarBorder)
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(LuminarNavy)
        ) {
            // Android WebView nativo para alta performance
            AndroidView(
                factory = { ctx ->
                    WebView(ctx).apply {
                        layoutParams = ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            ViewGroup.LayoutParams.MATCH_PARENT
                        )
                        settings.apply {
                            javaScriptEnabled = true
                            domStorageEnabled = true
                            databaseEnabled = true
                            cacheMode = WebSettings.LOAD_DEFAULT
                            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                            useWideViewPort = true
                            loadWithOverviewMode = true
                            setSupportZoom(true)
                            builtInZoomControls = true
                            displayZoomControls = false
                            allowFileAccess = true
                            allowContentAccess = true
                            mediaPlaybackRequiresUserGesture = false
                        }

                        webViewClient = object : WebViewClient() {
                            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                                super.onPageStarted(view, url, favicon)
                                isLoading = true
                                hasError = false
                            }

                            override fun onPageFinished(view: WebView?, url: String?) {
                                super.onPageFinished(view, url)
                                isLoading = false
                            }

                            override fun onReceivedError(
                                view: WebView?,
                                request: WebResourceRequest?,
                                error: WebResourceError?
                            ) {
                                super.onReceivedError(view, request, error)
                                if (request?.isForMainFrame == true) {
                                    hasError = true
                                    errorMessage = error?.description?.toString() ?: "No fue posible conectar con el servidor"
                                }
                            }
                        }

                        webChromeClient = object : WebChromeClient() {
                            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                                super.onProgressChanged(view, newProgress)
                                progress = newProgress
                                isLoading = newProgress < 100
                            }
                        }

                        loadUrl(serverUrl)
                        webViewInstance = this
                    }
                },
                update = { webView ->
                    // Si cambió la URL y no hay error
                    if (webView.url != serverUrl && !hasError) {
                        webView.loadUrl(serverUrl)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )

            // Pantalla de error si la VPN o el servidor no responden
            if (hasError) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(LuminarNavy)
                        .padding(24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = LuminarSlate),
                        shape = RoundedCornerShape(16.dp),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LuminarBorder)
                    ) {
                        Column(
                            modifier = Modifier.padding(20.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "⚠️",
                                fontSize = 40.sp
                            )
                            Spacer(modifier = Modifier.height(10.dp))
                            Text(
                                text = "Sin Conexión con Luminar",
                                color = LuminarText,
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                textAlign = TextAlign.Center
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = errorMessage.ifEmpty { "No se pudo alcanzar el servidor." },
                                color = LuminarRed,
                                fontSize = 12.sp,
                                textAlign = TextAlign.Center
                            )
                            Spacer(modifier = Modifier.height(16.dp))

                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(LuminarNavy, RoundedCornerShape(8.dp))
                                    .border(1.dp, LuminarBorder, RoundedCornerShape(8.dp))
                                    .padding(12.dp)
                            ) {
                                Text(
                                    text = "Pasos para conectar por Tailscale:",
                                    color = LuminarSky,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = "1. Abre Tailscale en este celular y activa la VPN.",
                                    color = LuminarMuted,
                                    fontSize = 11.sp
                                )
                                Text(
                                    text = "2. Ejecuta iniciar_luminar.bat en la PC servidora.",
                                    color = LuminarMuted,
                                    fontSize = 11.sp
                                )
                                Text(
                                    text = "3. Verifica que la IP coincida con tu IP de Tailscale.",
                                    color = LuminarMuted,
                                    fontSize = 11.sp
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = "Destino actual: $serverUrl",
                                    color = LuminarText,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                            }

                            Spacer(modifier = Modifier.height(18.dp))

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                OutlinedButton(
                                    onClick = { showSettingsDialog = true },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.outlinedButtonColors(
                                        contentColor = LuminarSky
                                    ),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, LuminarSky)
                                ) {
                                    Text("Cambiar IP")
                                }

                                Button(
                                    onClick = {
                                        hasError = false
                                        isLoading = true
                                        webViewInstance?.loadUrl(serverUrl)
                                    },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = LuminarSky,
                                        contentColor = LuminarNavy
                                    )
                                ) {
                                    Text("Reintentar", fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Diálogo modal para configurar la IP de Tailscale
    if (showSettingsDialog) {
        var tempUrl by remember { mutableStateOf(serverUrl) }

        AlertDialog(
            onDismissRequest = { showSettingsDialog = false },
            containerColor = LuminarSlate,
            title = {
                Text(
                    text = "Configurar Servidor Luminar",
                    color = LuminarText,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            },
            text = {
                Column {
                    Text(
                        text = "Ingresa la IP de Tailscale de la PC servidora con el puerto 8501:",
                        color = LuminarMuted,
                        fontSize = 13.sp
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    OutlinedTextField(
                        value = tempUrl,
                        onValueChange = { tempUrl = it },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = LuminarText,
                            unfocusedTextColor = LuminarText,
                            focusedBorderColor = LuminarSky,
                            unfocusedBorderColor = LuminarBorder,
                            cursorColor = LuminarSky
                        ),
                        placeholder = {
                            Text("http://pon-tu-ip-aqui:8501", color = LuminarMuted, fontSize = 13.sp)
                        }
                    )

                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = "Ejemplos rápidos:",
                        color = LuminarMuted,
                        fontSize = 11.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(4.dp))
                                .background(LuminarNavy)
                                .border(1.dp, LuminarBorder, RoundedCornerShape(4.dp))
                                .clickable { tempUrl = "http://10.0.2.2:8501" }
                                .padding(horizontal = 6.dp, vertical = 4.dp)
                        ) {
                            Text("Emulador (10.0.2.2)", color = LuminarSky, fontSize = 10.sp)
                        }
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(4.dp))
                                .background(LuminarNavy)
                                .border(1.dp, LuminarBorder, RoundedCornerShape(4.dp))
                                .clickable { tempUrl = "http://localhost:8501" }
                                .padding(horizontal = 6.dp, vertical = 4.dp)
                        ) {
                            Text("Localhost", color = LuminarSky, fontSize = 10.sp)
                        }
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        var cleanedUrl = tempUrl.trim()
                        if (!cleanedUrl.startsWith("http://") && !cleanedUrl.startsWith("https://")) {
                            cleanedUrl = "http://$cleanedUrl"
                        }
                        if (!cleanedUrl.substringAfter("://").contains(":")) {
                            cleanedUrl = "$cleanedUrl:8501"
                        }
                        serverUrl = cleanedUrl
                        sharedPrefs.edit().putString(KEY_SERVER_URL, cleanedUrl).apply()
                        showSettingsDialog = false
                        hasError = false
                        isLoading = true
                        webViewInstance?.loadUrl(cleanedUrl)
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = LuminarSky,
                        contentColor = LuminarNavy
                    )
                ) {
                    Text("Guardar y Conectar", fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showSettingsDialog = false },
                    colors = ButtonDefaults.textButtonColors(contentColor = LuminarMuted)
                ) {
                    Text("Cancelar")
                }
            }
        )
    }
}
