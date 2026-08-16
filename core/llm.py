"""
Cliente de integração com a API Google Gemini via requisições REST diretas.

Não utiliza SDKs pesados nem LangChain. Implementa retry, fallback de modelos
e enforça o System Prompt tributário do Leão IRPF Agent.
"""

import os
import json
import requests
from typing import List, Dict, Optional
from core.logger import get_logger

logger = get_logger(__name__)

# Modelos suportados pela API REST do Gemini em ordem de prioridade
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash"
]

# System Prompt oficial do Leão Digital
SYSTEM_INSTRUCTION = """Você é o Leão Digital, um assistente tributário especialista e empático focado na Declaração do Imposto de Renda Pessoa Física (IRPF 2026).

Suas diretrizes fundamentais:
1. Responda EXCLUSIVAMENTE com base nas perguntas e respostas fornecidas no CONTEXTO OFICIAL abaixo.
2. CITE SEMPRE o número da pergunta oficial da Receita Federal (ex: "Conforme a Pergunta 001...") correspondente de onde extraiu a resposta.
3. Se a dúvida do usuário NÃO puder ser respondida com base no contexto fornecido, declare claramente que não possui essa informação no guia oficial e oriente a consultar o portal da Receita Federal.
4. NUNCA invente alíquotas, prazos, limites de isenção ou regras tributárias. Informação tributária incorreta gera prejuízo ao contribuinte.
5. Use linguagem clara, objetiva, acessível e bem formatada em Markdown (use tópicos e negritos quando apropriado)."""


class GeminiClient:
    """
    Cliente HTTP REST nativo para comunicação com a API do Google Gemini.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Inicializa o cliente obtendo a API key dos parâmetros ou das variáveis de ambiente.

        :param api_key: Chave da API Gemini. Se omitido, busca de GEMINI_API_KEY.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            logger.warning("GeminiClient inicializado sem GEMINI_API_KEY.")

    def is_configured(self) -> bool:
        """Verifica se há uma chave de API válida configurada."""
        return bool(self.api_key and len(self.api_key) > 10)

    def generate(
        self,
        prompt: str,
        context: str,
        history: Optional[List[Dict[str, str]]] = None,
        model_name: Optional[str] = None
    ) -> str:
        """
        Gera uma resposta fundamentada utilizando a API REST do Gemini.

        :param prompt: Pergunta do usuário.
        :param context: Contexto tributário extraído do PDF pela busca.
        :param history: Histórico de mensagens anteriores (opcional).
        :param model_name: Nome do modelo específico (opcional).
        :return: Texto da resposta gerada.
        """
        if not self.is_configured():
            error_msg = "Chave de API do Gemini não configurada. Informe uma GEMINI_API_KEY válida."
            logger.error(error_msg)
            return "⚠️ **Erro de Configuração:** Nenhuma chave de API do Gemini foi fornecida. Por favor, insira uma API Key na barra lateral."

        models_to_try = [model_name] if model_name else AVAILABLE_MODELS

        full_prompt = (
            f"--- CONTEXTO OFICIAL DO MANUAL IRPF 2026 ---\n"
            f"{context}\n"
            f"--- FIM DO CONTEXTO ---\n\n"
            f"PERGUNTA DO CONTRIBUINTE: {prompt}"
        )

        contents = []

        # Adicionar histórico se houver
        if history:
            for msg in history:
                role = "user" if msg.get("role") == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.get("content", "")}]
                })

        # Adicionar a pergunta atual com o contexto
        contents.append({
            "role": "user",
            "parts": [{"text": full_prompt}]
        })

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 2048
            }
        }

        headers = {"Content-Type": "application/json"}

        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            logger.info(f"Enviando requisição REST para a API Gemini (Modelo: {model})...")

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            generated_text = parts[0].get("text", "").strip()
                            logger.info(f"Resposta recebida com sucesso do modelo {model} ({len(generated_text)} caracteres).")
                            return generated_text

                    logger.warning(f"Resposta vazia ou sem candidatos do modelo {model}.")
                
                logger.warning(f"Falha na resposta do modelo {model}. Status HTTP: {response.status_code}. Resposta: {response.text[:200]}")

            except requests.exceptions.RequestException as exc:
                logger.error(f"Erro de conexão/timeout ao chamar o modelo {model}: {exc}")

        # Se todos os modelos falharem
        fallback_msg = (
            "⚠️ Não foi possível obter uma resposta do serviço da IA no momento. "
            "Por favor, verifique se a chave de API fornecida é válida e se possui cota disponível."
        )
        logger.error("Todos os modelos de LLM configurados falharam em responder.")
        return fallback_msg
