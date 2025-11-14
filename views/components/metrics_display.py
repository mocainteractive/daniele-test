"""
Componenti UI per visualizzazione metriche
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.colors import DashboardColors


def display_kpi_cards(metrics):
    """
    Mostra KPI cards in formato responsive

    Args:
        metrics: Dict con metriche
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📊 Post Totali",
            value=metrics.get('total_posts', 0)
        )

    with col2:
        st.metric(
            label="❤️ Likes Totali",
            value=f"{metrics.get('total_likes', 0):,}"
        )

    with col3:
        st.metric(
            label="💬 Commenti Totali",
            value=f"{metrics.get('total_comments', 0):,}"
        )

    with col4:
        st.metric(
            label="📈 Engagement Rate",
            value=f"{metrics.get('avg_engagement_rate', 0):.2f}%"
        )


def display_performance_badge(performance_level):
    """
    Mostra badge performance

    Args:
        performance_level: Livello performance (low, medium, high, excellent)
    """
    badges = {
        'low': ('🔴', 'Basso', DashboardColors.SENTIMENT_NEGATIVE),
        'medium': ('🟡', 'Medio', DashboardColors.SENTIMENT_NEUTRAL),
        'high': ('🟢', 'Alto', DashboardColors.SENTIMENT_POSITIVE),
        'excellent': ('⭐', 'Eccellente', DashboardColors.PRIMARY)
    }

    emoji, label, color = badges.get(performance_level, ('⚪', 'N/A', DashboardColors.GRAY))

    st.markdown(
        f"<div style='background-color: {color}; padding: 10px; border-radius: 5px; "
        f"text-align: center; color: white; font-weight: bold;'>"
        f"{emoji} Performance: {label}</div>",
        unsafe_allow_html=True
    )


def display_engagement_chart(posts):
    """
    Mostra grafico engagement per post

    Args:
        posts: Lista post con metriche
    """
    if not posts:
        st.info("Nessun post disponibile")
        return

    # Prepara dati
    post_labels = [f"Post {i+1}" for i in range(len(posts[:10]))]
    engagement_rates = []

    for post in posts[:10]:
        likes = post.get('likes', 0)
        comments = post.get('comments_count', 0)
        shares = post.get('shares', 0)
        views = post.get('views', 1)

        er = ((likes + comments + shares) / views) * 100
        engagement_rates.append(er)

    # Crea grafico
    fig = go.Figure(data=[
        go.Bar(
            x=post_labels,
            y=engagement_rates,
            marker_color=DashboardColors.PRIMARY,
            text=[f"{er:.2f}%" for er in engagement_rates],
            textposition='auto'
        )
    ])

    fig.update_layout(
        title="Engagement Rate per Post",
        xaxis_title="Post",
        yaxis_title="Engagement Rate (%)",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


def display_content_type_distribution(content_types):
    """
    Mostra distribuzione tipi di contenuto

    Args:
        content_types: Dict {tipo: count}
    """
    if not content_types:
        st.info("Nessun dato disponibile")
        return

    # Crea pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(content_types.keys()),
        values=list(content_types.values()),
        marker=dict(colors=DashboardColors.get_gradient(len(content_types)))
    )])

    fig.update_layout(
        title="Distribuzione Tipi di Contenuto",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


def display_hashtags_table(top_hashtags):
    """
    Mostra tabella top hashtags

    Args:
        top_hashtags: Lista dict {tag, count}
    """
    if not top_hashtags:
        st.info("Nessun hashtag trovato")
        return

    st.subheader("🏷️ Top Hashtags")

    # Crea DataFrame
    import pandas as pd

    df = pd.DataFrame(top_hashtags[:10])
    df.columns = ['Hashtag', 'Utilizzi']
    df.index = df.index + 1

    # Mostra tabella
    st.dataframe(df, use_container_width=True)


def display_top_posts_cards(top_posts):
    """
    Mostra card per top posts

    Args:
        top_posts: Lista post top performing
    """
    if not top_posts:
        st.info("Nessun post disponibile")
        return

    st.subheader("🔥 Post Più Performanti")

    for idx, post in enumerate(top_posts[:5], 1):
        with st.container():
            col1, col2 = st.columns([1, 3])

            with col1:
                # Thumbnail (se disponibile)
                thumbnail = post.get('thumbnail', '')
                if thumbnail:
                    try:
                        st.image(thumbnail, use_container_width=True)
                    except:
                        st.write("📷")

            with col2:
                st.markdown(f"**Post #{idx}**")
                st.caption(post.get('caption', 'N/A')[:150])

                # Metriche
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Likes", f"{post.get('likes', 0):,}")
                with col_b:
                    st.metric("Commenti", post.get('comments', 0))
                with col_c:
                    st.metric("Views", f"{post.get('views', 0):,}")
                with col_d:
                    st.metric("ER", f"{post.get('engagement_rate', 0):.1f}%")

                # Link
                if post.get('url') and post['url'] != 'N/A':
                    st.markdown(f"[🔗 Vai al post]({post['url']})")

            st.divider()


def display_comments_preview(comments):
    """
    Mostra preview commenti

    Args:
        comments: Lista commenti
    """
    if not comments:
        st.info("Nessun commento disponibile")
        return

    st.subheader("💬 Esempi Commenti")

    # Mostra primi 10 commenti
    for comment in comments[:10]:
        with st.container():
            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"**{comment.get('author', 'N/A')}**")
                st.write(comment.get('text', '')[:200])

            with col2:
                st.caption(f"❤️ {comment.get('likes', 0)}")

            st.divider()
