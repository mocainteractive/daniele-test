"""
Configurazione centralizzata per Social Brand Analyzer
"""
import os
from pathlib import Path

# ============================================================================
# BRAND COLORS (MOCA)
# ============================================================================
BRAND_COLORS = {
    'primary_red': '#E52217',
    'light_red': '#FFE7E6',
    'black': '#191919',
    'gray': '#8A8A8A',
    'white': '#FFFFFF'
}

# ============================================================================
# PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / 'storage'
RESULTS_DIR = STORAGE_DIR / 'results'
EXPORTS_DIR = STORAGE_DIR / 'exports'
TEMPLATES_DIR = BASE_DIR / 'views' / 'templates'

# Crea cartelle se non esistono
STORAGE_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# APIFY ACTORS
# ============================================================================
APIFY_ACTORS = {
    'instagram': 'apify/instagram-scraper',
    'tiktok': 'clockworks/tiktok-scraper',
    'tiktok_comments': 'clockworks/tiktok-comments-scraper',
    'youtube': 'streamers/youtube-scraper',
    'youtube_comments': 'streamers/youtube-comments-scraper',
    'google_search': 'apify/google-search-scraper',
    'web_browser': 'apify/rag-web-browser'
}

# ============================================================================
# SCRAPING DEFAULTS
# ============================================================================
DEFAULT_MAX_POSTS = 10
DEFAULT_MAX_COMMENTS = 50
DEFAULT_SCRAPING_TIMEOUT = 300  # 5 minuti
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # secondi

# ============================================================================
# AI ANALYSIS
# ============================================================================
OPENAI_MODEL = 'gpt-4o-mini'  # Modello economico e veloce
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.3  # Più deterministico

# Lingue supportate per analisi
SUPPORTED_LANGUAGES = ['it', 'en']

# Stopwords italiane custom
ITALIAN_STOPWORDS = [
    'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra',
    'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una',
    'del', 'dello', 'della', 'dei', 'degli', 'delle',
    'al', 'allo', 'alla', 'ai', 'agli', 'alle',
    'dal', 'dallo', 'dalla', 'dai', 'dagli', 'dalle',
    'nel', 'nello', 'nella', 'nei', 'negli', 'nelle',
    'sul', 'sullo', 'sulla', 'sui', 'sugli', 'sulle',
    'e', 'è', 'che', 'non', 'mi', 'ti', 'si', 'ci', 'vi',
    'anche', 'come', 'ma', 'o', 'se', 'sono', 'hanno', 'ha',
    'questo', 'questa', 'questi', 'queste', 'quello', 'quella',
    'molto', 'più', 'mai', 'poi', 'però', 'quindi', 'dove'
]

# ============================================================================
# WORDCLOUD
# ============================================================================
WORDCLOUD_CONFIG = {
    'width': 1200,
    'height': 600,
    'background_color': 'white',
    'colormap': 'Reds',  # Tema rosso MOCA
    'max_words': 100,
    'min_font_size': 10,
    'relative_scaling': 0.5,
    'prefer_horizontal': 0.7
}

# ============================================================================
# EXPORT SETTINGS
# ============================================================================
PDF_CONFIG = {
    'page_size': 'A4',
    'margin_top': 50,
    'margin_bottom': 50,
    'margin_left': 50,
    'margin_right': 50,
    'font_family': 'Helvetica',
    'title_size': 24,
    'heading_size': 16,
    'body_size': 10
}

CSV_ENCODING = 'utf-8-sig'  # Per compatibilità Excel
XLSX_ENGINE = 'openpyxl'

# ============================================================================
# DASHBOARD SETTINGS
# ============================================================================
STREAMLIT_CONFIG = {
    'page_title': 'MOCA Social Brand Analyzer',
    'page_icon': '🎯',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Favicon URL
MOCA_FAVICON_URL = 'https://mocainteractive.com/wp-content/uploads/2025/04/cropped-moca-instagram-icona-1-192x192.png'

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# RATE LIMITING
# ============================================================================
# Pause tra richieste per evitare rate limiting
RATE_LIMIT_DELAY = {
    'instagram': 2,
    'tiktok': 3,
    'youtube': 2,
    'google_search': 1
}

# ============================================================================
# VALIDATION PATTERNS
# ============================================================================
URL_PATTERNS = {
    'instagram': r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9._]+)/?',
    'tiktok': r'https?://(?:www\.)?tiktok\.com/@([a-zA-Z0-9._]+)/?',
    'youtube': r'https?://(?:www\.)?youtube\.com/(?:@|c/|channel/|user/)([a-zA-Z0-9_-]+)/?'
}

# ============================================================================
# METRICS CALCULATION
# ============================================================================
# Formula engagement rate
def calculate_engagement_rate(likes, comments, shares, views):
    """Calcola engagement rate standardizzato"""
    if views == 0:
        return 0
    return ((likes + comments + shares) / views) * 100

# Soglie performance
PERFORMANCE_THRESHOLDS = {
    'low': 1.0,      # < 1% engagement
    'medium': 3.0,   # 1-3% engagement
    'high': 5.0,     # 3-5% engagement
    'excellent': 5.0 # > 5% engagement
}
