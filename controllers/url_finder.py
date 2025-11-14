"""
Controller per auto-discovery URL social tramite Google Search
"""
from apify_client import ApifyClient
import re
import time
from config import APIFY_ACTORS, URL_PATTERNS, RATE_LIMIT_DELAY
from utils.logger import Logger
from utils.validators import URLValidator


class URLFinder:
    """Trova automaticamente URL social di un brand"""

    def __init__(self, apify_token, logger=None):
        """
        Inizializza URL Finder

        Args:
            apify_token: Token API Apify
            logger: Logger opzionale
        """
        self.client = ApifyClient(apify_token)
        self.logger = logger or Logger.get_logger(self.__class__.__name__)

    def find_social_urls(self, brand_name, social_types):
        """
        Trova URL social per un brand

        Args:
            brand_name: Nome brand
            social_types: Lista social da cercare ['instagram', 'tiktok', 'youtube']

        Returns:
            Dict {social_type: [url1, url2, ...]}
        """
        self.logger.info(f"Ricerca URL social per: {brand_name}")

        results = {}

        for social_type in social_types:
            self.logger.info(f"  Cercando su {social_type.capitalize()}...")

            urls = self._search_social_urls(brand_name, social_type)
            results[social_type] = urls

            if urls:
                self.logger.info(f"    ✓ Trovati {len(urls)} URL")
            else:
                self.logger.warning(f"    ✗ Nessun URL trovato")

            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY.get('google_search', 1))

        return results

    def _search_social_urls(self, brand_name, social_type):
        """
        Cerca URL per uno specifico social

        Args:
            brand_name: Nome brand
            social_type: Tipo social

        Returns:
            Lista URL trovati
        """
        # Costruisci query ottimizzata
        query = self._build_search_query(brand_name, social_type)

        try:
            # Input per Google Search Scraper
            run_input = {
                "queries": query,
                "resultsPerPage": 10,
                "maxPagesPerQuery": 1,
                "languageCode": "it",
                "mobileResults": False,
                "includeUnfilteredResults": False
            }

            # Esegui ricerca
            run = self.client.actor(APIFY_ACTORS['google_search']).call(run_input=run_input)

            # Recupera risultati
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Estrai URL
            found_urls = self._extract_urls_from_results(items, social_type)

            # Valida e pulisci URL
            valid_urls = self._validate_and_clean_urls(found_urls, social_type)

            return valid_urls[:5]  # Max 5 URL per social

        except Exception as e:
            self.logger.error(f"Errore ricerca {social_type}: {e}")
            return []

    def _build_search_query(self, brand_name, social_type):
        """Costruisce query di ricerca ottimizzata"""
        queries = {
            'instagram': f'site:instagram.com "{brand_name}"',
            'tiktok': f'site:tiktok.com "{brand_name}"',
            'youtube': f'site:youtube.com "{brand_name}"'
        }

        return queries.get(social_type, f'{brand_name} {social_type}')

    def _extract_urls_from_results(self, items, social_type):
        """Estrae URL dai risultati Google"""
        pattern = URL_PATTERNS.get(social_type)
        if not pattern:
            return []

        found_urls = []

        for item in items:
            organic_results = item.get('organicResults', [])

            for result in organic_results:
                url = result.get('url', '')
                title = result.get('title', '')
                description = result.get('description', '')

                # Combina per ricerca
                combined_text = f"{url} {title} {description}"

                # Trova URL con regex
                matches = re.finditer(pattern, combined_text)
                for match in matches:
                    found_urls.append(match.group(0))

        # Rimuovi duplicati
        return list(set(found_urls))

    def _validate_and_clean_urls(self, urls, social_type):
        """Valida e pulisci URL trovati"""
        valid_urls = []

        for url in urls:
            # Pulisci URL
            clean_url = URLValidator.clean_url(url)

            # Valida
            is_valid, _ = URLValidator.validate_social_url(clean_url, social_type)

            if is_valid:
                # Filtri specifici per social
                if self._is_profile_url(clean_url, social_type):
                    valid_urls.append(clean_url)

        return valid_urls

    def _is_profile_url(self, url, social_type):
        """Verifica che URL sia un profilo e non un post/video"""
        if social_type == 'instagram':
            # Escludi post, reel, tv
            if any(x in url for x in ['/p/', '/reel/', '/tv/']):
                return False
            # Deve avere username
            if url.endswith('instagram.com/') or url.endswith('instagram.com'):
                return False

        elif social_type == 'tiktok':
            # Deve avere @
            if '@' not in url:
                return False
            # Escludi video
            if '/video/' in url:
                return False

        elif social_type == 'youtube':
            # Deve essere canale
            if not any(x in url for x in ['/@', '/c/', '/channel/', '/user/']):
                return False
            # Escludi video
            if '/watch' in url or '/shorts/' in url:
                return False

        return True
