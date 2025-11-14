"""
Test Integrazione: YouTube Scraper + AI Analysis
Combina estrazione video/commenti con analisi AI
"""
from apify_client import ApifyClient
from ai_analyzer import SocialAIAnalyzer, Colors
import json
from datetime import datetime
import time


def scrape_youtube_with_ai(apify_token, openai_token, channel_url, max_videos=3):
    """
    Scraping YouTube + Analisi AI completa
    
    Args:
        apify_token: Token Apify per scraping
        openai_token: Token OpenAI per analisi
        channel_url: URL canale YouTube
        max_videos: Numero video da analizzare
    """
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}🎥 YOUTUBE SCRAPER + AI ANALYSIS{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    # Step 1: Scrape video
    print(f"{Colors.GRAY}📹 Step 1: Estrazione video...{Colors.RESET}\n")
    videos_data = scrape_videos(apify_token, channel_url, max_videos)
    
    if not videos_data:
        print(f"{Colors.RED}❌ Nessun video estratto{Colors.RESET}")
        return None
    
    # Step 2: Scrape commenti per ogni video
    print(f"\n{Colors.GRAY}💬 Step 2: Estrazione commenti...{Colors.RESET}\n")
    client = ApifyClient(apify_token)
    
    for idx, video in enumerate(videos_data, 1):
        print(f"{Colors.GRAY}Video {idx}/{len(videos_data)}: {video['title'][:50]}...{Colors.RESET}")
        
        if video['comments_count'] > 0:
            comments = scrape_comments(client, video['video_url'], max_comments=20)
            video['comments'] = comments
            print(f"  {Colors.RED}✓ {len(comments)} commenti estratti{Colors.RESET}")
            time.sleep(1)
        else:
            video['comments'] = []
            print(f"  {Colors.GRAY}⚠ Nessun commento disponibile{Colors.RESET}")
    
    # Step 3: Analisi AI su tutti i commenti
    print(f"\n{Colors.GRAY}🤖 Step 3: Analisi AI...{Colors.RESET}")
    all_comments = []
    
    for video in videos_data:
        for comment in video['comments']:
            all_comments.append({
                'text': comment.get('text', ''),
                'url': video['video_url'],
                'author': comment.get('author', 'N/A'),
                'video_title': video['title']
            })
    
    if all_comments:
        analyzer = SocialAIAnalyzer(openai_token)
        ai_results = analyzer.analyze_comments(all_comments, social_type='youtube')
    else:
        ai_results = None
        print(f"{Colors.RED}⚠ Nessun commento da analizzare{Colors.RESET}")
    
    # Combina risultati
    final_results = {
        'scraped_at': datetime.now().isoformat(),
        'channel_url': channel_url,
        'total_videos': len(videos_data),
        'total_comments': len(all_comments),
        'videos': videos_data,
        'ai_analysis': ai_results
    }
    
    return final_results


def scrape_videos(api_token, channel_url, max_videos):
    """Estrae video da canale YouTube"""
    client = ApifyClient(api_token)
    
    try:
        run_input = {
            "startUrls": [{"url": channel_url}],
            "maxResults": max_videos,
            "maxResultsShorts": 0,
            "maxResultStreams": 0
        }
        
        run = client.actor("streamers/youtube-scraper").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        videos_data = []
        for item in items:
            videos_data.append({
                'video_id': item.get('id', 'N/A'),
                'video_url': item.get('url', 'N/A'),
                'title': item.get('title', 'N/A'),
                'description': item.get('text', '')[:200],
                'likes': item.get('likes', 0),
                'views': item.get('viewCount', 0),
                'comments_count': item.get('commentsCount', 0),
                'duration': item.get('duration', 'N/A'),
                'date': item.get('date', 'N/A'),
                'comments': []
            })
        
        return videos_data
        
    except Exception as e:
        print(f"{Colors.RED}❌ Errore scraping video: {str(e)}{Colors.RESET}")
        return []


def scrape_comments(client, video_url, max_comments=20):
    """Estrae commenti da video YouTube"""
    try:
        run_input = {
            "startUrls": [{"url": video_url}],
            "maxComments": max_comments,
            "commentsSortBy": "1"
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
                'replies': item.get('replyCount', 0)
            })
        
        return comments
        
    except Exception as e:
        print(f"{Colors.RED}⚠ Errore commenti: {str(e)}{Colors.RESET}")
        return []


def print_final_summary(results):
    """Stampa summary finale completo"""
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}📊 RISULTATI FINALI{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    print(f"{Colors.GRAY}Statistiche Scraping:{Colors.RESET}")
    print(f"  🎥 Video analizzati: {Colors.RED}{results['total_videos']}{Colors.RESET}")
    print(f"  💬 Commenti totali: {Colors.RED}{results['total_comments']}{Colors.RESET}")
    
    if results['ai_analysis']:
        ai = results['ai_analysis']
        sentiment = ai['sentiment']
        
        print(f"\n{Colors.GRAY}Sentiment Analysis:{Colors.RESET}")
        total = sentiment['positive'] + sentiment['negative'] + sentiment['neutral']
        if total > 0:
            print(f"  ✅ Positivi: {Colors.RED}{sentiment['positive']} ({sentiment['positive']/total*100:.1f}%){Colors.RESET}")
            print(f"  ⚠️  Neutri: {Colors.GRAY}{sentiment['neutral']} ({sentiment['neutral']/total*100:.1f}%){Colors.RESET}")
            print(f"  ❌ Negativi: {Colors.RED}{sentiment['negative']} ({sentiment['negative']/total*100:.1f}%){Colors.RESET}")
        
        insights = ai['insights']
        print(f"\n{Colors.GRAY}AI Insights:{Colors.RESET}")
        print(f"  💪 Punti di forza: {Colors.RED}{len(insights.get('punti_forza', []))}{Colors.RESET}")
        print(f"  ⚡ Punti di debolezza: {Colors.RED}{len(insights.get('punti_debolezza', []))}{Colors.RESET}")
        print(f"  💡 Suggerimenti: {Colors.RED}{len(insights.get('suggerimenti', []))}{Colors.RESET}")
        
        # Mostra top 5 parole wordcloud
        if ai['wordcloud']:
            print(f"\n{Colors.GRAY}Top 5 Parole Chiave:{Colors.RESET}")
            for idx, word_data in enumerate(ai['wordcloud'][:5], 1):
                print(f"  {idx}. {Colors.RED}{word_data['word']}{Colors.RESET} ({word_data['frequency']})")
    
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")


def main():
    """Test principale"""
    print(f"{Colors.RED}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║       🤖 YOUTUBE + AI INTEGRATION TEST v1.0                      ║")
    print("║                  Brand: Moca Interactive                          ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    # Input
    apify_token = input(f"{Colors.GRAY}🔑 Apify API Token: {Colors.RESET}").strip()
    openai_token = input(f"{Colors.GRAY}🤖 OpenAI API Key: {Colors.RESET}").strip()
    channel_url = input(f"{Colors.GRAY}🎥 URL Canale YouTube: {Colors.RESET}").strip()
    
    try:
        max_videos = int(input(f"{Colors.GRAY}📊 Numero video (default 3): {Colors.RESET}").strip() or "3")
    except:
        max_videos = 3
    
    # Esegui scraping + analisi
    results = scrape_youtube_with_ai(apify_token, openai_token, channel_url, max_videos)
    
    if results:
        # Salva risultati
        filename = f"youtube_ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Stampa summary
        print_final_summary(results)
        
        print(f"\n{Colors.RED}💾 Risultati salvati: {filename}{Colors.RESET}")
    
    print(f"\n{Colors.RED}✅ TEST COMPLETATO!{Colors.RESET}\n")


if __name__ == "__main__":
    main()