"""
Leão IRPF Agent — Entrypoint Principal.

Orquestra a integração entre a camada visual Atomic Design (ui/)
e os módulos de regras de negócio RAG / LLM (core/).
"""

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from core.logger import get_logger
from core.pdf_reader import IRPFDocumentReader
from core.search import SearchEngine
from core.llm import GeminiClient

from ui.layout import setup_page_layout, render_message_feed
from ui.organisms import (
    render_hero_banner,
    render_sidebar_organism,
    render_quick_questions_organism,
    render_sources_drawer_organism
)

# Carregar variáveis de ambiente
load_dotenv()
logger = get_logger("app")

# Caminho oficial do PDF
PDF_PATH = Path(__file__).parent / "data" / "P&R IRPF 2026.pdf"


@st.cache_resource(show_spinner="📖 Processando e indexando o guia oficial da Receita Federal...")
def load_search_engine() -> SearchEngine:
    """Carrega e indexa o PDF oficial uma única vez na inicialização."""
    logger.info("Inicializando SearchEngine via st.cache_resource...")
    reader = IRPFDocumentReader(str(PDF_PATH))
    chunks = reader.extract_questions()
    engine = SearchEngine(chunks)
    logger.info(f"SearchEngine pronto com {len(chunks)} perguntas indexadas.")
    return engine


def main() -> None:
    """Orquestrador principal da aplicação."""
    # 1. Configurar Layout e Estilos Globais
    setup_page_layout()

    # 2. Inicializar Estado da Sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

    # 3. Carregar Backend RAG (cached)
    try:
        search_engine = load_search_engine()
        chunks_count = len(search_engine.chunks)
    except Exception as exc:
        st.error(f"❌ Erro ao carregar a base de conhecimento PDF: {exc}")
        logger.error(f"Falha ao carregar search engine: {exc}", exc_info=True)
        st.stop()

    # 4. Renderizar Barra Lateral (Sidebar Organism)
    new_api_key, selected_model, clear_clicked = render_sidebar_organism(
        current_api_key=st.session_state.api_key,
        chunks_count=chunks_count
    )

    if new_api_key != st.session_state.api_key:
        st.session_state.api_key = new_api_key
        st.rerun()

    if clear_clicked:
        st.session_state.messages = []
        st.rerun()

    # 5. Renderizar Hero Header e Sugestões Rápidas (Main Organisms)
    render_hero_banner()
    quick_query = render_quick_questions_organism()

    # 6. Renderizar Histórico de Conversas
    render_message_feed(st.session_state.messages)

    # 7. Capturar Nova Entrada (Chat Input ou Botão Rápido)
    user_input = st.chat_input("Digite sua dúvida sobre o Imposto de Renda 2026...")
    prompt = quick_query or user_input

    if prompt:
        logger.info(f"Nova pergunta submetida: '{prompt}'")

        # Adicionar pergunta do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Processar busca RAG e chamada ao Gemini
        with st.chat_message("assistant", avatar="🦁"):
            with st.spinner("🔍 Consultando a legislação e preparando a resposta..."):
                # Busca semântica dos top-4 chunks
                search_results = search_engine.search(prompt, top_k=4)

                context_parts = []
                sources_info = []

                for res in search_results:
                    c = res.chunk
                    context_parts.append(
                        f"[PERGUNTA OFICIAL {c.number} - SEÇÃO: {c.section}]\n"
                        f"TÍTULO: {c.title}\n"
                        f"CONTEÚDO:\n{c.content}\n"
                    )
                    sources_info.append({
                        "number": c.number,
                        "title": c.title,
                        "page": c.page,
                        "relevance": res.relevance_label
                    })

                context_str = "\n\n".join(context_parts)

                # Chamada REST ao cliente Gemini
                llm_client = GeminiClient(api_key=st.session_state.api_key)
                response_text = llm_client.generate(
                    prompt=prompt,
                    context=context_str,
                    history=st.session_state.messages[:-1],
                    model_name=selected_model
                )

                # Exibir resposta e gaveta de fontes
                st.markdown(response_text)
                if sources_info:
                    render_sources_drawer_organism(sources_info)

                # Salvar mensagem no histórico
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "sources": sources_info
                })


if __name__ == "__main__":
    main()
