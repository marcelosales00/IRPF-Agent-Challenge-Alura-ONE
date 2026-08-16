"""
Organismos (Atomic Design) — Complexos de moléculas e átomos que formam seções completas da interface.

Totalmente adaptativo a Light Mode e Dark Mode.
"""

import streamlit as st
from typing import Tuple, List, Dict, Any, Optional
from ui.molecules import (
    render_source_card,
    render_api_status_molecule,
    render_document_status_molecule
)


def render_hero_banner() -> None:
    """Renderiza o Hero Banner principal no topo da página."""
    st.markdown(
        """
        <div style="background: var(--hero-bg); color: var(--hero-text); padding: 1.8rem 2rem; border-radius: 16px; margin-bottom: 1.5rem; box-shadow: var(--shadow-subtle);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 2.8rem;">🦁</span>
                <div>
                    <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #FFFFFF !important;">Leão IRPF Agent</h1>
                    <p style="margin: 0.3rem 0 0 0; opacity: 0.92; font-size: 0.95rem;">
                        Assistente Virtual Tributário Inteligente para o <b>Imposto de Renda 2026</b>
                    </p>
                </div>
            </div>
            <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.2); font-size: 0.82rem; opacity: 0.88;">
                🔒 Respostas fundamentadas e auditadas com base estrita no guia oficial de Perguntas e Respostas da Receita Federal.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sidebar_organism(current_api_key: str, chunks_count: int) -> Tuple[str, str, bool]:
    """
    Renderiza todo o painel de controle da barra lateral.

    :param current_api_key: Chave API atual no session state.
    :param chunks_count: Total de perguntas indexadas no RAG.
    :return: Tupla com (nova_api_key, modelo_selecionado, botao_limpar_clicado).
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.2rem;">
                <span style="font-size: 1.8rem;">🦁</span>
                <div>
                    <h3 style="margin: 0; font-size: 1.1rem; color: var(--text-primary);">Leão IRPF Agent</h3>
                    <span style="font-size: 0.75rem; color: var(--text-secondary);">Assistente Tributário — IRPF 2026</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # Status do Documento
        st.markdown("<h4 style='font-size: 0.9rem; color: var(--text-primary); margin-bottom: 0.5rem;'>📊 Documento Fonte</h4>", unsafe_allow_html=True)
        render_document_status_molecule(chunks_count)

        st.divider()

        # Configurações de API
        st.markdown("<h4 style='font-size: 0.9rem; color: var(--text-primary); margin-bottom: 0.5rem;'>🔑 Configuração da API</h4>", unsafe_allow_html=True)
        render_api_status_molecule(current_api_key)

        new_api_key = st.text_input(
            "Chave de API do Gemini",
            value=current_api_key,
            type="password",
            help="Sua chave de API do Google Gemini (salva apenas na sessão).",
            placeholder="AIzaSy..."
        )

        selected_model = st.selectbox(
            "Modelo do Gemini",
            options=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"],
            index=0,
            help="Selecione o modelo do Gemini para gerar as respostas."
        )

        st.divider()

        # Controle de Histórico
        clear_clicked = st.button(
            "🗑️ Limpar Conversa",
            use_container_width=True,
            help="Apaga todo o histórico da conversa atual."
        )

        # Rodapé da Sidebar
        st.markdown(
            """
            <div style='text-align: center; color: var(--text-muted); font-size: 0.78rem; margin-top: 2rem; line-height: 1.4;'>
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
    Renderiza o painel superior de botões rápidos categorizados com suporte adaptativo a temas.

    :return: Texto da pergunta selecionada (se algum botão for clicado) ou None.
    """
    st.markdown(
        '<h4 style="font-family: var(--font-title); margin-bottom: 0.8rem; font-size: 1.1rem; color: var(--text-primary);">'
        '💡 Sugestões de Perguntas Rápidas'
        '</h4>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    selected_query = None

    with col1:
        st.markdown(
            """
            <div class="leao-card" style="height: 95px;">
                <div class="leao-card-title">📌 Obrigatoriedade</div>
                <div class="leao-card-body">Quem precisa entregar a declaração em 2026?</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Consultar Obrigatoriedade", key="btn_obrig", use_container_width=True):
            selected_query = "Quem é obrigado a apresentar a declaração do IRPF em 2026?"

    with col2:
        st.markdown(
            """
            <div class="leao-card" style="height: 95px;">
                <div class="leao-card-title">🎓 Dedução de Educação</div>
                <div class="leao-card-body">Quais são as regras e limites para instrução?</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Consultar Educação", key="btn_educ", use_container_width=True):
            selected_query = "Quais são as regras e limites para dedução de despesas com instrução no IRPF?"

    with col3:
        st.markdown(
            """
            <div class="leao-card" style="height: 95px;">
                <div class="leao-card-title">👨‍👩‍👧 Dependentes</div>
                <div class="leao-card-body">Quem pode entrar como dependente na declaração?</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Consultar Dependentes", key="btn_dep", use_container_width=True):
            selected_query = "Quem pode ser considerado dependente na declaração do Imposto de Renda?"

    st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)
    return selected_query


def render_sources_drawer_organism(sources: List[Dict[str, Any]]) -> None:
    """
    Renderiza a gaveta de fontes citadas.

    :param sources: Lista de fontes contendo (number, title, page, relevance).
    """
    if not sources:
        return

    with st.expander("📚 Fontes consultadas no guia oficial da Receita Federal", expanded=False):
        for s in sources:
            render_source_card(
                number=s.get("number", 0),
                title=s.get("title", ""),
                page=s.get("page", 0),
                relevance=s.get("relevance", "Relevante")
            )
