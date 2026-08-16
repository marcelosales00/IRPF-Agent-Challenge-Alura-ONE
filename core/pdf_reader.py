"""
Módulo de extração e estruturação semântica do PDF oficial IRPF 2026.

Utiliza PyMuPDF (fitz) para extrair o texto, aplica correções de encoding
e segmenta o conteúdo em chunks estruturados por pergunta/resposta (QAChunk).
"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF

from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class QAChunk:
    """
    Representação estruturada de uma pergunta e resposta extraída do manual oficial do IRPF.
    """
    number: str        # Ex: "035"
    section: str       # Ex: "TRANSMISSÃO DA DECLARAÇÃO"
    title: str         # Ex: "Quais são os meios para a entrega da declaração?"
    content: str       # Texto completo da resposta
    page: int          # Página inicial no PDF
    keywords: str      # Texto normalizado para busca sem acentos e minúsculo


class IRPFDocumentReader:
    """
    Leitor e parser semântico do documento 'Perguntas e Respostas IRPF 2026'.
    """

    def __init__(self, pdf_path: str) -> None:
        """
        Inicializa o leitor apontando para o arquivo PDF.

        :param pdf_path: Caminho relativo ou absoluto do PDF.
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            error_msg = f"Arquivo PDF não encontrado no caminho: {self.pdf_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"IRPFDocumentReader inicializado para: {self.pdf_path.name}")

    @staticmethod
    def _fix_encoding(text: str) -> str:
        """
        Trata caracteres corrompidos comuns na extração de PDFs com encodings legados.

        :param text: Texto bruto extraído.
        :return: Texto higienizado e corrigido.
        """
        if not text:
            return ""

        # Mapeamento de substituições comuns de ligaturas e mojibake
        replacements = {
            "þ": "",
            "ÿ": "",
            "": "",
            "\x00": "",
            "ﬁ": "fi",
            "ﬂ": "fl",
            "–": "-",
            "—": "-",
            "“": '"',
            "”": '"',
            "’": "'",
            "‘": "'",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Normalizar espaços em branco excessivos preservando quebras de linha limpas
        lines = [line.strip() for line in text.splitlines()]
        cleaned_text = "\n".join([line for line in lines if line])
        return cleaned_text

    @staticmethod
    def _normalize_for_search(text: str) -> str:
        """
        Remove acentuação e converte para minúsculas para indexação de busca.

        :param text: Texto a ser normalizado.
        :return: String sem acentos em lowercase.
        """
        if not text:
            return ""
        nfkd = unicodedata.normalize("NFKD", text)
        no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
        return no_accents.lower()

    def extract_questions(self) -> List[QAChunk]:
        """
        Processa o PDF e extrai a lista completa de perguntas e respostas (QAChunk).

        :return: Lista de QAChunk extraídos do documento.
        """
        logger.info(f"Iniciando extração do PDF: {self.pdf_path}")
        chunks: List[QAChunk] = []

        try:
            doc = fitz.open(str(self.pdf_path))
            total_pages = len(doc)
            logger.info(f"PDF aberto com sucesso. Total de páginas: {total_pages}")

            # Extração de texto página a página acompanhando a seção atual
            current_section = "GERAL"
            full_document_blocks: List[dict] = []

            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                page_text = page.get_text("text")
                cleaned_page = self._fix_encoding(page_text)

                if not cleaned_page:
                    continue

                full_document_blocks.append({
                    "page": page_num + 1,
                    "text": cleaned_page
                })

            doc.close()

            # Regex para identificar início de pergunta no padrão "Pergunta 001 - Título" ou "001 - Título"
            # O manual IRPF usa "001 - ", "Pergunta 001", ou números seguidos de hífen/traço
            question_pattern = re.compile(
                r"^(?:Pergunta\s+)?(\d{3})\s*[-–—]\s*(.+)$",
                re.IGNORECASE | re.MULTILINE
            )
            section_pattern = re.compile(
                r"^(CAPÍTULO|SEÇÃO|CAPITULO|SECAO)\s+[IVXLCDM0-9]+[–—\s\:\-]+(.+)$",
                re.IGNORECASE | re.MULTILINE
            )

            # Reconstruir o texto global mantendo metadados de página
            full_text_accumulator = ""
            page_map = []  # Mapeia deslocamento de caractere para número da página

            for block in full_document_blocks:
                start_idx = len(full_text_accumulator)
                block_text = block["text"] + "\n\n"
                full_text_accumulator += block_text
                end_idx = len(full_text_accumulator)
                page_map.append((start_idx, end_idx, block["page"]))

            # Encontrar todas as ocorrências de perguntas
            matches = list(question_pattern.finditer(full_text_accumulator))
            logger.info(f"Total de ocorrências de perguntas encontradas: {len(matches)}")

            if not matches:
                # Fallback: tentar regex alternativo se o padrão rígido não capturar
                fallback_pattern = re.compile(r"(\d{3})\s*[-–—]\s*(.+)", re.MULTILINE)
                matches = list(fallback_pattern.finditer(full_text_accumulator))
                logger.info(f"Fallback: {len(matches)} ocorrências encontradas com regex alternativo.")

            for i, match in enumerate(matches):
                q_number = match.group(1).zfill(3)
                q_title = match.group(2).strip()

                start_pos = match.start()
                end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(full_text_accumulator)

                q_content = full_text_accumulator[start_pos:end_pos].strip()

                # Identificar número da página correspondente ao início da pergunta
                page_found = 1
                for p_start, p_end, p_num in page_map:
                    if p_start <= start_pos < p_end:
                        page_found = p_num
                        break

                # Tentar identificar seção no contexto anterior ao match
                before_text = full_text_accumulator[max(0, start_pos - 1000):start_pos]
                sec_match = section_pattern.findall(before_text)
                if sec_match:
                    current_section = sec_match[-1][1].strip()

                # Construir o texto de busca normalizado
                search_text = f"pergunta {q_number} {q_title} {q_content} {current_section}"
                keywords = self._normalize_for_search(search_text)

                chunk = QAChunk(
                    number=q_number,
                    section=current_section,
                    title=q_title,
                    content=q_content,
                    page=page_found,
                    keywords=keywords
                )
                chunks.append(chunk)

            logger.info(f"Extração concluída com sucesso. Total de QAChunks criados: {len(chunks)}")
            return chunks

        except Exception as exc:
            logger.error(f"Erro grave durante a extração do PDF: {exc}", exc_info=True)
            raise exc
