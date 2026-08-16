"""
Átomos (Atomic Design) — Tokens de design, tipografia, estilos CSS e componentes atômicos.

Suporta modo claro (Light Mode) e modo escuro (Dark Mode) de forma nativa e adaptativa.
"""

import streamlit as st


def inject_global_styles() -> None:
    """Injeta estilos CSS globais com suporte adaptativo a Light Mode e Dark Mode."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&display=swap');

        /* 🎨 TOKENS DE CORES ADAPTATIVOS (PADRÃO LIGHT MODE) */
        :root {
            --font-title: 'Outfit', sans-serif;
            --font-body: 'Inter', sans-serif;

            --color-primary: #0F5132;
            --color-accent: #D97706;

            --bg-card: rgba(248, 250, 252, 0.85);
            --border-card: #E2E8F0;
            --text-primary: #1E293B;
            --text-secondary: #64748B;
            --text-muted: #94A3B8;

            --hero-bg: linear-gradient(135deg, #0F5132 0%, #198754 100%);
            --hero-text: #FFFFFF;

            --badge-bg: #E6F4EA;
            --badge-text: #0F5132;
            --badge-border: #A3E0B5;

            --shadow-subtle: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        /* 🌙 SUPORTE ADAPTATIVO A DARK MODE */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-card: rgba(30, 41, 59, 0.85);
                --border-card: #334155;
                --text-primary: #F8FAFC;
                --text-secondary: #CBD5E1;
                --text-muted: #94A3B8;

                --hero-bg: linear-gradient(135deg, #0B3D26 0%, #0F5132 100%);
                --hero-text: #FFFFFF;

                --badge-bg: rgba(15, 81, 50, 0.4);
                --badge-text: #6EE7B7;
                --badge-border: #10B981;

                --shadow-subtle: 0 4px 12px rgba(0, 0, 0, 0.3);
            }
        }

        /* 🌙 SUPORTE AO SELECTOR DO STREAMLIT DARK THEME */
        [data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"] {
            --bg-card: rgba(30, 41, 59, 0.85);
            --border-card: #334155;
            --text-primary: #F8FAFC;
            --text-secondary: #CBD5E1;
            --text-muted: #94A3B8;

            --hero-bg: linear-gradient(135deg, #0B3D26 0%, #0F5132 100%);
            --hero-text: #FFFFFF;

            --badge-bg: rgba(15, 81, 50, 0.4);
            --badge-text: #6EE7B7;
            --badge-border: #10B981;

            --shadow-subtle: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        /* TIPOGRAFIA GLOBAL */
        html, body, [class*="css"], .stMarkdown {
            font-family: var(--font-body) !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-title) !important;
        }

        /* CARD ADAPTATIVO ATÔMICO */
        .leao-card {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            box-shadow: var(--shadow-subtle);
            backdrop-filter: blur(8px);
            transition: all 0.2s ease-in-out;
        }

        .leao-card-title {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
        }

        .leao-card-body {
            color: var(--text-secondary);
            font-size: 0.85rem;
            line-height: 1.4;
        }

        .leao-text-primary {
            color: var(--text-primary) !important;
        }

        .leao-text-secondary {
            color: var(--text-secondary) !important;
        }

        .leao-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            background-color: var(--badge-bg);
            color: var(--badge-text);
            border: 1px solid var(--badge-border);
        }

        .stButton button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_badge(text: str, icon: str = "📌") -> None:
    """Renderiza um badge atômico com suporte adaptativo a temas."""
    st.markdown(
        f"""
        <span class="leao-badge">
            <span>{icon}</span>
            <span>{text}</span>
        </span>
        """,
        unsafe_allow_html=True
    )


def render_status_dot(is_active: bool = True, label: str = "Online") -> None:
    """Renderiza um indicador visual de status (online/offline)."""
    color = "#10B981" if is_active else "#EF4444"
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; color: var(--text-secondary);">
            <span style="height: 8px; width: 8px; background-color: {color}; border-radius: 50%; display: inline-block;"></span>
            <span>{label}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
