"""
Scraper specifico per TikTok
"""
from models.scrapers.base_scraper import BaseScraper
from config import APIFY_ACTORS


class TikTokScraper(BaseScraper):
    """Scraper per TikTok"""

    def _get_social_type(self):
        return 'tiktok'

    def _get_posts_actor(self):
        return APIFY_ACTORS['tiktok']

    def _get_comments_actor(self):
        return APIFY_ACTORS['tiktok_comments']

    def _build_posts_input(self, profile_url, max_posts):
        """Build input per TikTok video scraper"""
        # Estrai username da URL
        username = profile_url.rstrip('/').split('/@')[-1]

        return {
            "profiles": [username],
            "resultsPerPage": max_posts,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "shouldDownloadSubtitles": False
        }

    def _build_comments_input(self, post_url, max_comments):
        """Build input per TikTok comments scraper"""
        return {
            "postURLs": [post_url],
            "maxComments": max_comments,
            "maxRepliesPerComment": 0  # Solo commenti top-level
        }

    def _parse_post(self, item):
        """Parse video TikTok"""
        # Estrai hashtags dal testo
        text = item.get('text', '')
        hashtags = [word[1:] for word in text.split() if word.startswith('#')]

        return {
            'id': item.get('id', 'N/A'),
            'url': item.get('webVideoUrl', 'N/A'),
            'type': 'video',
            'caption': text,
            'timestamp': item.get('createTimeISO', 'N/A'),
            'likes': item.get('diggCount', 0),
            'comments_count': item.get('commentCount', 0),
            'shares': item.get('shareCount', 0),
            'views': item.get('playCount', 0),
            'thumbnail': item.get('videoMeta', {}).get('coverUrl', ''),
            'owner_username': item.get('authorMeta', {}).get('name', 'N/A'),
            'hashtags': hashtags,
            'music': item.get('musicMeta', {}).get('musicName', 'N/A'),
            'duration': item.get('videoMeta', {}).get('duration', 0),
            'preview_comments': [],
            'comments': []
        }

    def _parse_comment(self, item):
        """Parse commento TikTok"""
        return {
            'id': item.get('id', 'N/A'),
            'text': item.get('text', ''),
            'author': item.get('authorName', 'N/A'),
            'timestamp': item.get('createTimeISO', 'N/A'),
            'likes': item.get('diggCount', 0)
        }
