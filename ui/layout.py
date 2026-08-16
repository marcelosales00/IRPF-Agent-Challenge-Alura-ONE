"""
Módulo de Layout (Atomic Design) — Orquestrador de contêineres e estrutura de página.

Combina os organismos e modelos visuais na estrutura final da aplicação Streamlit.
"""

import streamlit as st
from typing import List, Dict, Any
from ui.atoms import inject_global_styles
from ui.organisms import render_sources_drawer_organism


def setup_page_layout() -> None:
    """Configura a página Streamlit e injeta os estilos visuais globais."""
    st.set_page_config(
        page_title="Leão IRPF Agent — Assistente IRPF 2026",
        page_icon="🦁",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    inject_global_styles()


def render_message_feed(messages: List[Dict[str, Any]]) -> None:
    """
    Renderiza todo o feed de histórico de mensagens no chat com seus respectivos cards de fonte.

    :param messages: Lista de dicionários de mensagens da sessão.
    """
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        sources = msg.get("sources", [])

        avatar = "👤" if role == "user" else "🦁"
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            if sources:
                render_sources_drawer_organism(sources)
