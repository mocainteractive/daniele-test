"""
Manager per export risultati in vari formati (PDF, CSV, XLSX)
"""
import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors as rl_colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from config import EXPORTS_DIR, CSV_ENCODING, XLSX_ENGINE, PDF_CONFIG, BRAND_COLORS
from utils.logger import Logger


class ExportManager:
    """Manager per esportazione risultati"""

    def __init__(self, exports_dir=None, logger=None):
        """
        Inizializza export manager

        Args:
            exports_dir: Directory export (default da config)
            logger: Logger opzionale
        """
        self.exports_dir = Path(exports_dir) if exports_dir else EXPORTS_DIR
        self.logger = logger or Logger.get_logger(self.__class__.__name__)

        # Crea directory se non esiste
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def export_to_json(self, results, filename=None):
        """
        Export in JSON

        Args:
            results: Risultati da esportare
            filename: Nome file (opzionale)

        Returns:
            Path del file esportato
        """
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.exports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"✓ JSON esportato: {filepath}")
        return str(filepath)

    def export_to_csv(self, results, filename=None):
        """
        Export metriche in CSV

        Args:
            results: Risultati analisi
            filename: Nome file (opzionale)

        Returns:
            Path del file esportato
        """
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = self.exports_dir / filename

        with open(filepath, 'w', encoding=CSV_ENCODING, newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Brand',
                'Social',
                'Post Totali',
                'Commenti Totali',
                'Likes Totali',
                'Views Totali',
                'Engagement Rate (%)',
                'Performance Level'
            ])

            # Dati per social
            brand_name = results.get('brand_name', 'N/A')
            social_results = results.get('social_results', {})

            for social_type, data in social_results.items():
                metrics = data.get('metrics', {})

                writer.writerow([
                    brand_name,
                    social_type.capitalize(),
                    metrics.get('total_posts', 0),
                    metrics.get('total_comments', 0),
                    metrics.get('total_likes', 0),
                    metrics.get('total_views', 0),
                    f"{metrics.get('avg_engagement_rate', 0):.2f}",
                    metrics.get('performance_level', 'N/A')
                ])

        self.logger.info(f"✓ CSV esportato: {filepath}")
        return str(filepath)

    def export_to_xlsx(self, results, filename=None):
        """
        Export in Excel con tabelle strutturate

        Args:
            results: Risultati analisi
            filename: Nome file (opzionale)

        Returns:
            Path del file esportato
        """
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        filepath = self.exports_dir / filename

        with pd.ExcelWriter(filepath, engine=XLSX_ENGINE) as writer:
            # Sheet 1: Overview
            overview_data = self._prepare_overview_data(results)
            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='Overview', index=False)

            # Sheet 2: Metriche per Social
            for social_type, data in results.get('social_results', {}).items():
                metrics_data = self._prepare_social_metrics_data(social_type, data)
                if metrics_data:
                    df = pd.DataFrame(metrics_data)
                    sheet_name = social_type.capitalize()[:31]  # Excel limit 31 chars
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Sheet 3: Top Posts
            top_posts_data = self._prepare_top_posts_data(results)
            if top_posts_data:
                df = pd.DataFrame(top_posts_data)
                df.to_excel(writer, sheet_name='Top Posts', index=False)

            # Sheet 4: Commenti RAW (opzionale)
            raw_comments = self._prepare_raw_comments_data(results)
            if raw_comments and len(raw_comments) > 0:
                df = pd.DataFrame(raw_comments)
                df.to_excel(writer, sheet_name='Commenti RAW', index=False)

        self.logger.info(f"✓ XLSX esportato: {filepath}")
        return str(filepath)

    def export_to_pdf(self, results, filename=None):
        """
        Export in PDF con layout simile a dashboard

        Args:
            results: Risultati analisi
            filename: Nome file (opzionale)

        Returns:
            Path del file esportato
        """
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        filepath = self.exports_dir / filename

        # Crea documento
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=PDF_CONFIG['margin_right'],
            leftMargin=PDF_CONFIG['margin_left'],
            topMargin=PDF_CONFIG['margin_top'],
            bottomMargin=PDF_CONFIG['margin_bottom']
        )

        # Elementi del documento
        story = []
        styles = getSampleStyleSheet()

        # Stile custom MOCA
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=PDF_CONFIG['title_size'],
            textColor=rl_colors.HexColor(BRAND_COLORS['primary_red']),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        # Titolo
        brand_name = results.get('brand_name', 'N/A')
        story.append(Paragraph(f"Social Brand Analysis Report", title_style))
        story.append(Paragraph(f"Brand: {brand_name}", styles['Heading2']))
        story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))

        # Overview Table
        story.append(Paragraph("📊 Overview", styles['Heading2']))
        overview_table = self._create_overview_table(results)
        story.append(overview_table)
        story.append(Spacer(1, 20))

        # Metriche per Social
        for social_type, data in results.get('social_results', {}).items():
            story.append(PageBreak())
            story.append(Paragraph(f"📱 {social_type.capitalize()}", styles['Heading2']))

            metrics_table = self._create_metrics_table(data.get('metrics', {}))
            story.append(metrics_table)
            story.append(Spacer(1, 20))

            # Top Posts
            if data.get('metrics', {}).get('top_posts'):
                story.append(Paragraph("🔥 Top Posts", styles['Heading3']))
                top_posts_table = self._create_top_posts_table(data['metrics']['top_posts'])
                story.append(top_posts_table)

        # Build PDF
        doc.build(story)

        self.logger.info(f"✓ PDF esportato: {filepath}")
        return str(filepath)

    def _prepare_overview_data(self, results):
        """Prepara dati overview per Excel"""
        agg = results.get('aggregated_stats', {})

        return [{
            'Brand': results.get('brand_name', 'N/A'),
            'Social Analizzati': agg.get('socials_analyzed', 0),
            'Post Totali': agg.get('total_posts', 0),
            'Commenti Totali': agg.get('total_comments', 0),
            'Likes Totali': agg.get('total_likes', 0),
            'Views Totali': agg.get('total_views', 0)
        }]

    def _prepare_social_metrics_data(self, social_type, data):
        """Prepara dati metriche per singolo social"""
        metrics = data.get('metrics', {})

        return [{
            'Metrica': 'Post Totali',
            'Valore': metrics.get('total_posts', 0)
        }, {
            'Metrica': 'Likes Totali',
            'Valore': metrics.get('total_likes', 0)
        }, {
            'Metrica': 'Commenti Totali',
            'Valore': metrics.get('total_comments', 0)
        }, {
            'Metrica': 'Views Totali',
            'Valore': metrics.get('total_views', 0)
        }, {
            'Metrica': 'Engagement Rate Medio',
            'Valore': f"{metrics.get('avg_engagement_rate', 0):.2f}%"
        }, {
            'Metrica': 'Performance Level',
            'Valore': metrics.get('performance_level', 'N/A')
        }]

    def _prepare_top_posts_data(self, results):
        """Prepara dati top posts per Excel"""
        top_posts = []

        for social_type, data in results.get('social_results', {}).items():
            for post in data.get('metrics', {}).get('top_posts', [])[:10]:
                top_posts.append({
                    'Social': social_type.capitalize(),
                    'URL': post.get('url', 'N/A'),
                    'Caption': post.get('caption', '')[:100],
                    'Likes': post.get('likes', 0),
                    'Commenti': post.get('comments', 0),
                    'Views': post.get('views', 0),
                    'Engagement Rate': f"{post.get('engagement_rate', 0):.2f}%"
                })

        return top_posts

    def _prepare_raw_comments_data(self, results):
        """Prepara commenti RAW per Excel"""
        raw_comments = []

        for social_type, data in results.get('social_results', {}).items():
            for post in data.get('posts', []):
                for comment in post.get('comments', []):
                    raw_comments.append({
                        'Social': social_type.capitalize(),
                        'Post URL': post.get('url', 'N/A'),
                        'Autore': comment.get('author', 'N/A'),
                        'Testo': comment.get('text', ''),
                        'Likes': comment.get('likes', 0),
                        'Timestamp': comment.get('timestamp', 'N/A')
                    })

        return raw_comments

    def _create_overview_table(self, results):
        """Crea tabella overview per PDF"""
        agg = results.get('aggregated_stats', {})

        data = [
            ['Metrica', 'Valore'],
            ['Social Analizzati', str(agg.get('socials_analyzed', 0))],
            ['Post Totali', str(agg.get('total_posts', 0))],
            ['Commenti Totali', str(agg.get('total_comments', 0))],
            ['Likes Totali', f"{agg.get('total_likes', 0):,}"],
            ['Views Totali', f"{agg.get('total_views', 0):,}"]
        ]

        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor(BRAND_COLORS['primary_red'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), rl_colors.white),
            ('GRID', (0, 0), (-1, -1), 1, rl_colors.grey)
        ]))

        return table

    def _create_metrics_table(self, metrics):
        """Crea tabella metriche per PDF"""
        data = [
            ['Metrica', 'Valore'],
            ['Post', str(metrics.get('total_posts', 0))],
            ['Likes', f"{metrics.get('total_likes', 0):,}"],
            ['Commenti', f"{metrics.get('total_comments', 0):,}"],
            ['Engagement Rate', f"{metrics.get('avg_engagement_rate', 0):.2f}%"],
            ['Performance', metrics.get('performance_level', 'N/A')]
        ]

        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor(BRAND_COLORS['light_red'])),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, rl_colors.grey)
        ]))

        return table

    def _create_top_posts_table(self, top_posts):
        """Crea tabella top posts per PDF"""
        data = [['Caption', 'Likes', 'Engagement']]

        for post in top_posts[:5]:
            data.append([
                post.get('caption', '')[:50] + '...',
                str(post.get('likes', 0)),
                f"{post.get('engagement_rate', 0):.1f}%"
            ])

        table = Table(data, colWidths=[250, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor(BRAND_COLORS['gray'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, rl_colors.grey)
        ]))

        return table
