"""
Módulo de Organismos (Atomic Design) — Seções completas e complexas da interface.

Combina moléculas e átomos no Hero Banner, Painel de Controle Sidebar,
Cards de Perguntas Rápidas e Gaveta de Fontes da Receita Federal.
"""

import streamlit as st
from typing import Optional, List, Dict, Tuple, Any
from ui.atoms import render_badge
from ui.molecules import (
    render_source_card,
    render_api_status_molecule,
    render_document_status_molecule
)


def render_hero_banner() -> None:
    """Renderiza o cabeçalho Hero principal em estilo Banner Glassmorphism."""
    html = """
    <div class="hero-banner">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
            <span class="atom-badge atom-badge-accent">
                ✨ Challenge Alura Agente
            </span>
            <span class="atom-badge atom-badge-primary" style="background: rgba(255,255,255,0.2); color: #FFF; border: 1px solid rgba(255,255,255,0.3);">
                IRPF 2026 Oficial
            </span>
        </div>
        <h1 class="hero-title">🦁 Leão IRPF Agent</h1>
        <div class="hero-subtitle">
            Assistente tributário inteligente especializado na Declaração do Imposto de Renda Pessoa Física 2026. 
            Respostas fundamentadas e auditadas com base estrita no guia oficial de <b>Perguntas e Respostas da Receita Federal</b>.
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_sidebar_organism(
    current_api_key: str,
    chunks_count: int
) -> Tuple[str, str, bool]:
    """
    Renderiza todo o painel de controle e configurações na barra lateral (Sidebar).

    :param current_api_key: Chave de API atual na sessão.
    :param chunks_count: Quantidade de perguntas do PDF indexadas.
    :return: Tupla (nova_api_key, modelo_selecionado, botao_limpar_clicado).
    """
    with st.sidebar:
        st.markdown(
            '<h2 style="font-family: \'Outfit\', sans-serif; font-size: 1.4rem; color: #0F5132; margin-bottom: 0;">'
            '⚙️ Painel de Controle'
            '</h2>',
            unsafe_allow_html=True
        )
        st.caption("Configurações do Assistente & Modelo LLM")
        st.markdown("---")

        # Status da Conexão
        is_configured = bool(current_api_key and len(current_api_key) > 10)
        render_api_status_molecule(is_configured)

        # Campo da Chave de API
        st.markdown("##### 🔑 Credenciais")
        new_api_key = st.text_input(
            "Chave de API do Gemini",
            value=current_api_key,
            type="password",
            help="Obtenha gratuitamente no Google AI Studio (https://aistudio.google.com/)"
        )

        # Seletor de Modelo Gemini
        st.markdown("##### 🤖 Modelo de Inteligência Artificial")
        selected_model = st.selectbox(
            "Selecione o modelo",
            options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"],
            index=0,
            help="Modelo de linguagem responsável pela síntese das respostas."
        )

        st.markdown("---")
        # Status do Documento PDF
        st.markdown("##### 📚 Base de Conhecimento")
        render_document_status_molecule(chunks_count, "P&R IRPF 2026.pdf")

        st.markdown("---")
        # Ação Global: Limpar Histórico
        clear_clicked = st.button(
            "🧹 Limpar Histórico de Conversa",
            use_container_width=True,
            help="Apaga todo o histórico da conversa atual."
        )

        # Rodapé
        st.markdown(
            """
            <div style='text-align: center; color: #94A3B8; font-size: 0.78rem; margin-top: 2rem; line-height: 1.4;'>
                <b>Leão IRPF Agent v1.0</b><br/>
                Desenvolvido por Marcelo Sales<br/>
                <i>ONE — Oracle Next Education</i>
            </div>
            """,
            unsafe_allow_html=True
        )

    return new_api_key, selected_model, clear_clicked


def render_quick_questions_organism() -> Optional[str]:
    """
    Renderiza o painel superior de botões rápidos categorizados.

    :return: Texto da pergunta selecionada (se algum botão for clicado) ou None.
    """
    st.markdown(
        '<h4 style="font-family: \'Outfit\', sans-serif; margin-bottom: 0.8rem; font-size: 1.1rem; color: #1E293B;">'
        '💡 Sugestões de Perguntas Rápidas'
        '</h4>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    selected_query = None

    with col1:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-card-icon">📌</div>
                <div class="quick-card-title">Obrigatoriedade</div>
                <div class="quick-card-desc">Quem precisa entregar a declaração em 2026?</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Consultar Obrigatoriedade", key="btn_obrig", use_container_width=True):
            selected_query = "Quem é obrigado a apresentar a declaração do IRPF em 2026?"

    with col2:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-card-icon">🎓</div>
                <div class="quick-card-title">Dedução de Educação</div>
                <div class="quick-card-desc">Quais são as regras e limites para instrução?</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Consultar Educação", key="btn_educ", use_container_width=True):
            selected_query = "Quais são as regras e limites para dedução de despesas com instrução?"

    with col3:
        st.markdown(
            """
            <div class="quick-card">
                <div class="quick-card-icon">👨‍👩‍👧</div>
                <div class="quick-card-title">Dependentes</div>
                <div class="quick-card-desc">Quem pode entrar como dependente na declaração?</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Consultar Dependentes", key="btn_dep", use_container_width=True):
            selected_query = "Quem pode ser considerado dependente na declaração de imposto de renda?"

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    return selected_query


def render_sources_drawer_organism(sources: List[Dict[str, Any]]) -> None:
    """
    Renderiza a gaveta/expander de fontes citadas.

    :param sources: Lista de dicionários das fontes recuperadas pela busca RAG.
    """
    if not sources:
        return

    with st.expander(f"📚 Ver {len(sources)} Fontes Consultadas no Guia Oficial da Receita Federal"):
        for src in sources:
            render_source_card(src)
