"""
Calcolo metriche e KPI dai dati scraped
"""
from collections import Counter
from datetime import datetime
from config import calculate_engagement_rate, PERFORMANCE_THRESHOLDS


class MetricsCalculator:
    """Calcola metriche e KPI da post e commenti"""

    @staticmethod
    def calculate_post_metrics(posts):
        """
        Calcola metriche aggregate dai post

        Args:
            posts: Lista post

        Returns:
            Dict con metriche
        """
        if not posts:
            return MetricsCalculator._empty_metrics()

        total_posts = len(posts)
        total_likes = sum(p.get('likes', 0) for p in posts)
        total_comments = sum(p.get('comments_count', 0) for p in posts)
        total_shares = sum(p.get('shares', 0) for p in posts)
        total_views = sum(p.get('views', 0) for p in posts)

        # Medie
        avg_likes = total_likes / total_posts if total_posts > 0 else 0
        avg_comments = total_comments / total_posts if total_posts > 0 else 0
        avg_shares = total_shares / total_posts if total_posts > 0 else 0
        avg_views = total_views / total_posts if total_posts > 0 else 0

        # Engagement rate medio
        engagement_rates = []
        for post in posts:
            er = calculate_engagement_rate(
                post.get('likes', 0),
                post.get('comments_count', 0),
                post.get('shares', 0),
                post.get('views', 1)  # Evita divisione per 0
            )
            engagement_rates.append(er)

        avg_engagement_rate = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0

        # Performance classification
        performance = MetricsCalculator._classify_performance(avg_engagement_rate)

        # Hashtags più usati
        all_hashtags = []
        for post in posts:
            all_hashtags.extend(post.get('hashtags', []))

        top_hashtags = Counter(all_hashtags).most_common(10)

        # Post più performanti
        top_posts = sorted(
            posts,
            key=lambda p: calculate_engagement_rate(
                p.get('likes', 0),
                p.get('comments_count', 0),
                p.get('shares', 0),
                p.get('views', 1)
            ),
            reverse=True
        )[:5]

        # Distribuzione tipo contenuto
        content_types = Counter(p.get('type', 'unknown') for p in posts)

        return {
            'total_posts': total_posts,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'total_views': total_views,
            'avg_likes': round(avg_likes, 2),
            'avg_comments': round(avg_comments, 2),
            'avg_shares': round(avg_shares, 2),
            'avg_views': round(avg_views, 2),
            'avg_engagement_rate': round(avg_engagement_rate, 2),
            'performance_level': performance,
            'top_hashtags': [{'tag': tag, 'count': count} for tag, count in top_hashtags],
            'top_posts': [
                {
                    'url': p.get('url', 'N/A'),
                    'caption': p.get('caption', '')[:100],
                    'thumbnail': p.get('thumbnail', ''),
                    'likes': p.get('likes', 0),
                    'comments': p.get('comments_count', 0),
                    'views': p.get('views', 0),
                    'engagement_rate': round(calculate_engagement_rate(
                        p.get('likes', 0),
                        p.get('comments_count', 0),
                        p.get('shares', 0),
                        p.get('views', 1)
                    ), 2)
                }
                for p in top_posts
            ],
            'content_type_distribution': dict(content_types)
        }

    @staticmethod
    def calculate_comments_metrics(all_comments):
        """
        Calcola metriche dai commenti

        Args:
            all_comments: Lista commenti

        Returns:
            Dict con metriche commenti
        """
        if not all_comments:
            return {
                'total_comments': 0,
                'avg_comment_length': 0,
                'total_comment_likes': 0,
                'top_commenters': []
            }

        total_comments = len(all_comments)

        # Lunghezza media commento
        comment_lengths = [len(c.get('text', '')) for c in all_comments]
        avg_length = sum(comment_lengths) / total_comments if total_comments > 0 else 0

        # Likes totali sui commenti
        total_comment_likes = sum(c.get('likes', 0) for c in all_comments)

        # Top commenters
        commenters = Counter(c.get('author', 'unknown') for c in all_comments)
        top_commenters = [
            {'author': author, 'comments_count': count}
            for author, count in commenters.most_common(10)
        ]

        return {
            'total_comments': total_comments,
            'avg_comment_length': round(avg_length, 2),
            'total_comment_likes': total_comment_likes,
            'top_commenters': top_commenters
        }

    @staticmethod
    def calculate_aggregated_metrics(social_results):
        """
        Calcola metriche aggregate cross-social

        Args:
            social_results: Dict con risultati per social
                            {social_type: {posts: [...], metrics: {...}}}

        Returns:
            Dict con metriche aggregate
        """
        total_posts = 0
        total_comments = 0
        total_likes = 0
        total_views = 0
        all_hashtags = []

        for social_type, data in social_results.items():
            metrics = data.get('metrics', {})
            total_posts += metrics.get('total_posts', 0)
            total_comments += metrics.get('total_comments', 0)
            total_likes += metrics.get('total_likes', 0)
            total_views += metrics.get('total_views', 0)

            # Hashtags
            for ht in metrics.get('top_hashtags', []):
                all_hashtags.append(ht['tag'])

        # Top hashtags aggregati
        top_hashtags_aggregated = Counter(all_hashtags).most_common(15)

        # Social con più engagement
        social_by_engagement = sorted(
            social_results.items(),
            key=lambda x: x[1].get('metrics', {}).get('avg_engagement_rate', 0),
            reverse=True
        )

        return {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_likes': total_likes,
            'total_views': total_views,
            'socials_analyzed': len(social_results),
            'top_hashtags_global': [
                {'tag': tag, 'count': count}
                for tag, count in top_hashtags_aggregated
            ],
            'best_performing_social': social_by_engagement[0][0] if social_by_engagement else None,
            'social_ranking': [
                {
                    'social': social,
                    'engagement_rate': data.get('metrics', {}).get('avg_engagement_rate', 0),
                    'posts': data.get('metrics', {}).get('total_posts', 0)
                }
                for social, data in social_by_engagement
            ]
        }

    @staticmethod
    def _classify_performance(engagement_rate):
        """Classifica livello performance"""
        if engagement_rate < PERFORMANCE_THRESHOLDS['low']:
            return 'low'
        elif engagement_rate < PERFORMANCE_THRESHOLDS['medium']:
            return 'medium'
        elif engagement_rate < PERFORMANCE_THRESHOLDS['high']:
            return 'high'
        else:
            return 'excellent'

    @staticmethod
    def _empty_metrics():
        """Metriche vuote"""
        return {
            'total_posts': 0,
            'total_likes': 0,
            'total_comments': 0,
            'total_shares': 0,
            'total_views': 0,
            'avg_likes': 0,
            'avg_comments': 0,
            'avg_shares': 0,
            'avg_views': 0,
            'avg_engagement_rate': 0,
            'performance_level': 'none',
            'top_hashtags': [],
            'top_posts': [],
            'content_type_distribution': {}
        }
