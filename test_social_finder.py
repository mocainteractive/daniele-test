"""
Test ricerca automatica URL social per un brand
Usa BeautifulSoup + Google Search per trovare account social
"""
from apify_client import ApifyClient
import json
import re
from bs4 import BeautifulSoup
import time

# Colori Moca per output
class Colors:
    RED = '\033[91m'      # #E52217
    LIGHT_RED = '\033[38;2;255;231;230m'  # #FFE7E6
    BLACK = '\033[38;2;25;25;25m'  # #191919
    GRAY = '\033[38;2;138;138;138m'  # #8A8A8A
    RESET = '\033[0m'


def extract_urls_from_text(text, platform):
    """Estrae URL social dal testo"""
    urls = []
    
    patterns = {
        'instagram': r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9._]+)/?',
        'tiktok': r'https?://(?:www\.)?tiktok\.com/@([a-zA-Z0-9._]+)/?',
        'youtube': r'https?://(?:www\.)?youtube\.com/(?:@|c/|channel/|user/)([a-zA-Z0-9_-]+)/?'
    }
    
    pattern = patterns.get(platform)
    if pattern:
        matches = re.finditer(pattern, text)
        for match in matches:
            urls.append(match.group(0))
    
    return list(set(urls))  # Rimuovi duplicati


def find_social_urls(api_token, brand_name, platforms):
    """
    Trova automaticamente gli URL social di un brand usando Google Search
    
    Args:
        api_token: Token API Apify
        brand_name: Nome del brand da cercare
        platforms: Lista di piattaforme (es. ['instagram', 'tiktok', 'youtube'])
    
    Returns:
        Dict con URL trovati per ogni piattaforma
    """
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}🔍 RICERCA URL SOCIAL PER: {brand_name}{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    client = ApifyClient(api_token)
    results = {}
    
    # Usa Google Search Scraper ufficiale Apify
    for platform in platforms:
        print(f"{Colors.GRAY}📱 Cercando su {platform.capitalize()}...{Colors.RESET}")
        
        # Query ottimizzata per ogni piattaforma
        if platform == 'instagram':
            query = f'site:instagram.com "{brand_name}"'
        elif platform == 'tiktok':
            query = f'site:tiktok.com "{brand_name}"'
        elif platform == 'youtube':
            query = f'site:youtube.com "{brand_name}"'
        else:
            query = f'{brand_name} {platform}'
        
        print(f"   Query: '{query}'")
        
        try:
            # Input per Google Search Scraper
            run_input = {
                "queries": query,
                "resultsPerPage": 10,
                "maxPagesPerQuery": 1,
                "languageCode": "it",
                "mobileResults": False,
                "includeUnfilteredResults": False
            }
            
            run = client.actor("apify/google-search-scraper").call(run_input=run_input)
            
            # Recupera risultati
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            platform_urls = []
            
            # Estrai URL dai risultati organici
            for item in items:
                organic_results = item.get('organicResults', [])
                
                for result in organic_results:
                    url = result.get('url', '')
                    title = result.get('title', '')
                    description = result.get('description', '')
                    
                    # Combina per ricerca
                    combined_text = f"{url} {title} {description}"
                    
                    # Estrai URL specifici
                    found_urls = extract_urls_from_text(combined_text, platform)
                    platform_urls.extend(found_urls)
            
            # Rimuovi duplicati
            platform_urls = list(set(platform_urls))
            
            # Filtra URL validi (non homepage generiche)
            valid_urls = []
            for url in platform_urls:
                # Pulisci URL (rimuovi parametri query)
                clean_url = url.split('?')[0]
                
                # Rimuovi URL troppo generici
                if platform == 'instagram':
                    # Accetta solo profili, non homepage
                    if not clean_url.endswith('instagram.com/') and not clean_url.endswith('instagram.com'):
                        # Verifica che sia un profilo valido (non /p/ post, /reel/, etc)
                        if '/p/' not in clean_url and '/reel/' not in clean_url and '/tv/' not in clean_url:
                            valid_urls.append(clean_url)
                            
                elif platform == 'tiktok':
                    # Solo profili con @
                    if '@' in clean_url and '/video/' not in clean_url:
                        valid_urls.append(clean_url)
                        
                elif platform == 'youtube':
                    # Solo canali, non video singoli
                    if any(x in clean_url for x in ['/@', '/c/', '/channel/', '/user/']):
                        if '/watch' not in clean_url:
                            valid_urls.append(clean_url)
            
            results[platform] = valid_urls[:5]  # Primi 5 risultati
            
            if valid_urls:
                print(f"   {Colors.RED}✓ Trovati {len(valid_urls)} URL{Colors.RESET}")
                for url in valid_urls[:3]:  # Mostra primi 3
                    print(f"     • {url}")
                if len(valid_urls) > 3:
                    print(f"     ... e altri {len(valid_urls) - 3}")
            else:
                print(f"   {Colors.GRAY}✗ Nessun URL trovato{Colors.RESET}")
            
        except Exception as e:
            print(f"   {Colors.RED}✗ Errore: {str(e)}{Colors.RESET}")
            results[platform] = []
        
        print()
        time.sleep(2)  # Pausa tra richieste
    
    return results


def save_results(results, brand_name):
    """Salva risultati in JSON"""
    filename = f"social_urls_{brand_name.replace(' ', '_')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.RED}💾 Risultati salvati in: {filename}{Colors.RESET}")


def main():
    """Test principale"""
    print(f"{Colors.RED}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║            🎯 SOCIAL URL FINDER - TEST v1.0                      ║")
    print("║                    Brand: Moca Interactive                        ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    # Input
    api_token = input(f"{Colors.GRAY}🔑 Apify API Token: {Colors.RESET}").strip()
    brand_name = input(f"{Colors.GRAY}🏢 Nome Brand (es. 'Moca Interactive'): {Colors.RESET}").strip()
    
    # Piattaforme da cercare
    platforms = ['instagram', 'tiktok', 'youtube']
    
    print(f"\n{Colors.GRAY}🎯 Piattaforme da cercare: {', '.join(platforms)}{Colors.RESET}")
    print(f"{Colors.GRAY}⏳ Avvio ricerca... (può richiedere 1-2 minuti){Colors.RESET}\n")
    
    # Cerca URL social
    results = find_social_urls(api_token, brand_name, platforms)
    
    # Salva risultati
    save_results(results, brand_name)
    
    # Riepilogo
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}📊 RIEPILOGO RICERCA{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")
    
    total_found = sum(len(urls) for urls in results.values())
    print(f"Brand: {Colors.RED}{brand_name}{Colors.RESET}")
    print(f"Totale URL trovati: {Colors.RED}{total_found}{Colors.RESET}\n")
    
    for platform, urls in results.items():
        status = f"{Colors.RED}✓{Colors.RESET}" if urls else f"{Colors.GRAY}✗{Colors.RESET}"
        print(f"{status} {platform.capitalize()}: {len(urls)} URL")
    
    print(f"\n{Colors.RED}✅ TEST COMPLETATO!{Colors.RESET}\n")


if __name__ == "__main__":
    main()