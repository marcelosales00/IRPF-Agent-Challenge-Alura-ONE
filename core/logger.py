"""
Módulo de observabilidade e logging estruturado para o Leão IRPF Agent.

Garante a separação entre logs operacionais gerais (app.log) e logs de exceção (error.log),
além de sanitizar dados sensíveis (como API keys) antes de gravar em disco ou stdout.
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional


LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
APP_LOG_PATH = LOGS_DIR / "app.log"
ERROR_LOG_PATH = LOGS_DIR / "error.log"

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class SensitiveDataFilter(logging.Filter):
    """
    Filtro de segurança que remove ou mascara dados sensíveis (chaves de API Gemini, etc.)
    dos registros de log.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        # Regex para detectar padrões típicos de chave Gemini (ex: AIzaSy...) ou parâmetros de API key
        self.api_key_regex = re.compile(r"(AIzaSy[A-Za-z0-9_-]{33}|key=[A-Za-z0-9_-]+)", re.IGNORECASE)

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.api_key_regex.sub("[CHAVE_OCULTADA]", record.msg)
        return True


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Configura e retorna uma instância do logger com os handlers app.log (INFO+)
    e error.log (ERROR+), além de saída para o console.

    :param name: Nome do módulo que solicita o logger.
    :return: Logger estruturado e sanitizado.
    """
    logger_name = name or "irpf_agent"
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    sensitive_filter = SensitiveDataFilter()

    # Garantir que a pasta logs/ exista
    os.makedirs(LOGS_DIR, exist_ok=True)

    # 1. Handler para logs operacionais gerais (app.log) - Nível INFO+
    try:
        app_handler = logging.FileHandler(APP_LOG_PATH, encoding="utf-8")
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(formatter)
        app_handler.addFilter(sensitive_filter)
        logger.addHandler(app_handler)
    except Exception as exc:
        print(f"[WARN] Não foi possível criar FileHandler para app.log: {exc}")

    # 2. Handler exclusivo para erros e exceções (error.log) - Nível ERROR+
    try:
        error_handler = logging.FileHandler(ERROR_LOG_PATH, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        error_handler.addFilter(sensitive_filter)
        logger.addHandler(error_handler)
    except Exception as exc:
        print(f"[WARN] Não foi possível criar FileHandler para error.log: {exc}")

    # 3. Handler de Console (stdout/stderr) para ambiente Streamlit/OCI
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(sensitive_filter)
    logger.addHandler(console_handler)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    """
    Função utilitária para os módulos registrarem seus loggers.
    """
    return setup_logger(module_name)
