"""
Test scraping post Instagram + commenti
Usa apify/instagram-scraper
"""
from apify_client import ApifyClient
import json
from datetime import datetime

# Colori Moca
class Colors:
    RED = '\033[91m'
    LIGHT_RED = '\033[38;2;255;231;230m'
    BLACK = '\033[38;2;25;25;25m'
    GRAY = '\033[38;2;138;138;138m'
    RESET = '\033[0m'


def scrape_instagram_posts(api_token, profile_url, max_posts=10):
    """
    Scrape post da profilo Instagram + commenti
    
    Args:
        api_token: Token API Apify
        profile_url: URL profilo Instagram
        max_posts: Numero massimo di post da estrarre
    
    Returns:
        Lista di post con commenti
    """
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}📷 SCRAPING INSTAGRAM{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.GRAY}📍 Profilo: {profile_url}{Colors.RESET}")
    print(f"{Colors.GRAY}📊 Max post: {max_posts}{Colors.RESET}\n")
    
    client = ApifyClient(api_token)
    
    try:
        # Input per Instagram Scraper
        run_input = {
            "directUrls": [profile_url],
            "resultsType": "posts",  # Vogliamo i post
            "resultsLimit": max_posts,
            "searchLimit": 1,
            "addParentData": True
        }
        
        print(f"{Colors.GRAY}⏳ Avvio scraping... (può richiedere 1-2 minuti){Colors.RESET}\n")
        
        # Avvia actor
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        
        # Recupera risultati
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        print(f"{Colors.RED}✅ Scraping completato!{Colors.RESET}")
        print(f"{Colors.RED}📊 Post estratti: {len(items)}{Colors.RESET}\n")
        
        # Processa risultati
        posts_data = []
        
        for idx, item in enumerate(items, 1):
            post = {
                'post_id': item.get('id', 'N/A'),
                'post_url': item.get('url', 'N/A'),
                'caption': item.get('caption', '')[:200],  # Primi 200 char
                'likes': item.get('likesCount', 0),
                'comments_count': item.get('commentsCount', 0),
                'timestamp': item.get('timestamp', 'N/A'),
                'type': item.get('type', 'N/A'),
                'owner_username': item.get('ownerUsername', 'N/A'),
                'comments': []
            }
            
            # Estrai primi commenti se disponibili
            latest_comments = item.get('latestComments', [])
            for comment in latest_comments[:5]:  # Primi 5 commenti
                post['comments'].append({
                    'text': comment.get('text', ''),
                    'owner': comment.get('ownerUsername', 'N/A'),
                    'likes': comment.get('likesCount', 0)
                })
            
            posts_data.append(post)
            
            # Mostra preview
            print(f"{Colors.GRAY}{'─'*70}{Colors.RESET}")
            print(f"{Colors.RED}Post #{idx}{Colors.RESET}")
            print(f"  URL: {post['post_url']}")
            print(f"  Likes: {Colors.RED}{post['likes']}{Colors.RESET} | Commenti: {Colors.RED}{post['comments_count']}{Colors.RESET}")
            print(f"  Caption: {post['caption'][:100]}...")
            if post['comments']:
                print(f"  💬 Commenti estratti: {len(post['comments'])}")
        
        return posts_data
        
    except Exception as e:
        print(f"{Colors.RED}✗ Errore: {str(e)}{Colors.RESET}")
        return []


def scrape_instagram_comments(api_token, post_url, max_comments=50):
    """
    Scrape commenti da un singolo post Instagram
    
    Args:
        api_token: Token API Apify
        post_url: URL del post Instagram
        max_comments: Numero massimo commenti
    
    Returns:
        Lista commenti
    """
    print(f"\n{Colors.GRAY}💬 Scraping commenti dal post...{Colors.RESET}")
    
    client = ApifyClient(api_token)
    
    try:
        run_input = {
            "directUrls": [post_url],
            "resultsType": "comments",
            "resultsLimit": max_comments,
            "searchLimit": 1
        }
        
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        comments = []
        for item in items:
            comments.append({
                'id': item.get('id', 'N/A'),
                'text': item.get('text', ''),
                'owner': item.get('ownerUsername', 'N/A'),
                'timestamp': item.get('timestamp', 'N/A'),
                'likes': item.get('likesCount', 0)
            })
        
        print(f"   {Colors.RED}✓ Estratti {len(comments)} commenti{Colors.RESET}")
        return comments
        
    except Exception as e:
        print(f"   {Colors.RED}✗ Errore commenti: {str(e)}{Colors.RESET}")
        return []


def save_results(posts_data, profile_username):
    """Salva risultati in JSON"""
    filename = f"instagram_posts_{profile_username}.json"
    
    output = {
        'scraped_at': datetime.now().isoformat(),
        'profile': profile_username,
        'total_posts': len(posts_data),
        'posts': posts_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.RED}💾 Risultati salvati in: {filename}{Colors.RESET}")


def main():
    """Test principale"""
    print(f"{Colors.RED}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║           📷 INSTAGRAM SCRAPER - TEST v1.0                       ║")
    print("║                   Brand: Moca Interactive                         ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    # Input
    api_token = input(f"{Colors.GRAY}🔑 Apify API Token: {Colors.RESET}").strip()
    profile_url = input(f"{Colors.GRAY}📷 URL Profilo Instagram: {Colors.RESET}").strip()
    
    # Estrai username
    username = profile_url.rstrip('/').split('/')[-1]
    
    # Numero post
    try:
        max_posts = int(input(f"{Colors.GRAY}📊 Numero post da estrarre (default 10): {Colors.RESET}").strip() or "10")
    except:
        max_posts = 10
    
    # Scrape posts
    posts_data = scrape_instagram_posts(api_token, profile_url, max_posts)
    
    if posts_data:
        # Opzionale: scrape commenti dettagliati dal primo post
        print(f"\n{Colors.GRAY}{'='*70}{Colors.RESET}")
        scrape_detailed = input(f"{Colors.GRAY}Vuoi scrapare tutti i commenti del primo post? (s/n): {Colors.RESET}").strip().lower()
        
        if scrape_detailed == 's' and posts_data[0]['post_url'] != 'N/A':
            detailed_comments = scrape_instagram_comments(api_token, posts_data[0]['post_url'], 50)
            posts_data[0]['all_comments'] = detailed_comments
            print(f"{Colors.RED}✓ Aggiunti {len(detailed_comments)} commenti dettagliati al primo post{Colors.RESET}")
        
        # Salva risultati
        save_results(posts_data, username)
        
        # Statistiche finali
        print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
        print(f"{Colors.RED}📊 STATISTICHE FINALI{Colors.RESET}")
        print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
        
        total_likes = sum(p['likes'] for p in posts_data)
        total_comments = sum(p['comments_count'] for p in posts_data)
        
        print(f"Profilo: {Colors.RED}@{username}{Colors.RESET}")
        print(f"Post estratti: {Colors.RED}{len(posts_data)}{Colors.RESET}")
        print(f"Totale likes: {Colors.RED}{total_likes:,}{Colors.RESET}")
        print(f"Totale commenti: {Colors.RED}{total_comments:,}{Colors.RESET}")
        
        if posts_data:
            avg_likes = total_likes / len(posts_data)
            avg_comments = total_comments / len(posts_data)
            print(f"\nMedia likes/post: {Colors.RED}{avg_likes:.1f}{Colors.RESET}")
            print(f"Media commenti/post: {Colors.RED}{avg_comments:.1f}{Colors.RESET}")
    
    print(f"\n{Colors.RED}✅ TEST COMPLETATO!{Colors.RESET}\n")


if __name__ == "__main__":
    main()