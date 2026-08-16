"""
Módulo de Moléculas (Atomic Design) — Combinação de átomos em unidades funcionais.

Contém renderizadores de cards de citação, status da API/Documento,
balões de chat e pílulas de atalho interativas.
"""

import streamlit as st
from typing import Dict, List, Any
from ui.atoms import render_badge, render_status_dot


def render_source_card(src: Dict[str, Any]) -> None:
    """
    Renderiza um card individual de citação do manual oficial da Receita Federal.

    :param src: Dicionário com número, título, página e relevância.
    """
    number = src.get("number", "000")
    title = src.get("title", "")
    page = src.get("page", 1)
    relevance = src.get("relevance", "Média Relevância")

    badge_variant = "primary" if "Alta" in relevance else "accent"

    html = f"""
    <div class="source-card">
        <div class="source-header">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-weight: 700; color: #0F5132; font-family: 'Outfit', sans-serif;">
                    📌 Pergunta {number}
                </span>
                <span class="source-meta">(Página {page})</span>
            </div>
            {render_badge(relevance, badge_variant)}
        </div>
        <div class="source-title">{title}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_api_status_molecule(is_configured: bool) -> None:
    """Renderiza o estado atual de conexão com a API Gemini na Sidebar."""
    dot = render_status_dot(is_configured)
    status_text = "API Gemini Conectada" if is_configured else "Chave API Não Configurada"
    badge_variant = "primary" if is_configured else "accent"

    html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 0.8rem; background: #F8FAFC; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; font-size: 0.85rem; font-weight: 600;">
            {dot} {status_text}
        </div>
        {render_badge("REST Direct", badge_variant)}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_document_status_molecule(chunks_count: int, filename: str) -> None:
    """Renderiza os metadados do PDF oficial indexado."""
    html = f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 0.9rem 1.1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.4rem;">
            <span style="font-size: 1.2rem;">📄</span>
            <span style="font-weight: 700; font-size: 0.92rem; font-family: 'Outfit', sans-serif;">Guia Oficial IRPF 2026</span>
        </div>
        <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 0.4rem;">
            Arquivo: <code>{filename}</code>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            {render_badge(f"✅ {chunks_count} Perguntas Indexadas", "primary")}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
