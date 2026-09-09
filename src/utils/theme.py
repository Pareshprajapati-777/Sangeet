"""
Theme and UI utilities for Sangeet.
Applies consistent White Glassmorphism styling, branding, and Plotly styling across all pages.
Enforces Light Theme and provides crisp gradient SVGs.
"""

import streamlit as st
from pathlib import Path

# Path to styling assets
ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
CSS_PATH = ASSETS_DIR / "style.css"

# Reusable colorful SVG Icons that never render as black glyphs
import base64

# Raw SVG XML Definitions with Gradients
RAW_SVGS = {
    "music": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_mus" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#4f46e5"/><stop offset="100%" stop-color="#9333ea"/></linearGradient></defs>
        <path d="M9 18V5l12-2v13" stroke="url(#g_mus)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="6" cy="18" r="3" fill="url(#g_mus)"/>
        <circle cx="18" cy="16" r="3" fill="url(#g_mus)"/>
    </svg>""",
    "dashboard": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_dash" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#a855f7"/></linearGradient></defs>
        <path d="M4 19V13M8 19V7M12 19V11M16 19V4M20 19V9" stroke="url(#g_dash)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="8" cy="7" r="2.2" fill="#6366f1"/>
        <circle cx="16" cy="4" r="2.2" fill="#a855f7"/>
    </svg>""",
    "chart": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_ch" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs>
        <rect x="3.5" y="11" width="4" height="9" rx="2" fill="url(#g_ch)"/>
        <rect x="10" y="4" width="4" height="16" rx="2" fill="url(#g_ch)"/>
        <rect x="16.5" y="8" width="4" height="12" rx="2" fill="url(#g_ch)"/>
        <circle cx="5.5" cy="8" r="1.5" fill="#3b82f6"/>
        <circle cx="12" cy="1.5" r="1.5" fill="#6366f1"/>
        <circle cx="18.5" cy="5" r="1.5" fill="#8b5cf6"/>
    </svg>""",
    "database": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_db" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#4f46e5"/></linearGradient></defs>
        <ellipse cx="12" cy="5" rx="9" ry="3" stroke="url(#g_db)" stroke-width="2.2" fill="rgba(6, 182, 212, 0.15)"/>
        <path d="M21 12c0 1.66-4.03 3-9 3s-9-1.34-9-3" stroke="url(#g_db)" stroke-width="2.2"/>
        <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" stroke="url(#g_db)" stroke-width="2.2"/>
        <circle cx="7.5" cy="12" r="1.5" fill="#06b6d4"/>
        <circle cx="7.5" cy="17" r="1.5" fill="#4f46e5"/>
    </svg>""",
    "search": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_srch" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0ea5e9"/><stop offset="100%" stop-color="#6366f1"/></linearGradient></defs>
        <circle cx="11" cy="11" r="7" stroke="url(#g_srch)" stroke-width="2.4"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65" stroke="url(#g_srch)" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M11 8v6M8 11h6" stroke="url(#g_srch)" stroke-width="1.8" stroke-linecap="round"/>
    </svg>""",
    "flask": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_flk" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#f43f5e"/></linearGradient></defs>
        <path d="M9 3h6M10 3v5.5L4.5 17.5C3.8 18.7 4.7 20 6 20h12c1.3 0 2.2-1.3 1.5-2.5L14 8.5V3" stroke="url(#g_flk)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M7 15h10" stroke="url(#g_flk)" stroke-width="1.8" stroke-linecap="round"/>
        <circle cx="10" cy="17" r="1.2" fill="#f59e0b"/>
        <circle cx="14" cy="16.5" r="1.5" fill="#f43f5e"/>
    </svg>""",
    "brain": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_brn" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#ec4899"/></linearGradient></defs>
        <path d="M9.5 2A4.5 4.5 0 0 0 5 6.5c0 .4.05.8.15 1.18A4.5 4.5 0 0 0 3 11.5c0 1.6 1.05 3 2.5 3.5a4.5 4.5 0 0 0 4 6.5c1.4 0 2.65-.65 3.5-1.65.85 1 2.1 1.65 3.5 1.65a4.5 4.5 0 0 0 4-6.5c1.45-.5 2.5-1.9 2.5-3.5a4.5 4.5 0 0 0-2.15-3.82C20.95 7.3 21 6.9 21 6.5A4.5 4.5 0 0 0 14.5 2c-1.05 0-2 .35-2.75.95A4.3 4.3 0 0 0 9.5 2z" stroke="url(#g_brn)" stroke-width="2" stroke-linejoin="round" fill="rgba(139, 92, 246, 0.08)"/>
        <path d="M12 4v16" stroke="url(#g_brn)" stroke-width="1.8" stroke-linecap="round"/>
        <circle cx="8.5" cy="10" r="1.5" fill="#8b5cf6"/>
        <circle cx="15.5" cy="10" r="1.5" fill="#ec4899"/>
        <circle cx="8.5" cy="15" r="1.5" fill="#ec4899"/>
        <circle cx="15.5" cy="15" r="1.5" fill="#8b5cf6"/>
    </svg>""",
    "playlist": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_ply" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ec4899"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs>
        <path d="M9 18V5l12-2v13" stroke="url(#g_ply)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="6" cy="18" r="3" fill="url(#g_ply)"/>
        <circle cx="18" cy="16" r="3" fill="url(#g_ply)"/>
        <line x1="3" y1="6" x2="6" y2="6" stroke="url(#g_ply)" stroke-width="2" stroke-linecap="round"/>
        <line x1="3" y1="10" x2="6" y2="10" stroke="url(#g_ply)" stroke-width="2" stroke-linecap="round"/>
    </svg>""",
    "robot": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_rob" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#ec4899"/></linearGradient></defs>
        <rect x="3" y="11" width="18" height="10" rx="3" stroke="url(#g_rob)" stroke-width="2.2" fill="rgba(99, 102, 241, 0.12)"/>
        <circle cx="12" cy="5" r="2" fill="url(#g_rob)"/>
        <path d="M12 7v4" stroke="url(#g_rob)" stroke-width="2.2" stroke-linecap="round"/>
        <circle cx="8" cy="15" r="1.5" fill="#4f46e5"/>
        <circle cx="16" cy="15" r="1.5" fill="#ec4899"/>
        <line x1="9" y1="18" x2="15" y2="18" stroke="url(#g_rob)" stroke-width="2" stroke-linecap="round"/>
    </svg>""",
    "recommend": """<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none">
        <defs>
            <linearGradient id="g_rec" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#06b6d4"/>
                <stop offset="50%" stop-color="#6366f1"/>
                <stop offset="100%" stop-color="#d946ef"/>
            </linearGradient>
            <linearGradient id="g_star" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#f59e0b"/>
                <stop offset="100%" stop-color="#ec4899"/>
            </linearGradient>
        </defs>
        <circle cx="12" cy="12" r="9" stroke="url(#g_rec)" stroke-width="2" stroke-dasharray="2 2"/>
        <circle cx="12" cy="12" r="5" stroke="url(#g_rec)" stroke-width="2.2" fill="rgba(99, 102, 241, 0.12)"/>
        <circle cx="12" cy="12" r="2" fill="url(#g_rec)"/>
        <path d="M19 4l.6 1.4 1.4.6-1.4.6-.6 1.4-.6-1.4-1.4-.6 1.4-.6z" fill="url(#g_star)"/>
        <path d="M4.5 17.5l.4 1 1 .4-1 .4-.4 1-.4-1-1-.4 1-.4z" fill="url(#g_star)"/>
    </svg>""",
    "studio": """<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none">
        <defs>
            <linearGradient id="g_std" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ec4899"/>
                <stop offset="50%" stop-color="#8b5cf6"/>
                <stop offset="100%" stop-color="#3b82f6"/>
            </linearGradient>
        </defs>
        <path d="M3 12h1M6 8v8M9 4v16M12 7v10M15 9v6M18 5v14M21 12h-1" stroke="url(#g_std)" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="9" cy="4" r="1.5" fill="#ec4899"/>
        <circle cx="18" cy="5" r="1.5" fill="#3b82f6"/>
    </svg>""",
    "mic": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_mic" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#ec4899"/></linearGradient></defs>
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" fill="url(#g_mic)" opacity="0.9"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="url(#g_mic)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="12" y1="19" x2="12" y2="23" stroke="url(#g_mic)" stroke-width="2" stroke-linecap="round"/>
        <line x1="8" y1="23" x2="16" y2="23" stroke="url(#g_mic)" stroke-width="2" stroke-linecap="round"/>
    </svg>""",
    "musicgen": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_mg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ec4899"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient></defs>
        <path d="M2 10v4M6 6v12M10 3v18M14 7v10M18 5v14M22 10v4" stroke="url(#g_mg)" stroke-width="2.4" stroke-linecap="round"/>
        <circle cx="10" cy="3" r="1.5" fill="#ec4899"/>
        <circle cx="18" cy="5" r="1.5" fill="#06b6d4"/>
    </svg>""",
    "palette": """<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none">
        <defs><linearGradient id="g_pal" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#ec4899"/><stop offset="50%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs>
        <path d="M12 2C6.48 2 2 6.48 2 12c0 4.97 3.61 9.07 8.35 9.87.55.09.95-.38.95-.94 0-.32-.13-.6-.35-.82-.67-.67-1.08-1.59-1.08-2.61 0-2.07 1.68-3.75 3.75-3.75h1.75c3.31 0 6-2.69 6-6 0-4.42-4.03-8-9.37-8z" stroke="url(#g_pal)" stroke-width="2" fill="rgba(236, 72, 153, 0.08)"/>
        <circle cx="6.5" cy="11.5" r="1.5" fill="#ec4899"/>
        <circle cx="9.5" cy="7.5" r="1.5" fill="#f59e0b"/>
        <circle cx="14.5" cy="7.5" r="1.5" fill="#8b5cf6"/>
        <circle cx="17.5" cy="11.5" r="1.5" fill="#06b6d4"/>
    </svg>"""
}

def get_svg_icon_html(icon_key: str, size: int = 28) -> str:
    """Encodes SVG into base64 data URI img tag ensuring 100% rendering fidelity."""
    raw_svg = RAW_SVGS.get(icon_key, RAW_SVGS["music"])
    b64 = base64.b64encode(raw_svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}" width="{size}" height="{size}" style="display: block; vertical-align: middle;" alt="{icon_key}" />'

# SVG_ICONS dictionary for backwards compatibility
SVG_ICONS = {k: get_svg_icon_html(k, 28) for k in RAW_SVGS}

def render_hero_banner(icon_key: str, title: str, subtitle: str):
    """
    Renders a unified White Glass hero banner with a colorful gradient SVG badge
    and high-contrast text styling.
    """
    icon_html = get_svg_icon_html(icon_key, 28)
    st.markdown(f"""
        <div class="sangeet-hero">
            <div class="hero-header-row">
                <div class="hero-icon-badge">
                    {icon_html}
                </div>
                <div class="hero-text-col">
                    <h1 class="hero-title-text">{title}</h1>
                    <p class="hero-subtitle">{subtitle}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def apply_sangeet_theme(page_title: str = "Sangeet — Music Intelligence Platform", page_icon: str = "🎵", layout: str = "wide"):
    """
    Applies the unified White Glass theme, locks Light theme in localStorage,
    and sets up gradient SVG branding in the sidebar.
    """
    try:
        st.set_page_config(
            page_title=page_title,
            page_icon=page_icon,
            layout=layout,
            initial_sidebar_state="expanded"
        )
    except Exception:
        pass

    # Inject White Glass CSS & Light-Mode Enforcer Script
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.html(f"""
                <style>{css_content}</style>
                <script>
                    (function() {{
                        try {{
                            localStorage.setItem("stActiveTheme", "Light");
                            localStorage.setItem("stTheme", "Light");
                        }} catch(e) {{}}
                    }})();
                </script>
            """)

    # Render Persistent Frosted Glass Sidebar Branding with Dynamic Shimmer & Icon Animations
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-branding">
                <div class="brand-glow-backdrop"></div>
                <div class="brand-title-wrap">
                    <div class="brand-icon-animated">
                        {get_svg_icon_html('music', 32)}
                        <span class="brand-music-ring"></span>
                    </div>
                    <h2 class="sangeet-animated-title">SANGEET</h2>
                </div>
                <div class="brand-subtitle-badge">
                    <span class="brand-live-pulse"></span>
                    <small>MUSIC INTELLIGENCE PLATFORM</small>
                    <span class="brand-mini-bars">
                        <span></span><span></span><span></span>
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)


def get_glass_plotly_layout(title: str = None) -> dict:
    """Returns standard Plotly layout parameters tailored for the White Glass design."""
    layout = dict(
        template="plotly_white",
        paper_bgcolor="rgba(255, 255, 255, 0.65)",
        plot_bgcolor="rgba(248, 250, 252, 0.75)",
        font=dict(
            family="Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            color="#1e293b",
            size=12.5
        ),
        margin=dict(l=24, r=24, t=48 if title else 24, b=24),
    )
    if title:
        layout["title"] = dict(
            text=f"<b>{title}</b>",
            font=dict(family="Outfit, sans-serif", size=16, color="#0f172a")
        )
    return layout
