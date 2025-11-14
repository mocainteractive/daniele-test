"""
Scraper specifico per Instagram
"""
from models.scrapers.base_scraper import BaseScraper
from config import APIFY_ACTORS


class InstagramScraper(BaseScraper):
    """Scraper per Instagram"""

    def _get_social_type(self):
        return 'instagram'

    def _get_posts_actor(self):
        return APIFY_ACTORS['instagram']

    def _get_comments_actor(self):
        return APIFY_ACTORS['instagram']  # Stesso actor per post e commenti

    def _build_posts_input(self, profile_url, max_posts):
        """Build input per Instagram post scraper"""
        return {
            "directUrls": [profile_url],
            "resultsType": "posts",
            "resultsLimit": max_posts,
            "searchLimit": 1,
            "addParentData": True
        }

    def _build_comments_input(self, post_url, max_comments):
        """Build input per Instagram comments scraper"""
        return {
            "directUrls": [post_url],
            "resultsType": "comments",
            "resultsLimit": max_comments,
            "searchLimit": 1
        }

    def _parse_post(self, item):
        """Parse post Instagram"""
        # Estrai primi commenti se disponibili
        preview_comments = []
        latest_comments = item.get('latestComments', [])

        for comment in latest_comments[:3]:  # Primi 3 commenti preview
            preview_comments.append({
                'text': comment.get('text', ''),
                'author': comment.get('ownerUsername', 'N/A'),
                'likes': comment.get('likesCount', 0)
            })

        return {
            'id': item.get('id', 'N/A'),
            'url': item.get('url', 'N/A'),
            'type': item.get('type', 'N/A'),
            'caption': item.get('caption', ''),
            'timestamp': item.get('timestamp', 'N/A'),
            'likes': item.get('likesCount', 0),
            'comments_count': item.get('commentsCount', 0),
            'shares': 0,  # Instagram non espone share count pubblicamente
            'views': item.get('videoViewCount', 0) if item.get('type') == 'Video' else 0,
            'thumbnail': item.get('displayUrl', ''),
            'owner_username': item.get('ownerUsername', 'N/A'),
            'hashtags': item.get('hashtags', []),
            'mentions': item.get('mentions', []),
            'location': item.get('locationName', ''),
            'preview_comments': preview_comments,
            'comments': []  # Sarà popolato dopo
        }

    def _parse_comment(self, item):
        """Parse commento Instagram"""
        return {
            'id': item.get('id', 'N/A'),
            'text': item.get('text', ''),
            'author': item.get('ownerUsername', 'N/A'),
            'timestamp': item.get('timestamp', 'N/A'),
            'likes': item.get('likesCount', 0)
        }
