from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    bg_primary: str = "#0a0a0f"
    bg_secondary: str = "#12121a"
    bg_card: str = "rgba(255, 255, 255, 0.03)"
    bg_card_hover: str = "rgba(255, 255, 255, 0.05)"

    accent: str = "#00e676"
    accent_dim: str = "rgba(0, 230, 118, 0.1)"
    accent_glow: str = "rgba(0, 230, 118, 0.3)"

    blue: str = "#00b0ff"
    blue_dim: str = "rgba(0, 176, 255, 0.1)"

    purple: str = "#9c27b0"
    purple_dim: str = "rgba(156, 39, 176, 0.08)"

    warning: str = "#ffd600"
    warning_dim: str = "rgba(255, 214, 0, 0.1)"

    danger: str = "#ff1744"
    danger_dim: str = "rgba(255, 23, 68, 0.1)"

    text_primary: str = "rgba(255, 255, 255, 0.92)"
    text_secondary: str = "rgba(255, 255, 255, 0.65)"
    text_tertiary: str = "rgba(255, 255, 255, 0.4)"
    text_muted: str = "rgba(255, 255, 255, 0.25)"

    border: str = "rgba(255, 255, 255, 0.06)"
    border_hover: str = "rgba(255, 255, 255, 0.12)"
    border_accent: str = "rgba(0, 230, 118, 0.2)"

    gradient_primary: str = "linear-gradient(135deg, #00e676 0%, #00b0ff 100%)"
    gradient_full: str = "linear-gradient(135deg, #00e676 0%, #00b0ff 50%, #9c27b0 100%)"

    font_family: str = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
    font_mono: str = "'JetBrains Mono', 'Fira Code', monospace"

    radius_sm: str = "6px"
    radius_md: str = "10px"
    radius_lg: str = "16px"
    radius_xl: str = "20px"
    radius_full: str = "9999px"

    shadow_sm: str = "0 2px 8px rgba(0,0,0,0.2)"
    shadow_md: str = "0 4px 16px rgba(0,0,0,0.25)"
    shadow_lg: str = "0 8px 32px rgba(0,0,0,0.3)"
    shadow_accent: str = "0 4px 20px rgba(0,230,118,0.15)"
    shadow_glow: str = "0 0 20px rgba(0,230,118,0.08)"

    transition_fast: str = "all 0.15s ease"
    transition: str = "all 0.25s ease"
    transition_slow: str = "all 0.35s ease"


T = Theme()
