"""
Gestione colori brand MOCA per terminal e dashboard
"""
from config import BRAND_COLORS


class TerminalColors:
    """Colori ANSI per output terminale"""
    RED = '\033[91m'
    LIGHT_RED = '\033[38;2;255;231;230m'
    BLACK = '\033[38;2;25;25;25m'
    GRAY = '\033[38;2;138;138;138m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def red(text):
        """Testo rosso"""
        return f"{TerminalColors.RED}{text}{TerminalColors.RESET}"

    @staticmethod
    def gray(text):
        """Testo grigio"""
        return f"{TerminalColors.GRAY}{text}{TerminalColors.RESET}"

    @staticmethod
    def bold(text):
        """Testo bold"""
        return f"{TerminalColors.BOLD}{text}{TerminalColors.RESET}"


class DashboardColors:
    """Colori esadecimali per dashboard e grafici"""
    PRIMARY = BRAND_COLORS['primary_red']
    LIGHT = BRAND_COLORS['light_red']
    DARK = BRAND_COLORS['black']
    GRAY = BRAND_COLORS['gray']
    WHITE = BRAND_COLORS['white']

    # Palette per grafici (variazioni di rosso)
    CHART_PALETTE = [
        '#E52217',  # Rosso primario
        '#FF4444',  # Rosso chiaro
        '#CC1100',  # Rosso scuro
        '#FF6B6B',  # Rosso pastello
        '#8A0000',  # Rosso molto scuro
    ]

    # Colori sentiment
    SENTIMENT_POSITIVE = '#4CAF50'  # Verde
    SENTIMENT_NEUTRAL = BRAND_COLORS['gray']
    SENTIMENT_NEGATIVE = BRAND_COLORS['primary_red']

    @staticmethod
    def get_gradient(n_colors=5):
        """Genera gradiente di rossi"""
        if n_colors <= len(DashboardColors.CHART_PALETTE):
            return DashboardColors.CHART_PALETTE[:n_colors]
        return DashboardColors.CHART_PALETTE * (n_colors // len(DashboardColors.CHART_PALETTE) + 1)


# Alias per retrocompatibilità con codice esistente
Colors = TerminalColors
