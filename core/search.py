"""
Motor de busca semântico e por relevância para o IRPF Agent.

Indexa os QAChunks extraídos e calcula o score de relevância para perguntas
do usuário com base em correspondência de termos, match de números e boosting tributário.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import List
from core.pdf_reader import QAChunk
from core.logger import get_logger

logger = get_logger(__name__)


# Palavras-chave do domínio tributário que recebem pontuação extra (boosting)
TAX_BOOST_KEYWORDS = {
    "obrigatoriedade", "obrigado", "declarar", "declaracao", "isencao", "isento",
    "deducao", "deducoes", "dependente", "dependentes", "saude", "educacao",
    "instrucao", "prazo", "transmissao", "restituicao", "malha", "fina",
    "rendimento", "rendimentos", "tributavel", "tributaveis", "aluguel",
    "imovel", "imoveis", "veiculo", "veiculos", "acoes", "bolsa", "cripto"
}

# Stopwords comuns em português a serem ignoradas na contagem individual
PORTUGUESE_STOPWORDS = {
    "a", "ao", "aos", "aquela", "aqueles", "aquilo", "as", "ate", "com", "como",
    "da", "das", "de", "dela", "delas", "dele", "deles", "depois", "do", "dos",
    "e", "ela", "elas", "ele", "eles", "em", "entre", "era", "eram", "essa",
    "essas", "esse", "esses", "esta", "estadas", "estava", "este", "estes",
    "eu", "foi", "fomos", "ha", "isso", "isto", "ja", "lhe", "lhes", "mais",
    "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na",
    "nas", "nem", "no", "nos", "nossa", "nossas", "nosso", "nossos", "num",
    "numa", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por",
    "qual", "quando", "que", "quem", "se", "sem", "ser", "seu", "seus", "sua",
    "suas", "tambem", "te", "tem", "temos", "ter", "tinha", "um", "uma", "você"
}


@dataclass
class SearchResult:
    """
    Resultado de uma consulta contendo o chunk correspondente e a pontuação calculada.
    """
    chunk: QAChunk
    score: float

    @property
    def relevance_label(self) -> str:
        """Retorna uma classificação amigável da relevância."""
        if self.score >= 15.0:
            return "Alta Relevância"
        elif self.score >= 7.0:
            return "Média Relevância"
        return "Baixa Relevância"


class SearchEngine:
    """
    Motor de busca leve em memória para recuperação dos chunks mais relevantes do IRPF.
    """

    def __init__(self, chunks: List[QAChunk]) -> None:
        """
        Inicializa o motor de busca com a lista de chunks extraídos.

        :param chunks: Lista de QAChunk.
        """
        self.chunks = chunks
        logger.info(f"SearchEngine inicializado com {len(self.chunks)} chunks indexados.")

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Remove acentos, pontuação e converte para minúsculas.
        """
        if not text:
            return ""
        nfkd = unicodedata.normalize("NFKD", text)
        no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
        cleaned = re.sub(r"[^\w\s]", " ", no_accents)
        return cleaned.lower().strip()

    def _calculate_score(self, query_norm: str, query_words: List[str], chunk: QAChunk) -> float:
        """
        Calcula a pontuação de relevância de um chunk para a query.
        """
        score = 0.0
        chunk_keywords = chunk.keywords

        # 1. Match direto pelo número da pergunta (ex: "pergunta 035" ou "035")
        number_match = re.search(r"\b(\d{1,3})\b", query_norm)
        if number_match:
            searched_num = number_match.group(1).zfill(3)
            if chunk.number == searched_num:
                score += 25.0  # Match direto no número da pergunta

        # 2. Match exato da query completa no conteúdo ou título
        if query_norm in self._normalize(chunk.title):
            score += 10.0
        elif query_norm in chunk_keywords:
            score += 5.0

        # 3. Match de palavras-chave individuais relevantes
        meaningful_words = [w for w in query_words if w not in PORTUGUESE_STOPWORDS and len(w) > 2]
        if not meaningful_words:
            meaningful_words = query_words

        matches_count = 0
        for word in meaningful_words:
            if word in chunk_keywords:
                matches_count += 1
                base_word_score = 1.5 + (len(word) * 0.1)
                
                # Boosting se a palavra for um termo tributário relevante
                if word in TAX_BOOST_KEYWORDS:
                    base_word_score += 2.5
                
                # Bônus extra se a palavra estiver no título da pergunta
                if word in self._normalize(chunk.title):
                    base_word_score += 2.0

                score += base_word_score

        # 4. Bônus pela proporção de palavras (Overlap Ratio)
        if meaningful_words:
            overlap_ratio = matches_count / len(meaningful_words)
            score += overlap_ratio * 4.0

        return score

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Executa a busca e retorna os top_k chunks mais relevantes.

        :param query: Pergunta do usuário.
        :param top_k: Quantidade máxima de resultados a retornar.
        :return: Lista de SearchResult ordenada por score decrescente.
        """
        if not query or not query.strip():
            logger.warning("Query de busca vazia recebida.")
            return []

        query_norm = self._normalize(query)
        query_words = query_norm.split()

        logger.info(f"Executando busca para query: '{query}' (normalizada: '{query_norm}')")

        results: List[SearchResult] = []
        for chunk in self.chunks:
            score = self._calculate_score(query_norm, query_words, chunk)
            if score > 0.5:
                results.append(SearchResult(chunk=chunk, score=score))

        # Ordenar por score decrescente
        results.sort(key=lambda x: x.score, reverse=True)
        top_results = results[:top_k]

        logger.info(f"Busca finalizada. Encontrados {len(results)} resultados. Retornando top {len(top_results)}.")
        for idx, res in enumerate(top_results, 1):
            logger.info(f"  Result #{idx}: Pergunta {res.chunk.number} (Score: {res.score:.2f}) - {res.chunk.title[:50]}...")

        return top_results
