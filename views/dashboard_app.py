"""
Dashboard Streamlit principale - Social Brand Analyzer
"""
import streamlit as st
from controllers.orchestrator import SocialOrchestrator
from controllers.export_manager import ExportManager
from utils.validators import InputValidator, URLValidator
from views.components.metrics_display import *
from views.components.ai_display import *
from config import STREAMLIT_CONFIG, MOCA_FAVICON_URL
import time


# Configurazione pagina
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
)

# Custom CSS MOCA
st.markdown("""
<style>
    .main-header {
        color: #E52217;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stMetric {
        background-color: #FFE7E6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inizializza session state"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None

    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False


def render_sidebar():
    """Renderizza sidebar con configurazione"""
    st.sidebar.image(MOCA_FAVICON_URL, width=80)
    st.sidebar.title("⚙️ Configurazione")

    # API Keys
    st.sidebar.subheader("🔑 API Keys")

    apify_token = st.sidebar.text_input(
        "Apify API Token",
        type="password",
        help="Token API Apify per scraping"
    )

    openai_token = st.sidebar.text_input(
        "OpenAI API Key (opzionale)",
        type="password",
        help="Key OpenAI per analisi AI"
    )

    enable_ai = st.sidebar.checkbox(
        "Abilita Analisi AI",
        value=bool(openai_token),
        disabled=not bool(openai_token),
        help="Sentiment analysis, wordcloud, insights"
    )

    # Validazione
    api_valid = False
    if apify_token:
        is_valid, error = InputValidator.validate_api_token(apify_token, 'apify')
        if is_valid:
            api_valid = True
            st.sidebar.success("✓ Token Apify valido")
        else:
            st.sidebar.error(f"✗ {error}")

    if openai_token:
        is_valid, error = InputValidator.validate_api_token(openai_token, 'openai')
        if is_valid:
            st.sidebar.success("✓ Token OpenAI valido")
        else:
            st.sidebar.warning(f"⚠ {error}")

    # Inizializza orchestrator se token valido
    if api_valid:
        if st.session_state.orchestrator is None:
            st.session_state.orchestrator = SocialOrchestrator(
                apify_token=apify_token,
                openai_token=openai_token if enable_ai else None
            )

    return api_valid, enable_ai


def render_analysis_config():
    """Renderizza configurazione analisi"""
    st.header("🎯 Nuova Analisi")

    # Brand name
    brand_name = st.text_input(
        "Nome Brand",
        placeholder="es. Moca Interactive"
    )

    # Social selection
    st.subheader("📱 Social da Analizzare")

    col1, col2, col3 = st.columns(3)

    with col1:
        use_instagram = st.checkbox("📷 Instagram", value=True)
    with col2:
        use_tiktok = st.checkbox("🎵 TikTok", value=True)
    with col3:
        use_youtube = st.checkbox("🎥 YouTube", value=True)

    selected_socials = []
    if use_instagram:
        selected_socials.append('instagram')
    if use_tiktok:
        selected_socials.append('tiktok')
    if use_youtube:
        selected_socials.append('youtube')

    # URL Mode
    url_mode = st.radio(
        "Modalità URL",
        ["Auto-discovery (ricerca automatica)", "Inserimento manuale"],
        help="Auto-discovery cerca automaticamente i profili social del brand"
    )

    manual_urls = {}

    if url_mode == "Inserimento manuale":
        st.subheader("🔗 URL Profili Social")

        if 'instagram' in selected_socials:
            ig_url = st.text_input("Instagram URL", placeholder="https://instagram.com/username")
            if ig_url:
                is_valid, result = URLValidator.validate_social_url(ig_url, 'instagram')
                if is_valid:
                    manual_urls['instagram'] = ig_url
                    st.success(f"✓ Username: @{result}")
                else:
                    st.error(f"✗ {result}")

        if 'tiktok' in selected_socials:
            tk_url = st.text_input("TikTok URL", placeholder="https://tiktok.com/@username")
            if tk_url:
                is_valid, result = URLValidator.validate_social_url(tk_url, 'tiktok')
                if is_valid:
                    manual_urls['tiktok'] = tk_url
                    st.success(f"✓ Username: @{result}")
                else:
                    st.error(f"✗ {result}")

        if 'youtube' in selected_socials:
            yt_url = st.text_input("YouTube URL", placeholder="https://youtube.com/@channelname")
            if yt_url:
                is_valid, result = URLValidator.validate_social_url(yt_url, 'youtube')
                if is_valid:
                    manual_urls['youtube'] = yt_url
                    st.success(f"✓ Canale: {result}")
                else:
                    st.error(f"✗ {result}")

    # Parametri scraping
    st.subheader("⚙️ Parametri Scraping")

    col1, col2 = st.columns(2)

    with col1:
        max_posts = st.slider("Post per social", min_value=1, max_value=50, value=10)

    with col2:
        max_comments = st.slider("Commenti per post", min_value=5, max_value=200, value=50)

    return {
        'brand_name': brand_name,
        'social_types': selected_socials,
        'auto_find_urls': url_mode == "Auto-discovery (ricerca automatica)",
        'manual_urls': manual_urls,
        'max_posts': max_posts,
        'max_comments': max_comments
    }


def run_analysis(config, enable_ai):
    """Esegue analisi"""
    if not st.session_state.orchestrator:
        st.error("Orchestrator non inizializzato. Inserisci API token valido.")
        return

    # Validazioni
    if not config['brand_name']:
        st.error("Inserisci il nome del brand")
        return

    if not config['social_types']:
        st.error("Seleziona almeno un social")
        return

    if not config['auto_find_urls'] and not config['manual_urls']:
        st.error("Inserisci almeno un URL manuale")
        return

    # Progress
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("🚀 Avvio analisi...")
        progress_bar.progress(10)

        # Esegui analisi
        result = st.session_state.orchestrator.run_complete_analysis(
            brand_name=config['brand_name'],
            social_types=config['social_types'],
            max_posts=config['max_posts'],
            max_comments_per_post=config['max_comments'],
            auto_find_urls=config['auto_find_urls'],
            manual_urls=config['manual_urls'],
            enable_ai=enable_ai
        )

        progress_bar.progress(100)
        status_text.text("✅ Analisi completata!")

        # Salva in session state
        st.session_state.current_analysis = result
        st.session_state.analysis_complete = True

        time.sleep(1)
        st.rerun()

    except Exception as e:
        st.error(f"Errore durante l'analisi: {e}")
        progress_bar.empty()
        status_text.empty()


def render_results():
    """Renderizza risultati analisi"""
    if not st.session_state.current_analysis:
        st.info("👈 Configura e avvia una nuova analisi dalla sidebar")
        return

    analysis = st.session_state.current_analysis
    results = analysis['results']
    analysis_id = analysis['analysis_id']

    # Header
    st.markdown(f"<div class='main-header'>📊 Risultati Analisi</div>", unsafe_allow_html=True)
    st.caption(f"ID: {analysis_id} | Brand: {results['brand_name']}")

    # Overview Aggregata
    st.subheader("📈 Overview Aggregata")
    display_kpi_cards(results['aggregated_stats'])

    st.divider()

    # Tabs per Social
    social_results = results['social_results']

    if social_results:
        # Tab per ogni social + tab aggregata
        tab_names = [s.capitalize() for s in social_results.keys()] + ["📊 Aggregata"]
        tabs = st.tabs(tab_names)

        # Tab individuali
        for idx, (social_type, data) in enumerate(social_results.items()):
            with tabs[idx]:
                render_social_tab(social_type, data, results.get('ai_analysis', {}))

        # Tab aggregata
        with tabs[-1]:
            render_aggregated_tab(results)

    # Export section
    st.divider()
    render_export_section(results, analysis_id)


def render_social_tab(social_type, data, ai_analysis):
    """Renderizza tab per singolo social"""
    st.header(f"📱 {social_type.capitalize()}")

    # URL
    st.caption(f"Profilo: {data.get('url', 'N/A')}")

    # Metriche
    metrics = data.get('metrics', {})

    display_kpi_cards(metrics)

    # Performance
    st.subheader("🎯 Performance")
    display_performance_badge(metrics.get('performance_level', 'none'))

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        display_engagement_chart(data.get('posts', []))

    with col2:
        display_content_type_distribution(metrics.get('content_type_distribution', {}))

    # Hashtags
    display_hashtags_table(metrics.get('top_hashtags', []))

    # Top Posts
    display_top_posts_cards(metrics.get('top_posts', []))

    # AI Analysis (se disponibile)
    if social_type in ai_analysis and ai_analysis[social_type]:
        st.divider()
        st.header("🤖 Analisi AI")
        display_ai_summary(ai_analysis[social_type])


def render_aggregated_tab(results):
    """Renderizza tab aggregata cross-social"""
    st.header("📊 Vista Aggregata Cross-Social")

    agg_stats = results['aggregated_stats']

    # KPI totali
    display_kpi_cards(agg_stats)

    # Confronto social
    st.subheader("⚖️ Confronto tra Social")

    social_ranking = agg_stats.get('social_ranking', [])

    if social_ranking:
        import pandas as pd

        df = pd.DataFrame(social_ranking)
        df.columns = ['Social', 'Engagement Rate (%)', 'Post']

        st.dataframe(df, use_container_width=True)

        # Chart comparativo
        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Bar(
                x=[s['social'].capitalize() for s in social_ranking],
                y=[s['engagement_rate'] for s in social_ranking],
                marker_color=DashboardColors.PRIMARY,
                text=[f"{s['engagement_rate']:.2f}%" for s in social_ranking],
                textposition='auto'
            )
        ])

        fig.update_layout(
            title="Engagement Rate per Social",
            xaxis_title="Social",
            yaxis_title="Engagement Rate (%)",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # AI Aggregato
    if results.get('ai_analysis'):
        st.divider()
        st.header("🤖 Analisi AI Aggregata")
        display_aggregated_sentiment(results['social_results'])


def render_export_section(results, analysis_id):
    """Renderizza sezione export"""
    st.subheader("📥 Esportazione Risultati")

    col1, col2, col3, col4 = st.columns(4)

    export_manager = ExportManager()

    with col1:
        if st.button("📄 Esporta PDF", use_container_width=True):
            with st.spinner("Generando PDF..."):
                filepath = export_manager.export_to_pdf(results, f"report_{analysis_id}.pdf")
                st.success(f"✓ PDF esportato: {filepath}")

    with col2:
        if st.button("📊 Esporta CSV", use_container_width=True):
            with st.spinner("Generando CSV..."):
                filepath = export_manager.export_to_csv(results, f"metrics_{analysis_id}.csv")
                st.success(f"✓ CSV esportato: {filepath}")

    with col3:
        if st.button("📑 Esporta XLSX", use_container_width=True):
            with st.spinner("Generando XLSX..."):
                filepath = export_manager.export_to_xlsx(results, f"report_{analysis_id}.xlsx")
                st.success(f"✓ XLSX esportato: {filepath}")

    with col4:
        if st.button("💾 Esporta JSON", use_container_width=True):
            with st.spinner("Generando JSON..."):
                filepath = export_manager.export_to_json(results, f"data_{analysis_id}.json")
                st.success(f"✓ JSON esportato: {filepath}")


def main():
    """Main app"""
    # Logo header
    st.markdown("<div class='main-header'>🎯 MOCA Social Brand Analyzer</div>", unsafe_allow_html=True)

    # Initialize
    initialize_session_state()

    # Sidebar
    api_valid, enable_ai = render_sidebar()

    # Main area
    if not api_valid:
        st.warning("👈 Inserisci le API Keys nella sidebar per iniziare")
        return

    # Se analisi già completata, mostra risultati
    if st.session_state.analysis_complete:
        # Pulsante per nuova analisi
        if st.button("🔄 Nuova Analisi"):
            st.session_state.analysis_complete = False
            st.session_state.current_analysis = None
            st.rerun()

        render_results()

    else:
        # Form configurazione
        config = render_analysis_config()

        # Pulsante avvia
        if st.button("🚀 Avvia Analisi", type="primary", use_container_width=True):
            run_analysis(config, enable_ai)


if __name__ == "__main__":
    main()
