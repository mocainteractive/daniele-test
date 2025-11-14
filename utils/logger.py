"""
Sistema di logging centralizzato con colori brand MOCA
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, STORAGE_DIR
from utils.colors import TerminalColors


class ColoredFormatter(logging.Formatter):
    """Formatter con colori MOCA"""

    COLORS = {
        'DEBUG': TerminalColors.GRAY,
        'INFO': TerminalColors.RESET,
        'WARNING': TerminalColors.LIGHT_RED,
        'ERROR': TerminalColors.RED,
        'CRITICAL': f"{TerminalColors.RED}{TerminalColors.BOLD}"
    }

    def format(self, record):
        # Colora il livello
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{TerminalColors.RESET}"

        # Colora il messaggio per errori
        if record.levelno >= logging.ERROR:
            record.msg = f"{TerminalColors.RED}{record.msg}{TerminalColors.RESET}"

        return super().format(record)


class Logger:
    """Logger centralizzato per l'applicazione"""

    _loggers = {}

    @staticmethod
    def get_logger(name='SocialAnalyzer', log_to_file=True):
        """
        Ottiene logger configurato

        Args:
            name: Nome del logger
            log_to_file: Se True, salva anche su file

        Returns:
            Logger configurato
        """
        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, LOG_LEVEL))

        # Evita duplicati
        if logger.handlers:
            return logger

        # Handler console con colori
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Handler file (opzionale)
        if log_to_file:
            log_dir = STORAGE_DIR / 'logs'
            log_dir.mkdir(exist_ok=True)

            log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        Logger._loggers[name] = logger
        return logger

    @staticmethod
    def log_section(logger, title):
        """Stampa una sezione visiva nel log"""
        separator = "=" * 70
        logger.info(f"\n{TerminalColors.RED}{separator}{TerminalColors.RESET}")
        logger.info(f"{TerminalColors.RED}{title.center(70)}{TerminalColors.RESET}")
        logger.info(f"{TerminalColors.RED}{separator}{TerminalColors.RESET}")

    @staticmethod
    def log_step(logger, step_number, total_steps, description):
        """Stampa uno step del processo"""
        logger.info(f"\n{TerminalColors.RED}[STEP {step_number}/{total_steps}] {description}{TerminalColors.RESET}")

    @staticmethod
    def log_success(logger, message):
        """Stampa un messaggio di successo"""
        logger.info(f"{TerminalColors.RED}✓ {message}{TerminalColors.RESET}")

    @staticmethod
    def log_error(logger, message):
        """Stampa un messaggio di errore"""
        logger.error(f"✗ {message}")

    @staticmethod
    def log_warning(logger, message):
        """Stampa un warning"""
        logger.warning(f"⚠ {message}")


# Istanza globale default
default_logger = Logger.get_logger()
