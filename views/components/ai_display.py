"""
Componenti UI per visualizzazione analisi AI
"""
import streamlit as st
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils.colors import DashboardColors
from config import WORDCLOUD_CONFIG


def display_sentiment_analysis(sentiment):
    """
    Mostra analisi sentiment

    Args:
        sentiment: Dict con dati sentiment
    """
    if not sentiment:
        st.info("Nessun dato sentiment disponibile")
        return

    st.subheader("🎭 Sentiment Analysis")

    # Gauge chart sentiment
    total = sentiment.get('positive', 0) + sentiment.get('neutral', 0) + sentiment.get('negative', 0)

    if total > 0:
        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Positivo', 'Neutro', 'Negativo'],
            values=[
                sentiment.get('positive', 0),
                sentiment.get('neutral', 0),
                sentiment.get('negative', 0)
            ],
            marker=dict(colors=[
                DashboardColors.SENTIMENT_POSITIVE,
                DashboardColors.SENTIMENT_NEUTRAL,
                DashboardColors.SENTIMENT_NEGATIVE
            ]),
            hole=0.4,
            textinfo='label+percent',
            textposition='inside'
        )])

        fig.update_layout(
            title="Distribuzione Sentiment",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Metriche
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="✅ Positivi",
                value=sentiment.get('positive', 0),
                delta=f"{sentiment.get('positive_pct', 0):.1f}%"
            )

        with col2:
            st.metric(
                label="⚠️ Neutri",
                value=sentiment.get('neutral', 0),
                delta=f"{sentiment.get('neutral_pct', 0):.1f}%"
            )

        with col3:
            st.metric(
                label="❌ Negativi",
                value=sentiment.get('negative', 0),
                delta=f"{sentiment.get('negative_pct', 0):.1f}%"
            )
    else:
        st.warning("Nessun dato sentiment disponibile")


def display_wordcloud(wordcloud_data):
    """
    Mostra wordcloud

    Args:
        wordcloud_data: Lista dict {word, frequency}
    """
    if not wordcloud_data:
        st.info("Nessun dato wordcloud disponibile")
        return

    st.subheader("☁️ Word Cloud")

    # Crea dizionario frequenze
    word_freq = {item['word']: item['frequency'] for item in wordcloud_data}

    if word_freq:
        # Genera wordcloud
        wc = WordCloud(
            width=WORDCLOUD_CONFIG['width'],
            height=WORDCLOUD_CONFIG['height'],
            background_color=WORDCLOUD_CONFIG['background_color'],
            colormap=WORDCLOUD_CONFIG['colormap'],
            max_words=WORDCLOUD_CONFIG['max_words'],
            min_font_size=WORDCLOUD_CONFIG['min_font_size'],
            relative_scaling=WORDCLOUD_CONFIG['relative_scaling'],
            prefer_horizontal=WORDCLOUD_CONFIG['prefer_horizontal']
        ).generate_from_frequencies(word_freq)

        # Mostra
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')

        st.pyplot(fig)

        # Top 10 parole
        st.caption("🔝 Top 10 Parole")
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        cols = st.columns(5)
        for idx, (word, freq) in enumerate(top_words):
            with cols[idx % 5]:
                st.markdown(f"**{word}**")
                st.caption(f"{freq} volte")
    else:
        st.warning("Nessuna parola da visualizzare")


def display_insights(insights):
    """
    Mostra insight AI

    Args:
        insights: Dict con punti forza, debolezza, suggerimenti
    """
    if not insights:
        st.info("Nessun insight disponibile")
        return

    st.subheader("💡 AI Insights")

    # Punti di Forza
    if insights.get('punti_forza'):
        st.markdown("### 💪 Punti di Forza")
        for punto in insights['punti_forza']:
            st.markdown(f"- {punto}")

    st.divider()

    # Punti di Debolezza
    if insights.get('punti_debolezza'):
        st.markdown("### ⚡ Punti di Debolezza")
        for punto in insights['punti_debolezza']:
            st.markdown(f"- {punto}")

    st.divider()

    # Suggerimenti
    if insights.get('suggerimenti'):
        st.markdown("### 🎯 Suggerimenti Strategici")
        for suggerimento in insights['suggerimenti']:
            st.markdown(f"- {suggerimento}")

    st.divider()

    # Temi Ricorrenti
    if insights.get('temi_ricorrenti'):
        st.markdown("### 📊 Temi Ricorrenti")
        for tema in insights['temi_ricorrenti']:
            st.markdown(f"- {tema}")


def display_ai_summary(ai_results):
    """
    Mostra summary completo AI per un social

    Args:
        ai_results: Dict con risultati AI completi
    """
    if not ai_results:
        st.info("Nessuna analisi AI disponibile")
        return

    # Tabs per sezioni AI
    tab1, tab2, tab3 = st.tabs(["🎭 Sentiment", "☁️ Word Cloud", "💡 Insights"])

    with tab1:
        display_sentiment_analysis(ai_results.get('sentiment'))

    with tab2:
        display_wordcloud(ai_results.get('wordcloud'))

    with tab3:
        display_insights(ai_results.get('insights'))


def display_aggregated_sentiment(social_results):
    """
    Mostra sentiment aggregato cross-social

    Args:
        social_results: Dict risultati per social con AI
    """
    st.subheader("🎭 Sentiment Aggregato Cross-Social")

    # Raccoglie sentiment da tutti i social
    all_sentiments = {
        'positive': 0,
        'neutral': 0,
        'negative': 0
    }

    for social_type, data in social_results.items():
        ai = data.get('ai_analysis', {})
        sentiment = ai.get('sentiment', {})

        all_sentiments['positive'] += sentiment.get('positive', 0)
        all_sentiments['neutral'] += sentiment.get('neutral', 0)
        all_sentiments['negative'] += sentiment.get('negative', 0)

    total = sum(all_sentiments.values())

    if total > 0:
        # Chart aggregato
        fig = go.Figure(data=[go.Bar(
            x=['Positivo', 'Neutro', 'Negativo'],
            y=[
                all_sentiments['positive'],
                all_sentiments['neutral'],
                all_sentiments['negative']
            ],
            marker_color=[
                DashboardColors.SENTIMENT_POSITIVE,
                DashboardColors.SENTIMENT_NEUTRAL,
                DashboardColors.SENTIMENT_NEGATIVE
            ],
            text=[
                f"{all_sentiments['positive']}",
                f"{all_sentiments['neutral']}",
                f"{all_sentiments['negative']}"
            ],
            textposition='auto'
        )])

        fig.update_layout(
            title="Sentiment Aggregato",
            xaxis_title="Sentiment",
            yaxis_title="Numero Commenti",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Percentuali
        col1, col2, col3 = st.columns(3)

        with col1:
            pct = (all_sentiments['positive'] / total) * 100
            st.metric("✅ Positivi", all_sentiments['positive'], f"{pct:.1f}%")

        with col2:
            pct = (all_sentiments['neutral'] / total) * 100
            st.metric("⚠️ Neutri", all_sentiments['neutral'], f"{pct:.1f}%")

        with col3:
            pct = (all_sentiments['negative'] / total) * 100
            st.metric("❌ Negativi", all_sentiments['negative'], f"{pct:.1f}%")
    else:
        st.warning("Nessun dato sentiment disponibile")
