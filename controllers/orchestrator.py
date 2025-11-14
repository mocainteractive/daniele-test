"""
Orchestratore principale - coordina scraping, analisi e storage
"""
from models.scrapers.instagram_scraper import InstagramScraper
from models.scrapers.tiktok_scraper import TikTokScraper
from models.scrapers.youtube_scraper import YouTubeScraper
from models.analyzers.metrics_calculator import MetricsCalculator
from models.analyzers.ai_analyzer import AIAnalyzer
from models.storage.storage_manager import StorageManager
from controllers.url_finder import URLFinder
from utils.logger import Logger
from utils.progress_tracker import MultiPhaseProgress


class SocialOrchestrator:
    """Orchestratore centrale per analisi multi-social"""

    def __init__(self, apify_token, openai_token=None, logger=None):
        """
        Inizializza orchestratore

        Args:
            apify_token: Token Apify
            openai_token: Token OpenAI (opzionale)
            logger: Logger opzionale
        """
        self.apify_token = apify_token
        self.openai_token = openai_token
        self.logger = logger or Logger.get_logger(self.__class__.__name__)

        # Inizializza componenti
        self.url_finder = URLFinder(apify_token, logger=self.logger)
        self.storage = StorageManager(logger=self.logger)

        # Scrapers
        self.scrapers = {
            'instagram': InstagramScraper(apify_token, logger=self.logger),
            'tiktok': TikTokScraper(apify_token, logger=self.logger),
            'youtube': YouTubeScraper(apify_token, logger=self.logger)
        }

        # Analyzers
        self.metrics_calculator = MetricsCalculator()
        self.ai_analyzer = None
        if openai_token:
            self.ai_analyzer = AIAnalyzer(openai_token, logger=self.logger)

    def run_complete_analysis(self, brand_name, social_types, max_posts=10,
                             max_comments_per_post=50, auto_find_urls=True,
                             manual_urls=None, enable_ai=True):
        """
        Esegue analisi completa end-to-end

        Args:
            brand_name: Nome brand
            social_types: Lista social ['instagram', 'tiktok', 'youtube']
            max_posts: Numero massimo post per social
            max_comments_per_post: Numero massimo commenti per post
            auto_find_urls: Se True, cerca URL automaticamente
            manual_urls: Dict URL manuali {social: url}
            enable_ai: Abilita analisi AI

        Returns:
            Dict con risultati completi + analysis_id
        """
        # Setup progress tracker
        phases = [
            {'name': 'URL Discovery', 'steps': 1},
            {'name': 'Scraping Multi-Social', 'steps': len(social_types)},
            {'name': 'Analisi Metriche', 'steps': 1},
            {'name': 'Analisi AI', 'steps': 1 if enable_ai else 0},
            {'name': 'Salvataggio', 'steps': 1}
        ]

        progress = MultiPhaseProgress(phases)

        # FASE 1: URL Discovery
        progress.start_phase('URL Discovery')

        if auto_find_urls:
            social_urls = self.url_finder.find_social_urls(brand_name, social_types)
            progress.update(f"URL trovati per {len(social_urls)} social")
        else:
            social_urls = manual_urls or {}
            progress.update("URL manuali configurati")

        if not social_urls:
            self.logger.error("Nessun URL disponibile per analisi")
            return None

        # FASE 2: Scraping Multi-Social
        progress.start_phase('Scraping Multi-Social')
        results_by_social = {}

        for social_type in social_types:
            url = social_urls.get(social_type)

            if not url:
                self.logger.warning(f"URL non disponibile per {social_type}, skip")
                continue

            progress.update(f"Scraping {social_type}: {url}")

            # Scrape con scraper specifico
            scraper = self.scrapers.get(social_type)
            if not scraper:
                self.logger.warning(f"Scraper non disponibile per {social_type}")
                continue

            posts = scraper.scrape_posts_with_comments(
                url,
                max_posts=max_posts,
                max_comments_per_post=max_comments_per_post
            )

            results_by_social[social_type] = {
                'url': url,
                'posts': posts,
                'total_posts': len(posts),
                'total_comments': sum(len(p.get('comments', [])) for p in posts)
            }

        # FASE 3: Analisi Metriche
        progress.start_phase('Analisi Metriche')

        for social_type, data in results_by_social.items():
            posts = data['posts']

            # Calcola metriche post
            post_metrics = self.metrics_calculator.calculate_post_metrics(posts)

            # Calcola metriche commenti
            all_comments = []
            for post in posts:
                all_comments.extend(post.get('comments', []))

            comment_metrics = self.metrics_calculator.calculate_comments_metrics(all_comments)

            # Aggiungi metriche ai risultati
            data['metrics'] = post_metrics
            data['comment_metrics'] = comment_metrics

        # Metriche aggregate
        aggregated_metrics = self.metrics_calculator.calculate_aggregated_metrics(results_by_social)

        progress.update("Metriche calcolate per tutti i social")

        # FASE 4: Analisi AI (opzionale)
        ai_results = {}

        if enable_ai and self.ai_analyzer:
            progress.start_phase('Analisi AI')

            for social_type, data in results_by_social.items():
                # Raccogli tutti i commenti
                all_comments = []
                for post in data['posts']:
                    for comment in post.get('comments', []):
                        all_comments.append({
                            'text': comment.get('text', ''),
                            'author': comment.get('author', 'N/A'),
                            'post_url': post.get('url', 'N/A')
                        })

                if all_comments:
                    ai_analysis = self.ai_analyzer.analyze_comments(all_comments, social_type)
                    ai_results[social_type] = ai_analysis

            progress.update(f"Analisi AI completata per {len(ai_results)} social")

        # FASE 5: Salvataggio
        progress.start_phase('Salvataggio')

        final_results = {
            'brand_name': brand_name,
            'social_results': results_by_social,
            'aggregated_stats': aggregated_metrics,
            'ai_analysis': ai_results if enable_ai else None
        }

        # Salva in storage
        analysis_id = self.storage.save_analysis(
            brand_name=brand_name,
            social_urls=social_urls,
            results=final_results,
            enable_ai=enable_ai
        )

        progress.update(f"Analisi salvata con ID: {analysis_id}")

        # Completa
        progress.complete()

        return {
            'analysis_id': analysis_id,
            'results': final_results
        }

    def scrape_single_social(self, social_type, profile_url, max_posts=10,
                            max_comments_per_post=50):
        """
        Scraping di un singolo social (più veloce)

        Args:
            social_type: Tipo social
            profile_url: URL profilo
            max_posts: Numero post
            max_comments_per_post: Numero commenti per post

        Returns:
            Dict con post e commenti
        """
        self.logger.info(f"Scraping singolo social: {social_type}")

        scraper = self.scrapers.get(social_type)
        if not scraper:
            self.logger.error(f"Scraper non disponibile per {social_type}")
            return None

        posts = scraper.scrape_posts_with_comments(
            profile_url,
            max_posts=max_posts,
            max_comments_per_post=max_comments_per_post
        )

        # Calcola metriche
        metrics = self.metrics_calculator.calculate_post_metrics(posts)

        all_comments = []
        for post in posts:
            all_comments.extend(post.get('comments', []))

        comment_metrics = self.metrics_calculator.calculate_comments_metrics(all_comments)

        return {
            'social_type': social_type,
            'url': profile_url,
            'posts': posts,
            'metrics': metrics,
            'comment_metrics': comment_metrics
        }

    def load_analysis(self, analysis_id):
        """
        Carica analisi esistente

        Args:
            analysis_id: ID analisi

        Returns:
            Dict con dati analisi
        """
        return self.storage.load_analysis(analysis_id)

    def list_analyses(self, brand_name=None, limit=10):
        """
        Lista analisi salvate

        Args:
            brand_name: Filtra per brand
            limit: Limita risultati

        Returns:
            Lista analisi
        """
        return self.storage.list_analyses(brand_name=brand_name, limit=limit)

    def delete_analysis(self, analysis_id):
        """
        Elimina analisi

        Args:
            analysis_id: ID analisi

        Returns:
            bool: True se eliminata
        """
        return self.storage.delete_analysis(analysis_id)
