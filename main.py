#!/usr/bin/env python3
"""
MOCA Social Brand Analyzer - Entry Point Principale

Supporta sia modalità CLI che Dashboard web
"""
import sys
import argparse
from utils.colors import TerminalColors as Colors


def print_banner():
    """Stampa banner MOCA"""
    banner = f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║          🎯 MOCA SOCIAL BRAND ANALYZER v1.0                      ║
║                                                                   ║
║          Analisi Completa Brand Social Media                     ║
║          Instagram • TikTok • YouTube                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def run_dashboard():
    """Avvia dashboard Streamlit"""
    import os
    import subprocess

    print(f"\n{Colors.RED}🚀 Avvio Dashboard Web...{Colors.RESET}\n")

    # Path alla dashboard
    dashboard_path = "views/dashboard_app.py"

    # Avvia Streamlit
    try:
        subprocess.run([
            "streamlit", "run", dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Dashboard chiusa.{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Errore avvio dashboard: {e}{Colors.RESET}\n")
        print(f"{Colors.GRAY}Assicurati di aver installato le dipendenze: pip install -r requirements.txt{Colors.RESET}\n")


def run_cli_analysis():
    """Avvia analisi CLI interattiva"""
    from controllers.orchestrator import SocialOrchestrator
    from controllers.export_manager import ExportManager
    from utils.validators import InputValidator, URLValidator

    print(f"\n{Colors.RED}🔧 Modalità CLI Interattiva{Colors.RESET}\n")

    # Input API Keys
    print(f"{Colors.GRAY}📝 Configurazione API Keys{Colors.RESET}\n")

    apify_token = input(f"🔑 Apify API Token: ").strip()

    is_valid, error = InputValidator.validate_api_token(apify_token, 'apify')
    if not is_valid:
        print(f"{Colors.RED}✗ {error}{Colors.RESET}")
        return

    openai_token = input(f"🤖 OpenAI API Key (Enter per skip): ").strip()
    enable_ai = bool(openai_token)

    if openai_token:
        is_valid, error = InputValidator.validate_api_token(openai_token, 'openai')
        if not is_valid:
            print(f"{Colors.RED}⚠ {error}. Analisi AI disabilitata.{Colors.RESET}")
            enable_ai = False
            openai_token = None

    # Input Brand
    print(f"\n{Colors.GRAY}🏢 Informazioni Brand{Colors.RESET}\n")

    brand_name = input(f"Nome Brand: ").strip()

    is_valid, result = InputValidator.validate_brand_name(brand_name)
    if not is_valid:
        print(f"{Colors.RED}✗ {result}{Colors.RESET}")
        return

    # Selezione Social
    print(f"\n{Colors.GRAY}📱 Selezione Social{Colors.RESET}\n")

    use_instagram = input("Analizzare Instagram? (s/n): ").lower() == 's'
    use_tiktok = input("Analizzare TikTok? (s/n): ").lower() == 's'
    use_youtube = input("Analizzare YouTube? (s/n): ").lower() == 's'

    social_types = []
    if use_instagram:
        social_types.append('instagram')
    if use_tiktok:
        social_types.append('tiktok')
    if use_youtube:
        social_types.append('youtube')

    if not social_types:
        print(f"{Colors.RED}✗ Devi selezionare almeno un social{Colors.RESET}")
        return

    # Modalità URL
    print(f"\n{Colors.GRAY}🔗 Modalità URL{Colors.RESET}\n")
    print("1. Auto-discovery (ricerca automatica)")
    print("2. Inserimento manuale")

    url_mode = input("\nScegli (1/2): ").strip()

    auto_find = url_mode == '1'
    manual_urls = {}

    if not auto_find:
        print(f"\n{Colors.GRAY}Inserisci URL profili:{Colors.RESET}\n")

        for social in social_types:
            url = input(f"{social.capitalize()} URL: ").strip()

            if url:
                is_valid, result = URLValidator.validate_social_url(url, social)
                if is_valid:
                    manual_urls[social] = url
                    print(f"{Colors.RED}✓ URL valido{Colors.RESET}")
                else:
                    print(f"{Colors.RED}✗ {result}{Colors.RESET}")

    # Parametri scraping
    print(f"\n{Colors.GRAY}⚙️ Parametri Scraping{Colors.RESET}\n")

    try:
        max_posts = int(input("Post per social (default 10): ").strip() or "10")
        max_comments = int(input("Commenti per post (default 50): ").strip() or "50")
    except:
        max_posts = 10
        max_comments = 50

    # Inizializza orchestrator
    print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
    print(f"{Colors.RED}🚀 Avvio Analisi...{Colors.RESET}")
    print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")

    orchestrator = SocialOrchestrator(
        apify_token=apify_token,
        openai_token=openai_token if enable_ai else None
    )

    # Esegui analisi
    try:
        result = orchestrator.run_complete_analysis(
            brand_name=brand_name,
            social_types=social_types,
            max_posts=max_posts,
            max_comments_per_post=max_comments,
            auto_find_urls=auto_find,
            manual_urls=manual_urls,
            enable_ai=enable_ai
        )

        if result:
            analysis_id = result['analysis_id']
            results = result['results']

            # Summary
            print(f"\n{Colors.RED}{'='*70}{Colors.RESET}")
            print(f"{Colors.RED}✅ ANALISI COMPLETATA!{Colors.RESET}")
            print(f"{Colors.RED}{'='*70}{Colors.RESET}\n")

            print(f"ID Analisi: {Colors.RED}{analysis_id}{Colors.RESET}")
            print(f"Brand: {Colors.RED}{brand_name}{Colors.RESET}")

            agg = results['aggregated_stats']
            print(f"\nPost totali: {Colors.RED}{agg['total_posts']}{Colors.RESET}")
            print(f"Commenti totali: {Colors.RED}{agg['total_comments']}{Colors.RESET}")
            print(f"Likes totali: {Colors.RED}{agg['total_likes']:,}{Colors.RESET}")

            # Export
            print(f"\n{Colors.GRAY}Vuoi esportare i risultati?{Colors.RESET}")
            export_choice = input("Scegli formato (pdf/csv/xlsx/json/skip): ").lower()

            if export_choice != 'skip':
                export_manager = ExportManager()

                if export_choice == 'pdf':
                    filepath = export_manager.export_to_pdf(results)
                elif export_choice == 'csv':
                    filepath = export_manager.export_to_csv(results)
                elif export_choice == 'xlsx':
                    filepath = export_manager.export_to_xlsx(results)
                elif export_choice == 'json':
                    filepath = export_manager.export_to_json(results)
                else:
                    print(f"{Colors.RED}Formato non riconosciuto{Colors.RESET}")
                    return

                print(f"\n{Colors.RED}✓ File esportato: {filepath}{Colors.RESET}")

            print(f"\n{Colors.RED}Grazie per aver usato MOCA Social Brand Analyzer!{Colors.RESET}\n")

        else:
            print(f"\n{Colors.RED}✗ Analisi fallita{Colors.RESET}\n")

    except Exception as e:
        print(f"\n{Colors.RED}✗ Errore: {e}{Colors.RESET}\n")


def main():
    """Entry point principale"""
    parser = argparse.ArgumentParser(
        description="MOCA Social Brand Analyzer - Analisi completa brand social media"
    )

    parser.add_argument(
        '--mode',
        choices=['dashboard', 'cli'],
        default='dashboard',
        help='Modalità di esecuzione (default: dashboard)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='MOCA Social Brand Analyzer v1.0'
    )

    args = parser.parse_args()

    # Banner
    print_banner()

    # Esegui modalità scelta
    if args.mode == 'dashboard':
        run_dashboard()
    elif args.mode == 'cli':
        run_cli_analysis()


if __name__ == "__main__":
    main()
