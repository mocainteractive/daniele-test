"""
Test End-to-End - Backend Completo
Simula flusso completo: auto-discovery → scraping → AI → storage
"""
from social_orchestrator import SocialScraperOrchestrator
from social_url_finder import SocialURLFinder
from storage_manager import StorageManager
from ai_analyzer import Colors
import json
from datetime import datetime


def test_complete_workflow():
    """Test completo del workflow"""
    print(f"{Colors.RED}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║      🧪 TEST END-TO-END - WORKFLOW COMPLETO v1.0                 ║")
    print("║                  Brand: Moca Interactive                          ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    # === INPUT ===
    print(f"{Colors.RED}📝 CONFIGURAZIONE{Colors.RESET}\n")
    
    apify_token = input(f"{Colors.GRAY}🔑 Apify API Token: {Colors.RESET}").strip()
    openai_token = input(f"{Colors.GRAY}🤖 OpenAI API Key (Enter per skip): {Colors.RESET}").strip()
    brand_name = input(f"{Colors.GRAY}🏢 Nome Brand: {Colors.RESET}").strip()
    
    enable_ai = bool(openai_token)
    
    # Opzioni social
    print(f"\n{Colors.GRAY}Seleziona social da analizzare:{Colors.RESET}")
    use_youtube = input(f"  YouTube (y/n): ").lower() == 'y'
    use_instagram = input(f"  Instagram (y/n): ").lower() == 'y'
    use_tiktok = input(f"  TikTok (y/n): ").lower() == 'y'
    
    social_types = []
    if use_youtube: social_types.append('youtube')
    if use_instagram: social_types.append('instagram')
    if use_tiktok: social_types.append('tiktok')
    
    if not social_types:
        print(f"{Colors.RED}❌ Devi selezionare almeno un social!{Colors.RESET}")
        return
    
    try:
        max_posts = int(input(f"\n{Colors.GRAY}📊 Max post per social (default 3): {Colors.RESET}").strip() or "3")
        max_comments = int(input(f"{Colors.GRAY}💬 Max commenti per post (default 10): {Colors.RESET}").strip() or "10")
    except:
        max_posts, max_comments = 3, 10
    
    # === STEP 1: AUTO-DISCOVERY ===
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}STEP 1/4: AUTO-DISCOVERY URL SOCIAL{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}")
    
    finder = SocialURLFinder(use_web_search=False)  # Modalità simulazione
    found_urls = finder.find_social_urls(brand_name, social_types)
    
    # Conferma URL
    print(f"\n{Colors.GRAY}🔍 URL trovati:{Colors.RESET}\n")
    
    social_urls = {}
    for social_type in social_types:
        urls = found_urls.get(social_type, [])
        
        if urls:
            print(f"{Colors.RED}{social_type.upper()}:{Colors.RESET}")
            for idx, url in enumerate(urls, 1):
                print(f"  {idx}. {url}")
            
            # Chiedi conferma
            confirm = input(f"  Usare questo URL? (y/n oppure inserisci URL custom): ").strip()
            
            if confirm.lower() == 'y':
                social_urls[social_type] = urls[0]
            elif confirm.lower() == 'n':
                pass
            else:
                social_urls[social_type] = confirm
        else:
            # Chiedi URL manuale
            custom_url = input(f"{Colors.GRAY}{social_type.upper()} - Inserisci URL manuale: {Colors.RESET}").strip()
            if custom_url:
                social_urls[social_type] = custom_url
        
        print()
    
    if not social_urls:
        print(f"{Colors.RED}❌ Nessun URL confermato!{Colors.RESET}")
        return
    
    print(f"{Colors.RED}✓ URL confermati:{Colors.RESET}")
    for social, url in social_urls.items():
        print(f"  {social}: {url}")
    
    # === STEP 2: SCRAPING MULTI-SOCIAL ===
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}STEP 2/4: SCRAPING MULTI-SOCIAL{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    orchestrator = SocialScraperOrchestrator(
        apify_token=apify_token,
        openai_token=openai_token if enable_ai else None
    )
    
    results = orchestrator.scrape_multi_social(
        brand_name=brand_name,
        social_urls=social_urls,
        enable_ai=enable_ai,
        max_posts=max_posts,
        max_comments=max_comments
    )
    
    # === STEP 3: STORAGE ===
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}STEP 3/4: SALVATAGGIO RISULTATI{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    storage = StorageManager('./storage')
    search_id = storage.save_search(
        brand_name=brand_name,
        social_urls=social_urls,
        results=results,
        enable_ai=enable_ai
    )
    
    print(f"{Colors.RED}✓ Salvato con ID: {search_id}{Colors.RESET}")
    
    # === STEP 4: EXPORT ===
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}STEP 4/4: EXPORT RISULTATI{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    # Export JSON completo
    export_file = f'export_{search_id}.json'
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"{Colors.RED}📄 Export JSON: {export_file}{Colors.RESET}")
    
    # Export storico CSV
    storage.export_history_csv(f'history_{search_id}.csv')
    
    # === SUMMARY FINALE ===
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}🎉 TEST COMPLETATO CON SUCCESSO!{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    stats = results['aggregated_stats']
    
    print(f"{Colors.GRAY}📊 Riepilogo:{Colors.RESET}")
    print(f"  Brand: {Colors.RED}{brand_name}{Colors.RESET}")
    print(f"  Social analizzati: {Colors.RED}{len(social_urls)}{Colors.RESET}")
    print(f"  Post totali: {Colors.RED}{stats['total_posts']}{Colors.RESET}")
    print(f"  Commenti totali: {Colors.RED}{stats['total_comments']}{Colors.RESET}")
    print(f"  Likes totali: {Colors.RED}{stats['total_likes']:,}{Colors.RESET}")
    
    if stats.get('sentiment_aggregate'):
        sentiment = stats['sentiment_aggregate']
        print(f"\n{Colors.GRAY}🎭 Sentiment:{Colors.RESET}")
        print(f"  ✅ Positivi: {Colors.RED}{sentiment['positive_pct']:.1f}%{Colors.RESET}")
        print(f"  ⚠️  Neutri: {Colors.GRAY}{sentiment['neutral_pct']:.1f}%{Colors.RESET}")
        print(f"  ❌ Negativi: {Colors.RED}{sentiment['negative_pct']:.1f}%{Colors.RESET}")
    
    print(f"\n{Colors.GRAY}💾 File generati:{Colors.RESET}")
    print(f"  - {export_file}")
    print(f"  - history_{search_id}.csv")
    print(f"  - storage/results/{search_id}.json")
    
    print(f"\n{Colors.RED}✨ Workflow completato!{Colors.RESET}\n")


if __name__ == "__main__":
    test_complete_workflow()