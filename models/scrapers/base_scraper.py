"""
Classe astratta base per tutti gli scrapers
Implementa pattern Template Method per evitare duplicazioni (DRY)
"""
from abc import ABC, abstractmethod
from apify_client import ApifyClient
import time
from config import RETRY_ATTEMPTS, RETRY_DELAY, RATE_LIMIT_DELAY
from utils.logger import Logger


class BaseScraper(ABC):
    """Classe base per scrapers social"""

    def __init__(self, apify_token, logger=None):
        """
        Inizializza scraper

        Args:
            apify_token: Token API Apify
            logger: Logger (opzionale)
        """
        self.client = ApifyClient(apify_token)
        self.logger = logger or Logger.get_logger(self.__class__.__name__)
        self.social_type = self._get_social_type()

    @abstractmethod
    def _get_social_type(self):
        """Restituisce tipo social ('instagram', 'tiktok', 'youtube')"""
        pass

    @abstractmethod
    def _build_posts_input(self, profile_url, max_posts):
        """Costruisce input per scraping post"""
        pass

    @abstractmethod
    def _build_comments_input(self, post_url, max_comments):
        """Costruisce input per scraping commenti"""
        pass

    @abstractmethod
    def _get_posts_actor(self):
        """Restituisce nome Actor Apify per post"""
        pass

    @abstractmethod
    def _get_comments_actor(self):
        """Restituisce nome Actor Apify per commenti"""
        pass

    @abstractmethod
    def _parse_post(self, item):
        """
        Parsing dati post dal risultato Apify

        Args:
            item: Item raw da Apify

        Returns:
            Dict con dati post normalizzati
        """
        pass

    @abstractmethod
    def _parse_comment(self, item):
        """
        Parsing dati commento dal risultato Apify

        Args:
            item: Item raw da Apify

        Returns:
            Dict con dati commento normalizzati
        """
        pass

    def scrape_posts(self, profile_url, max_posts=10):
        """
        Scrape post da profilo (Template Method)

        Args:
            profile_url: URL profilo social
            max_posts: Numero massimo post da estrarre

        Returns:
            Lista post con metadati
        """
        self.logger.info(f"Scraping {max_posts} post da {profile_url}")

        try:
            # Build input
            run_input = self._build_posts_input(profile_url, max_posts)

            # Esegui con retry
            items = self._run_actor_with_retry(
                self._get_posts_actor(),
                run_input,
                f"scraping post {self.social_type}"
            )

            # Parse risultati
            posts = []
            for item in items[:max_posts]:  # Limita a max_posts
                try:
                    post = self._parse_post(item)
                    posts.append(post)
                except Exception as e:
                    self.logger.warning(f"Errore parsing post: {e}")
                    continue

            self.logger.info(f"✓ Estratti {len(posts)} post")

            # Rate limiting
            self._apply_rate_limit()

            return posts

        except Exception as e:
            self.logger.error(f"Errore scraping post: {e}")
            return []

    def scrape_comments(self, post_url, max_comments=50):
        """
        Scrape commenti da post (Template Method)

        Args:
            post_url: URL del post
            max_comments: Numero massimo commenti

        Returns:
            Lista commenti
        """
        self.logger.debug(f"Scraping {max_comments} commenti da {post_url}")

        try:
            # Build input
            run_input = self._build_comments_input(post_url, max_comments)

            # Esegui con retry
            items = self._run_actor_with_retry(
                self._get_comments_actor(),
                run_input,
                f"scraping commenti {self.social_type}"
            )

            # Parse risultati
            comments = []
            for item in items[:max_comments]:
                try:
                    comment = self._parse_comment(item)
                    comments.append(comment)
                except Exception as e:
                    self.logger.warning(f"Errore parsing commento: {e}")
                    continue

            self.logger.debug(f"✓ Estratti {len(comments)} commenti")

            # Rate limiting
            self._apply_rate_limit()

            return comments

        except Exception as e:
            self.logger.error(f"Errore scraping commenti: {e}")
            return []

    def scrape_posts_with_comments(self, profile_url, max_posts=10, max_comments_per_post=50):
        """
        Scrape post + commenti (ottimizzato)

        Args:
            profile_url: URL profilo
            max_posts: Numero massimo post
            max_comments_per_post: Numero massimo commenti per post

        Returns:
            Lista post con commenti inclusi
        """
        self.logger.info(f"Scraping completo: {max_posts} post + {max_comments_per_post} commenti/post")

        # Scrape post
        posts = self.scrape_posts(profile_url, max_posts)

        if not posts:
            return []

        # Scrape commenti per ogni post
        for idx, post in enumerate(posts, 1):
            self.logger.info(f"  Post {idx}/{len(posts)}: estraendo commenti...")

            comments = self.scrape_comments(post['url'], max_comments_per_post)
            post['comments'] = comments
            post['comments_scraped'] = len(comments)

        total_comments = sum(len(p['comments']) for p in posts)
        self.logger.info(f"✓ Completato: {len(posts)} post, {total_comments} commenti totali")

        return posts

    def _run_actor_with_retry(self, actor_name, run_input, operation_desc):
        """
        Esegue Actor Apify con retry logic

        Args:
            actor_name: Nome Actor Apify
            run_input: Input per l'actor
            operation_desc: Descrizione operazione (per log)

        Returns:
            Lista items dal dataset

        Raises:
            Exception se fallisce dopo tutti i retry
        """
        last_error = None

        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                self.logger.debug(f"Tentativo {attempt}/{RETRY_ATTEMPTS}: {operation_desc}")

                # Esegui actor
                run = self.client.actor(actor_name).call(run_input=run_input)

                # Recupera risultati
                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

                return items

            except Exception as e:
                last_error = e
                self.logger.warning(f"Tentativo {attempt} fallito: {e}")

                if attempt < RETRY_ATTEMPTS:
                    wait_time = RETRY_DELAY * attempt  # Exponential backoff
                    self.logger.info(f"Retry tra {wait_time}s...")
                    time.sleep(wait_time)

        # Tutti i tentativi falliti
        self.logger.error(f"Tutti i tentativi falliti per {operation_desc}")
        raise last_error

    def _apply_rate_limit(self):
        """Applica rate limiting specifico per social"""
        delay = RATE_LIMIT_DELAY.get(self.social_type, 1)
        if delay > 0:
            time.sleep(delay)

    def get_social_type(self):
        """Restituisce tipo social"""
        return self.social_type
