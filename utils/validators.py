"""
Validatori per input e URL social
"""
import re
from urllib.parse import urlparse
from config import URL_PATTERNS


class URLValidator:
    """Validatore per URL social"""

    @staticmethod
    def is_valid_instagram_url(url):
        """Valida URL Instagram"""
        pattern = URL_PATTERNS['instagram']
        match = re.match(pattern, url)

        if not match:
            return False, "URL Instagram non valido. Formato: https://instagram.com/username"

        # Verifica che non sia un post
        if '/p/' in url or '/reel/' in url or '/tv/' in url:
            return False, "L'URL sembra essere un post, non un profilo"

        return True, match.group(1)  # Restituisce username

    @staticmethod
    def is_valid_tiktok_url(url):
        """Valida URL TikTok"""
        pattern = URL_PATTERNS['tiktok']
        match = re.match(pattern, url)

        if not match:
            return False, "URL TikTok non valido. Formato: https://tiktok.com/@username"

        # Verifica che non sia un video
        if '/video/' in url:
            return False, "L'URL sembra essere un video, non un profilo"

        return True, match.group(1)  # Restituisce username

    @staticmethod
    def is_valid_youtube_url(url):
        """Valida URL YouTube"""
        pattern = URL_PATTERNS['youtube']
        match = re.match(pattern, url)

        if not match:
            return False, "URL YouTube non valido. Formato: https://youtube.com/@channelname o /c/channelname"

        # Verifica che non sia un video
        if '/watch' in url or '/shorts/' in url:
            return False, "L'URL sembra essere un video, non un canale"

        return True, match.group(1)  # Restituisce channel name/id

    @staticmethod
    def validate_social_url(url, social_type):
        """
        Valida URL social generico

        Args:
            url: URL da validare
            social_type: Tipo social ('instagram', 'tiktok', 'youtube')

        Returns:
            (is_valid, error_or_username)
        """
        validators = {
            'instagram': URLValidator.is_valid_instagram_url,
            'tiktok': URLValidator.is_valid_tiktok_url,
            'youtube': URLValidator.is_valid_youtube_url
        }

        if social_type not in validators:
            return False, f"Social type '{social_type}' non supportato"

        return validators[social_type](url)

    @staticmethod
    def extract_username(url, social_type):
        """Estrae username/channel name da URL"""
        is_valid, result = URLValidator.validate_social_url(url, social_type)

        if is_valid:
            return result  # Username/channel name
        return None

    @staticmethod
    def clean_url(url):
        """Pulisce URL rimuovendo parametri query e trailing slash"""
        # Rimuovi parametri query
        url = url.split('?')[0]
        # Rimuovi trailing slash
        url = url.rstrip('/')
        return url


class InputValidator:
    """Validatore per input utente"""

    @staticmethod
    def validate_api_token(token, token_type='apify'):
        """
        Valida formato API token

        Args:
            token: Token da validare
            token_type: Tipo token ('apify' o 'openai')

        Returns:
            (is_valid, error_message)
        """
        if not token or not isinstance(token, str):
            return False, "Token vuoto o non valido"

        token = token.strip()

        if token_type == 'apify':
            # Token Apify inizia con 'apify_api_'
            if not token.startswith('apify_api_'):
                return False, "Token Apify deve iniziare con 'apify_api_'"

            if len(token) < 30:
                return False, "Token Apify troppo corto"

        elif token_type == 'openai':
            # Token OpenAI inizia con 'sk-'
            if not token.startswith('sk-'):
                return False, "Token OpenAI deve iniziare con 'sk-'"

            if len(token) < 40:
                return False, "Token OpenAI troppo corto"

        return True, None

    @staticmethod
    def validate_numeric_input(value, min_value=1, max_value=1000, field_name="Valore"):
        """
        Valida input numerico

        Args:
            value: Valore da validare
            min_value: Valore minimo accettato
            max_value: Valore massimo accettato
            field_name: Nome campo per messaggi errore

        Returns:
            (is_valid, error_or_value)
        """
        try:
            num = int(value)

            if num < min_value:
                return False, f"{field_name} deve essere almeno {min_value}"

            if num > max_value:
                return False, f"{field_name} non può superare {max_value}"

            return True, num

        except (ValueError, TypeError):
            return False, f"{field_name} deve essere un numero valido"

    @staticmethod
    def validate_brand_name(brand_name):
        """Valida nome brand"""
        if not brand_name or not isinstance(brand_name, str):
            return False, "Nome brand vuoto o non valido"

        brand_name = brand_name.strip()

        if len(brand_name) < 2:
            return False, "Nome brand troppo corto (minimo 2 caratteri)"

        if len(brand_name) > 100:
            return False, "Nome brand troppo lungo (massimo 100 caratteri)"

        return True, brand_name

    @staticmethod
    def validate_social_selection(social_list):
        """Valida selezione social"""
        if not social_list or not isinstance(social_list, list):
            return False, "Devi selezionare almeno un social"

        valid_socials = ['instagram', 'tiktok', 'youtube']

        for social in social_list:
            if social not in valid_socials:
                return False, f"Social '{social}' non supportato"

        return True, social_list
