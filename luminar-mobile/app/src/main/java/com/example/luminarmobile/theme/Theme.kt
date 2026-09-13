package com.example.luminarmobile.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = LuminarSky,
    secondary = LuminarSlate,
    tertiary = LuminarGreen,
    background = LuminarNavy,
    surface = LuminarSlate,
    onPrimary = LuminarNavy,
    onSecondary = LuminarText,
    onTertiary = LuminarNavy,
    onBackground = LuminarText,
    onSurface = LuminarText
)

@Composable
fun LuminarMobileTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography,
        content = content
    )
}
