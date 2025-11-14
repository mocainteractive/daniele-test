"""
Test scraping video TikTok + commenti
Usa clockworks/tiktok-scraper e clockworks/tiktok-comments-scraper
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


def scrape_tiktok_videos(api_token, profile_url, max_videos=10):
    """Scrape video da profilo TikTok"""
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}🎵 SCRAPING TIKTOK VIDEOS{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.GRAY}📍 Profilo: {profile_url}{Colors.RESET}")
    print(f"{Colors.GRAY}📊 Max video: {max_videos}{Colors.RESET}\n")
    
    client = ApifyClient(api_token)
    
    try:
        username = profile_url.rstrip('/').split('/@')[-1]
        
        run_input = {
            "profiles": [username],
            "resultsPerPage": max_videos,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
            "shouldDownloadSubtitles": False
        }
        
        print(f"{Colors.GRAY}⏳ Avvio scraping... (può richiedere 2-3 minuti){Colors.RESET}\n")
        
        run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        print(f"{Colors.RED}✅ Scraping completato!{Colors.RESET}")
        print(f"{Colors.RED}📊 Video estratti: {len(items)}{Colors.RESET}\n")
        
        videos_data = []
        
        for idx, item in enumerate(items, 1):
            video = {
                'video_id': item.get('id', 'N/A'),
                'video_url': item.get('webVideoUrl', 'N/A'),
                'text': item.get('text', '')[:200],
                'likes': item.get('diggCount', 0),
                'comments_count': item.get('commentCount', 0),
                'shares': item.get('shareCount', 0),
                'plays': item.get('playCount', 0),
                'timestamp': item.get('createTimeISO', 'N/A'),
                'author': item.get('authorMeta', {}).get('name', 'N/A'),
                'music': item.get('musicMeta', {}).get('musicName', 'N/A'),
                'comments': []
            }
            
            videos_data.append(video)
            
            print(f"{Colors.GRAY}{'─'*70}{Colors.RESET}")
            print(f"{Colors.RED}Video #{idx}{Colors.RESET}")
            print(f"  URL: {video['video_url']}")
            print(f"  Likes: {Colors.RED}{video['likes']:,}{Colors.RESET} | Commenti: {Colors.RED}{video['comments_count']}{Colors.RESET} | Views: {Colors.RED}{video['plays']:,}{Colors.RESET}")
            print(f"  Testo: {video['text'][:80]}...")
            
            # Estrai commenti per questo video (primi 5)
            if video['video_url'] != 'N/A' and video['comments_count'] > 0:
                print(f"  {Colors.GRAY}⏳ Estraendo commenti...{Colors.RESET}", end='', flush=True)
                video_comments = scrape_tiktok_comments(client, video['video_url'], max_comments=5)
                video['comments'] = video_comments
                print(f" {Colors.RED}✓ {len(video_comments)} estratti{Colors.RESET}")
                time.sleep(2)  # Pausa tra richieste
        
        return videos_data
        
    except Exception as e:
        print(f"{Colors.RED}✗ Errore: {str(e)}{Colors.RESET}")
        return []


def scrape_tiktok_comments(client, video_url, max_comments=5):
    """Scrape commenti da video TikTok"""
    try:
        run_input = {
            "postURLs": [video_url],
            "maxComments": max_comments,
            "maxRepliesPerComment": 0
        }
        
        run = client.actor("clockworks/tiktok-comments-scraper").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        comments = []
        for item in items:
            comments.append({
                'id': item.get('id', 'N/A'),
                'text': item.get('text', ''),
                'author': item.get('authorName', 'N/A'),
                'likes': item.get('diggCount', 0),
                'timestamp': item.get('createTimeISO', 'N/A')
            })
        
        return comments
        
    except Exception as e:
        return []


def save_results(videos_data, profile_username):
    """Salva risultati in JSON"""
    filename = f"tiktok_videos_{profile_username}.json"
    
    output = {
        'scraped_at': datetime.now().isoformat(),
        'profile': profile_username,
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
    print("║             🎵 TIKTOK SCRAPER - TEST v1.0                        ║")
    print("║                    Brand: Moca Interactive                        ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    api_token = input(f"{Colors.GRAY}🔑 Apify API Token: {Colors.RESET}").strip()
    profile_url = input(f"{Colors.GRAY}🎵 URL Profilo TikTok: {Colors.RESET}").strip()
    
    username = profile_url.rstrip('/').split('/@')[-1]
    
    try:
        max_videos = int(input(f"{Colors.GRAY}📊 Numero video da estrarre (default 10): {Colors.RESET}").strip() or "10")
    except:
        max_videos = 10
    
    videos_data = scrape_tiktok_videos(api_token, profile_url, max_videos)
    
    if videos_data:
        save_results(videos_data, username)
        
        print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"{Colors.RED}📊 STATISTICHE FINALI{Colors.RESET}")
        print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
        
        total_likes = sum(v['likes'] for v in videos_data)
        total_comments = sum(v['comments_count'] for v in videos_data)
        total_shares = sum(v['shares'] for v in videos_data)
        total_plays = sum(v['plays'] for v in videos_data)
        
        print(f"Profilo: {Colors.RED}@{username}{Colors.RESET}")
        print(f"Video estratti: {Colors.RED}{len(videos_data)}{Colors.RESET}")
        print(f"Totale likes: {Colors.RED}{total_likes:,}{Colors.RESET}")
        print(f"Totale commenti: {Colors.RED}{total_comments:,}{Colors.RESET}")
        print(f"Totale condivisioni: {Colors.RED}{total_shares:,}{Colors.RESET}")
        print(f"Totale visualizzazioni: {Colors.RED}{total_plays:,}{Colors.RESET}")
        
        if videos_data:
            print(f"\nMedia likes/video: {Colors.RED}{total_likes/len(videos_data):.1f}{Colors.RESET}")
            print(f"Media commenti/video: {Colors.RED}{total_comments/len(videos_data):.1f}{Colors.RESET}")
            print(f"Media views/video: {Colors.RED}{total_plays/len(videos_data):,.0f}{Colors.RESET}")
    
    print(f"\n{Colors.RED}✅ TEST COMPLETATO!{Colors.RESET}\n")


if __name__ == "__main__":
    main()