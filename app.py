"""
Interface Principal Streamlit do Leão IRPF Agent.

Fornece uma experiência de chat interativa, intuitiva e reativa para o contribuinte
tirar dúvidas sobre a declaração de Imposto de Renda 2026.
"""

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from core.logger import get_logger
from core.pdf_reader import IRPFDocumentReader
from core.search import SearchEngine
from core.llm import GeminiClient

# Carregar variáveis de ambiente do .env
load_dotenv()

logger = get_logger("app")

# Configuração da página Streamlit
st.set_page_config(
    page_title="Leão IRPF Agent — Assistente IRPF 2026",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Caminho padrão do PDF
PDF_PATH = Path(__file__).parent / "data" / "P&R IRPF 2026.pdf"


@st.cache_resource(show_spinner="📖 Processando e indexando o guia oficial da Receita Federal...")
def load_search_engine() -> SearchEngine:
    """
    Carrega o PDF e indexa os chunks em cache na inicialização.
    """
    logger.info("Carregando motor de busca via st.cache_resource...")
    reader = IRPFDocumentReader(str(PDF_PATH))
    chunks = reader.extract_questions()
    search_engine = SearchEngine(chunks)
    logger.info(f"Motor de busca pronto com {len(chunks)} perguntas indexadas.")
    return search_engine


def main() -> None:
    """Função principal da aplicação Streamlit."""
    
    # Inicializar estado da sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

    # Barra Lateral (Sidebar)
    with st.sidebar:
        st.title("🦁 Leão IRPF Agent")
        st.caption("Assistente Tributário Inteligente — IRPF 2026")
        st.markdown("---")

        st.subheader("🔑 Configuração de API")
        user_key = st.text_input(
            "Chave de API do Gemini",
            value=st.session_state.api_key,
            type="password",
            help="Obtenha sua chave gratuita em https://aistudio.google.com/"
        )
        if user_key != st.session_state.api_key:
            st.session_state.api_key = user_key

        selected_model = st.selectbox(
            "Modelo do Gemini",
            options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"],
            index=0
        )

        st.markdown("---")
        st.subheader("📊 Documento Fonte")
        
        # Carregar motor de busca (cached)
        try:
            search_engine = load_search_engine()
            st.success(f"✅ {len(search_engine.chunks)} perguntas indexadas!")
            st.caption(f"Documento: `P&R IRPF 2026.pdf`")
        except Exception as exc:
            st.error(f"❌ Erro ao carregar o PDF: {exc}")
            logger.error(f"Erro ao carregar search engine no app: {exc}")
            st.stop()

        st.markdown("---")
        if st.button("🧹 Limpar Histórico de Conversa", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown(
            "<div style='text-align: center; color: #6c757d; font-size: 0.8rem; margin-top: 2rem;'>"
            "Desenvolvido para o <b>Challenge Alura Agente</b><br/>"
            "Fonte: Receita Federal do Brasil"
            "</div>",
            unsafe_allow_html=True
        )

    # Painel Principal
    st.title("🦁 Assistente Virtual IRPF 2026")
    st.markdown(
        "Tire suas dúvidas sobre a **Declaração do Imposto de Renda Pessoa Física 2026** "
        "com fundamentação direta no manual oficial de Perguntas e Respostas da Receita Federal."
    )

    # Botões de Perguntas Rápidas por Categoria
    st.markdown("##### 💡 Sugestões de Perguntas Rápidas:")
    col1, col2, col3 = st.columns(3)

    quick_query = None
    with col1:
        if st.button("📌 Quem é obrigado a declarar?", use_container_width=True):
            quick_query = "Quem é obrigado a apresentar a declaração do IRPF em 2026?"
    with col2:
        if st.button("🎓 Regras para dedução de educação", use_container_width=True):
            quick_query = "Quais são as regras e limites para dedução de despesas com instrução?"
    with col3:
        if st.button("👨‍👩‍👧 Quem pode ser dependente?", use_container_width=True):
            quick_query = "Quem pode ser considerado dependente na declaração de imposto de renda?"

    st.markdown("---")

    # Exibir Histórico de Mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📚 Fontes consultadas no guia oficial da Receita Federal"):
                    for src in message["sources"]:
                        st.markdown(
                            f"- **Pergunta {src['number']}** (Pág. {src['page']}) — *{src['title']}* "
                            f"`Relevância: {src['relevance']}`"
                        )

    # Capturar Entrada do Usuário (Chat Input ou Botão Rápido)
    user_input = st.chat_input("Digite sua dúvida sobre o IRPF 2026...")
    prompt = quick_query or user_input

    if prompt:
        logger.info(f"Nova pergunta do usuário recebida: '{prompt}'")

        # Exibir a pergunta do usuário no chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Processamento e Resposta do Assistente
        with st.chat_message("assistant"):
            with st.spinner("🔍 Consultando a legislação e preparando a resposta..."):
                # 1. Recuperar chunks relevantes
                search_results = search_engine.search(prompt, top_k=4)

                # Formatar contexto para o prompt da LLM
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

                # 2. Chamar o modelo Gemini
                llm_client = GeminiClient(api_key=st.session_state.api_key)
                response_text = llm_client.generate(
                    prompt=prompt,
                    context=context_str,
                    history=st.session_state.messages[:-1],
                    model_name=selected_model
                )

                # Exibir a resposta
                st.markdown(response_text)

                # Exibir as fontes consultadas se houver resultados
                if sources_info:
                    with st.expander("📚 Fontes consultadas no guia oficial da Receita Federal"):
                        for src in sources_info:
                            st.markdown(
                                f"- **Pergunta {src['number']}** (Pág. {src['page']}) — *{src['title']}* "
                                f"`Relevância: {src['relevance']}`"
                            )

                # Salvar mensagem e fontes no histórico
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "sources": sources_info
                })


if __name__ == "__main__":
    main()
