"""
Test scraping video YouTube + commenti
Usa streamers/youtube-scraper e streamers/youtube-comments-scraper
"""
from apify_client import ApifyClient
import json
from datetime import datetime
import time

# Colori Moca
class Colors:
    RED = '\033[91m'
    LIGHT_RED = '\033[38;2;255;231;230m'
    BLACK = '\033[38;2;25;25;25m'
    GRAY = '\033[38;2;138;138;138m'
    RESET = '\033[0m'


def scrape_youtube_videos(api_token, channel_url, max_videos=10):
    """Scrape video da canale YouTube"""
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}🎥 SCRAPING YOUTUBE VIDEOS{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.GRAY}📍 Canale: {channel_url}{Colors.RESET}")
    print(f"{Colors.GRAY}📊 Max video: {max_videos}{Colors.RESET}\n")
    
    client = ApifyClient(api_token)
    
    try:
        # Input per YouTube Scraper - formato corretto
        run_input = {
            "startUrls": [{"url": channel_url}],  # Deve essere array di oggetti
            "maxResults": max_videos,
            "maxResultsShorts": 0,
            "maxResultStreams": 0
        }
        
        print(f"{Colors.GRAY}⏳ Avvio scraping... (può richiedere 2-3 minuti){Colors.RESET}\n")
        
        run = client.actor("streamers/youtube-scraper").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        print(f"{Colors.RED}✅ Scraping completato!{Colors.RESET}")
        print(f"{Colors.RED}📊 Video estratti: {len(items)}{Colors.RESET}\n")
        
        videos_data = []
        
        for idx, item in enumerate(items, 1):
            video = {
                'video_id': item.get('id', 'N/A'),
                'video_url': item.get('url', 'N/A'),
                'title': item.get('title', 'N/A'),
                'description': item.get('text', '')[:200],
                'likes': item.get('likes', 0),
                'views': item.get('viewCount', 0),
                'comments_count': item.get('commentsCount', 0),
                'duration': item.get('duration', 'N/A'),
                'date': item.get('date', 'N/A'),
                'channel_name': item.get('channelName', 'N/A'),
                'subscribers': item.get('numberOfSubscribers', 0),
                'comments': []
            }
            
            videos_data.append(video)
            
            print(f"{Colors.GRAY}{'─'*70}{Colors.RESET}")
            print(f"{Colors.RED}Video #{idx}{Colors.RESET}")
            print(f"  Titolo: {video['title'][:60]}...")
            print(f"  URL: {video['video_url']}")
            print(f"  Likes: {Colors.RED}{video['likes']:,}{Colors.RESET} | Commenti: {Colors.RED}{video['comments_count']}{Colors.RESET} | Views: {Colors.RED}{video['views']:,}{Colors.RESET}")
            
            # Estrai commenti per questo video (primi 5)
            if video['video_url'] != 'N/A' and video['comments_count'] > 0:
                print(f"  {Colors.GRAY}⏳ Estraendo commenti...{Colors.RESET}", end='', flush=True)
                video_comments = scrape_youtube_comments(client, video['video_url'], max_comments=5)
                video['comments'] = video_comments
                print(f" {Colors.RED}✓ {len(video_comments)} estratti{Colors.RESET}")
                time.sleep(2)  # Pausa tra richieste
        
        return videos_data
        
    except Exception as e:
        print(f"{Colors.RED}✗ Errore: {str(e)}{Colors.RESET}")
        return []


def scrape_youtube_comments(client, video_url, max_comments=5):
    """Scrape commenti da video YouTube"""
    try:
        run_input = {
            "startUrls": [{"url": video_url}],
            "maxComments": max_comments,
            "commentsSortBy": "1"  # 1=top comments, 0=newest first
        }
        
        run = client.actor("streamers/youtube-comments-scraper").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        comments = []
        for item in items:
            comments.append({
                'id': item.get('cid', 'N/A'),
                'text': item.get('comment', ''),
                'author': item.get('author', 'N/A'),
                'likes': item.get('voteCount', 0),
                'replies': item.get('replyCount', 0),
                'has_creator_heart': item.get('hasCreatorHeart', False)
            })
        
        return comments
        
    except Exception as e:
        return []


def save_results(videos_data, channel_name):
    """Salva risultati in JSON"""
    filename = f"youtube_videos_{channel_name.replace(' ', '_')}.json"
    
    output = {
        'scraped_at': datetime.now().isoformat(),
        'channel': channel_name,
        'total_videos': len(videos_data),
        'videos': videos_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.RED}💾 Risultati salvati in: {filename}{Colors.RESET}")


def main():
    """Test principale"""
    print(f"{Colors.RED}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║             🎥 YOUTUBE SCRAPER - TEST v1.0                       ║")
    print("║                    Brand: Moca Interactive                        ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    api_token = input(f"{Colors.GRAY}🔑 Apify API Token: {Colors.RESET}").strip()
    channel_url = input(f"{Colors.GRAY}🎥 URL Canale YouTube: {Colors.RESET}").strip()
    
    # Estrai nome canale
    if '/@' in channel_url:
        channel_name = channel_url.rstrip('/').split('/@')[-1]
    elif '/channel/' in channel_url:
        channel_name = channel_url.rstrip('/').split('/channel/')[-1]
    else:
        channel_name = "unknown"
    
    try:
        max_videos = int(input(f"{Colors.GRAY}📊 Numero video da estrarre (default 10): {Colors.RESET}").strip() or "10")
    except:
        max_videos = 10
    
    videos_data = scrape_youtube_videos(api_token, channel_url, max_videos)
    
    if videos_data:
        save_results(videos_data, channel_name)
        
        print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"{Colors.RED}📊 STATISTICHE FINALI{Colors.RESET}")
        print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
        
        total_likes = sum(v['likes'] for v in videos_data)
        total_comments = sum(v['comments_count'] for v in videos_data)
        total_views = sum(v['views'] for v in videos_data)
        
        print(f"Canale: {Colors.RED}{channel_name}{Colors.RESET}")
        print(f"Video estratti: {Colors.RED}{len(videos_data)}{Colors.RESET}")
        print(f"Totale likes: {Colors.RED}{total_likes:,}{Colors.RESET}")
        print(f"Totale commenti: {Colors.RED}{total_comments:,}{Colors.RESET}")
        print(f"Totale visualizzazioni: {Colors.RED}{total_views:,}{Colors.RESET}")
        
        if videos_data:
            print(f"\nMedia likes/video: {Colors.RED}{total_likes/len(videos_data):.1f}{Colors.RESET}")
            print(f"Media commenti/video: {Colors.RED}{total_comments/len(videos_data):.1f}{Colors.RESET}")
            print(f"Media views/video: {Colors.RED}{total_views/len(videos_data):,.0f}{Colors.RESET}")
    
    print(f"\n{Colors.RED}✅ TEST COMPLETATO!{Colors.RESET}\n")


if __name__ == "__main__":
    main()