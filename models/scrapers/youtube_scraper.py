"""
Scraper specifico per YouTube
"""
from models.scrapers.base_scraper import BaseScraper
from config import APIFY_ACTORS


class YouTubeScraper(BaseScraper):
    """Scraper per YouTube"""

    def _get_social_type(self):
        return 'youtube'

    def _get_posts_actor(self):
        return APIFY_ACTORS['youtube']

    def _get_comments_actor(self):
        return APIFY_ACTORS['youtube_comments']

    def _build_posts_input(self, profile_url, max_posts):
        """Build input per YouTube video scraper"""
        return {
            "startUrls": [{"url": profile_url}],
            "maxResults": max_posts,
            "maxResultsShorts": 0,  # Escludi shorts
            "maxResultStreams": 0   # Escludi live
        }

    def _build_comments_input(self, post_url, max_comments):
        """Build input per YouTube comments scraper"""
        return {
            "startUrls": [{"url": post_url}],
            "maxComments": max_comments,
            "commentsSortBy": "1"  # 1=top comments, 0=newest first
        }

    def _parse_post(self, item):
        """Parse video YouTube"""
        # Estrai hashtags dalla descrizione se disponibili
        description = item.get('text', '')
        hashtags = [word[1:] for word in description.split() if word.startswith('#')]

        return {
            'id': item.get('id', 'N/A'),
            'url': item.get('url', 'N/A'),
            'type': 'video',
            'caption': item.get('title', 'N/A'),
            'description': description[:500],  # Primi 500 char
            'timestamp': item.get('date', 'N/A'),
            'likes': item.get('likes', 0),
            'comments_count': item.get('commentsCount', 0),
            'shares': 0,  # YouTube non espone share count via API pubblica
            'views': item.get('viewCount', 0),
            'thumbnail': item.get('thumbnailUrl', ''),
            'owner_username': item.get('channelName', 'N/A'),
            'channel_id': item.get('channelId', 'N/A'),
            'subscribers': item.get('numberOfSubscribers', 0),
            'duration': item.get('duration', 'N/A'),
            'hashtags': hashtags,
            'preview_comments': [],
            'comments': []
        }

    def _parse_comment(self, item):
        """Parse commento YouTube"""
        return {
            'id': item.get('cid', 'N/A'),
            'text': item.get('comment', ''),
            'author': item.get('author', 'N/A'),
            'timestamp': item.get('time', 'N/A'),
            'likes': item.get('voteCount', 0),
            'replies_count': item.get('replyCount', 0),
            'has_creator_heart': item.get('hasCreatorHeart', False)
        }
