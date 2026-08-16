"""
Módulo de Átomos (Atomic Design) — Tokens visuais, CSS global e elementos indivisíveis.

Define a paleta HSL, tipografia Google Fonts (Outfit + Inter), componentes glassmorphism
e efeitos de micro-interação.
"""

import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
    --font-heading: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    
    --brand-primary: HSL(155, 65%, 22%);
    --brand-primary-hover: HSL(155, 65%, 18%);
    --brand-primary-light: HSL(155, 50%, 95%);
    --brand-primary-border: HSL(155, 40%, 82%);
    
    --brand-accent: HSL(38, 92%, 50%);
    --brand-accent-light: HSL(38, 90%, 95%);
    --brand-accent-border: HSL(38, 80%, 80%);
    
    --bg-main: HSL(210, 20%, 98%);
    --bg-glass: rgba(255, 255, 255, 0.88);
    --bg-card: #FFFFFF;
    
    --text-main: HSL(222, 47%, 11%);
    --text-muted: HSL(215, 16%, 47%);
    --text-light: HSL(215, 16%, 65%);
    
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
    --shadow-card: 0 8px 24px -4px rgba(15, 23, 42, 0.06);
    --shadow-hover: 0 12px 32px -4px rgba(15, 81, 50, 0.15);
    
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}

/* Reset Global de Tipografia */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    color: var(--text-main) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-heading) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* Fundo Principal da Aplicação */
.stApp {
    background-color: var(--bg-main) !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(15, 81, 50, 0.05) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(217, 119, 6, 0.04) 0px, transparent 50%);
}

/* Estilização Premium da Barra Lateral (Sidebar) */
[data-testid="stSidebar"] {
    background-color: var(--bg-glass) !important;
    backdrop-filter: blur(16px) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.06) !important;
}

/* Hero Banner Customizado */
.hero-banner {
    background: linear-gradient(135deg, HSL(155, 65%, 20%) 0%, HSL(155, 75%, 14%) 100%);
    border-radius: var(--radius-lg);
    padding: 2.2rem 2.5rem;
    color: #FFFFFF;
    box-shadow: var(--shadow-card);
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-banner::after {
    content: "🦁";
    position: absolute;
    right: -10px;
    bottom: -20px;
    font-size: 8.5rem;
    opacity: 0.12;
    pointer-events: none;
}

.hero-title {
    font-family: var(--font-heading);
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    color: #FFFFFF !important;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: rgba(255, 255, 255, 0.88);
    margin-top: 0.5rem;
    max-width: 680px;
    line-height: 1.5;
}

/* Badges Atômicos */
.atom-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: var(--font-body);
}

.atom-badge-primary {
    background-color: var(--brand-primary-light);
    color: var(--brand-primary);
    border: 1px solid var(--brand-primary-border);
}

.atom-badge-accent {
    background-color: var(--brand-accent-light);
    color: var(--brand-accent);
    border: 1px solid var(--brand-accent-border);
}

.atom-badge-neutral {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

/* Pílulas de Ação Rápida (Quick Action Cards) */
.quick-card {
    background: var(--bg-card);
    border: 1px solid #E2E8F0;
    border-radius: var(--radius-md);
    padding: 1.1rem 1.2rem;
    transition: all 0.25s ease-in-out;
    box-shadow: var(--shadow-sm);
    height: 100%;
    cursor: pointer;
}

.quick-card:hover {
    border-color: var(--brand-primary);
    transform: translateY(-3px);
    box-shadow: var(--shadow-hover);
}

.quick-card-icon {
    font-size: 1.5rem;
    margin-bottom: 0.4rem;
}

.quick-card-title {
    font-family: var(--font-heading);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 0.2rem;
}

.quick-card-desc {
    font-size: 0.82rem;
    color: var(--text-muted);
    line-height: 1.3;
}

/* Cards de Citação de Fontes */
.source-card {
    background-color: #F8FAFC;
    border-left: 4px solid var(--brand-primary);
    border-radius: var(--radius-sm);
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.6rem;
    transition: background 0.2s ease;
}

.source-card:hover {
    background-color: #F1F5F9;
}

.source-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.3rem;
}

.source-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-main);
}

.source-meta {
    font-size: 0.8rem;
    color: var(--text-muted);
}

/* Botões do Streamlit Customizados */
div.stButton > button {
    border-radius: var(--radius-md) !important;
    font-family: var(--font-heading) !important;
    font-weight: 600 !important;
    transition: all 0.2s ease-in-out !important;
}

div.stButton > button:hover {
    border-color: var(--brand-primary) !important;
    color: var(--brand-primary) !important;
}
</style>
"""


def inject_global_styles() -> None:
    """Injeta os estilos CSS globais do Atomic Design na aplicação."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_badge(label: str, variant: str = "primary") -> str:
    """
    Retorna o HTML formatado de um badge atômico.

    :param label: Texto do badge.
    :param variant: 'primary', 'accent' ou 'neutral'.
    """
    return f'<span class="atom-badge atom-badge-{variant}">{label}</span>'


def render_status_dot(is_active: bool) -> str:
    """Retorna o indicador visual de status ativo/inativo."""
    color = "#10B981" if is_active else "#EF4444"
    return f'<span style="height: 10px; width: 10px; background-color: {color}; border-radius: 50%; display: inline-block; margin-right: 6px;"></span>'
