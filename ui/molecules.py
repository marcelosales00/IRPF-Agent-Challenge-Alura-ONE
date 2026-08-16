"""
Moléculas (Atomic Design) — Combinações de átomos em componentes reutilizáveis.

Componentes adaptativos a temas (Light Mode / Dark Mode).
"""

import streamlit as st
from ui.atoms import render_badge


def render_source_card(number: int, title: str, page: int, relevance: str) -> None:
    """
    Renderiza um card de citação de fonte oficial do PDF da Receita Federal.

    :param number: Número oficial da pergunta (ex: 35).
    :param title: Título/pergunta do guia.
    :param page: Número da página no PDF original.
    :param relevance: Rótulo de relevância da busca.
    """
    st.markdown(
        f"""
        <div class="leao-card" style="border-left: 4px solid var(--color-primary);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span class="leao-card-title">📌 Pergunta {number} <small style="color: var(--text-muted); font-weight: normal;">(Página {page})</small></span>
                <span class="leao-badge">{relevance}</span>
            </div>
            <div class="leao-card-body">
                {title}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_api_status_molecule(api_key: str) -> None:
    """Renderiza a molécula de status de configuração da API Key."""
    has_key = bool(api_key.strip())
    status_color = "var(--badge-text)" if has_key else "#EF4444"
    status_bg = "var(--badge-bg)" if has_key else "rgba(239, 68, 68, 0.15)"
    status_text = "Chave API Configurada" if has_key else "Chave API Ausente (Insira abaixo)"
    icon = "✅" if has_key else "⚠️"

    st.markdown(
        f"""
        <div style="padding: 0.6rem 0.8rem; border-radius: 8px; background: {status_bg}; color: {status_color}; border: 1px solid {status_color}; font-size: 0.82rem; font-weight: 500; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.8rem;">
            <span>{icon}</span>
            <span>{status_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_document_status_molecule(chunks_count: int) -> None:
    """Renderiza a molécula de status da base de conhecimento PDF."""
    st.markdown(
        f"""
        <div class="leao-card" style="background: var(--badge-bg); border-color: var(--badge-border); padding: 0.6rem 0.8rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: var(--badge-text); font-weight: 600; font-size: 0.85rem;">
                <span>📖</span>
                <span>{chunks_count} perguntas indexadas!</span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.2rem;">
                Documento oficial: <b>P&R IRPF 2026</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
