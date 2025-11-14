"""
Analisi AI con OpenAI: sentiment, wordcloud, insight
"""
from openai import OpenAI
from collections import Counter
import re
from config import (
    OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE,
    ITALIAN_STOPWORDS, WORDCLOUD_CONFIG
)
from utils.logger import Logger


class AIAnalyzer:
    """Analizzatore AI per sentiment e insight"""

    def __init__(self, openai_api_key, logger=None):
        """
        Inizializza analyzer

        Args:
            openai_api_key: API key OpenAI
            logger: Logger opzionale
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.logger = logger or Logger.get_logger(self.__class__.__name__)

    def analyze_comments(self, comments, social_type='general'):
        """
        Analisi completa commenti con AI

        Args:
            comments: Lista commenti con 'text'
            social_type: Tipo social per contesto

        Returns:
            Dict con sentiment, wordcloud, insight
        """
        if not comments:
            return self._empty_analysis()

        self.logger.info(f"Analisi AI di {len(comments)} commenti ({social_type})")

        # Estrai solo testo
        texts = [c.get('text', '') for c in comments if c.get('text', '').strip()]

        if not texts:
            return self._empty_analysis()

        # 1. Sentiment Analysis
        sentiment = self._analyze_sentiment(texts)

        # 2. Wordcloud (parole più frequenti)
        wordcloud = self._generate_wordcloud_data(texts)

        # 3. AI Insights
        insights = self._extract_insights(texts, social_type)

        return {
            'sentiment': sentiment,
            'wordcloud': wordcloud,
            'insights': insights,
            'total_analyzed': len(texts)
        }

    def _analyze_sentiment(self, texts):
        """
        Analizza sentiment con OpenAI

        Args:
            texts: Lista testi commenti

        Returns:
            Dict con conteggi sentiment
        """
        self.logger.info("Analizzando sentiment...")

        # Campiona se troppi commenti (per risparmiare token)
        sample_size = min(200, len(texts))
        sample_texts = texts[:sample_size]

        # Batch sentiment analysis
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}

        # Analizza a batch di 20
        batch_size = 20
        for i in range(0, len(sample_texts), batch_size):
            batch = sample_texts[i:i + batch_size]
            batch_sentiments = self._batch_sentiment_analysis(batch)

            for s in batch_sentiments:
                sentiments[s] = sentiments.get(s, 0) + 1

        # Calcola percentuali
        total = sum(sentiments.values())
        if total > 0:
            sentiments['positive_pct'] = round((sentiments['positive'] / total) * 100, 1)
            sentiments['neutral_pct'] = round((sentiments['neutral'] / total) * 100, 1)
            sentiments['negative_pct'] = round((sentiments['negative'] / total) * 100, 1)
        else:
            sentiments['positive_pct'] = 0
            sentiments['neutral_pct'] = 0
            sentiments['negative_pct'] = 0

        self.logger.info(f"✓ Sentiment: {sentiments['positive']} pos, "
                        f"{sentiments['neutral']} neu, {sentiments['negative']} neg")

        return sentiments

    def _batch_sentiment_analysis(self, texts):
        """Analizza sentiment di un batch di testi"""
        try:
            # Crea prompt per batch
            comments_text = "\n".join([f"{i+1}. {text[:200]}" for i, text in enumerate(texts)])

            prompt = f"""Analizza il sentiment di questi commenti e rispondi SOLO con una lista di valori separati da virgola.
Per ogni commento, indica: positive, neutral, o negative.

Commenti:
{comments_text}

Rispondi SOLO con: sentiment1,sentiment2,sentiment3,...
Esempio: positive,neutral,negative,positive"""

            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un analista di sentiment. Rispondi solo con la lista richiesta."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=OPENAI_TEMPERATURE
            )

            result = response.choices[0].message.content.strip()

            # Parse risultati
            sentiments = [s.strip().lower() for s in result.split(',')]

            # Valida
            valid_sentiments = []
            for s in sentiments:
                if s in ['positive', 'neutral', 'negative']:
                    valid_sentiments.append(s)
                else:
                    valid_sentiments.append('neutral')  # Default

            return valid_sentiments

        except Exception as e:
            self.logger.warning(f"Errore batch sentiment: {e}")
            return ['neutral'] * len(texts)

    def _generate_wordcloud_data(self, texts):
        """
        Genera dati per wordcloud

        Args:
            texts: Lista testi

        Returns:
            Lista dict con {word, frequency}
        """
        self.logger.info("Generando wordcloud data...")

        # Combina tutti i testi
        all_text = ' '.join(texts).lower()

        # Pulisci testo
        all_text = re.sub(r'[^\w\s]', ' ', all_text)  # Rimuovi punteggiatura
        all_text = re.sub(r'\d+', '', all_text)  # Rimuovi numeri

        # Tokenizza
        words = all_text.split()

        # Filtra stopwords e parole corte
        filtered_words = [
            word for word in words
            if word not in ITALIAN_STOPWORDS
            and len(word) > 3  # Almeno 4 caratteri
            and not word.startswith(('http', 'www'))
        ]

        # Conta frequenze
        word_counts = Counter(filtered_words).most_common(WORDCLOUD_CONFIG['max_words'])

        wordcloud_data = [
            {'word': word, 'frequency': count}
            for word, count in word_counts
        ]

        self.logger.info(f"✓ Wordcloud: {len(wordcloud_data)} parole uniche")

        return wordcloud_data

    def _extract_insights(self, texts, social_type):
        """
        Estrae insight con OpenAI

        Args:
            texts: Lista testi commenti
            social_type: Tipo social

        Returns:
            Dict con punti forza, debolezza, suggerimenti
        """
        self.logger.info("Estraendo insight con AI...")

        # Campiona commenti rappresentativi
        sample_size = min(100, len(texts))
        sample = texts[:sample_size]

        # Crea prompt
        comments_text = "\n".join([f"- {text}" for text in sample[:50]])  # Max 50 per token limit

        prompt = f"""Analizza questi commenti da {social_type} e fornisci un'analisi strutturata.

Commenti:
{comments_text}

Fornisci la risposta in questo formato esatto:

PUNTI DI FORZA:
- punto 1
- punto 2
- punto 3

PUNTI DI DEBOLEZZA:
- punto 1
- punto 2
- punto 3

SUGGERIMENTI:
- suggerimento 1
- suggerimento 2
- suggerimento 3

TEMI RICORRENTI:
- tema 1
- tema 2
- tema 3"""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un esperto di social media marketing e analisi del sentiment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )

            result = response.choices[0].message.content

            # Parse risultati
            insights = self._parse_insights_response(result)

            self.logger.info("✓ Insight estratti")

            return insights

        except Exception as e:
            self.logger.error(f"Errore estrazione insight: {e}")
            return self._empty_insights()

    def _parse_insights_response(self, response_text):
        """Parse risposta OpenAI per estrarre insight strutturati"""
        insights = {
            'punti_forza': [],
            'punti_debolezza': [],
            'suggerimenti': [],
            'temi_ricorrenti': []
        }

        # Split per sezioni
        sections = {
            'PUNTI DI FORZA:': 'punti_forza',
            'PUNTI DI DEBOLEZZA:': 'punti_debolezza',
            'SUGGERIMENTI:': 'suggerimenti',
            'TEMI RICORRENTI:': 'temi_ricorrenti'
        }

        current_section = None
        for line in response_text.split('\n'):
            line = line.strip()

            # Identifica sezione
            for section_header, section_key in sections.items():
                if section_header in line:
                    current_section = section_key
                    break

            # Aggiungi punto alla sezione corrente
            if current_section and line.startswith('-'):
                point = line[1:].strip()
                if point:
                    insights[current_section].append(point)

        return insights

    def _empty_analysis(self):
        """Analisi vuota"""
        return {
            'sentiment': {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'positive_pct': 0,
                'neutral_pct': 0,
                'negative_pct': 0
            },
            'wordcloud': [],
            'insights': self._empty_insights(),
            'total_analyzed': 0
        }

    def _empty_insights(self):
        """Insight vuoti"""
        return {
            'punti_forza': [],
            'punti_debolezza': [],
            'suggerimenti': [],
            'temi_ricorrenti': []
        }
