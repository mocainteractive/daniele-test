# 🎯 MOCA Social Brand Analyzer

**Analisi Completa dei Brand sui Social Media**

Strumento professionale per analizzare automaticamente i post e i commenti di un brand su Instagram, TikTok e YouTube, con analisi AI avanzata di sentiment, wordcloud e insight strategici.

---

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Requisiti](#-requisiti)
- [Installazione](#-installazione)
- [Utilizzo](#-utilizzo)
- [Architettura](#-architettura)
- [API e Servizi](#-api-e-servizi)
- [Export](#-export)
- [Configurazione](#-configurazione)

---

## ✨ Caratteristiche

### 🔍 Auto-Discovery
- Ricerca automatica profili social del brand via Google Search
- Supporto inserimento manuale URL
- Validazione URL automatica

### 📊 Scraping Multi-Social
- **Instagram**: Post + Commenti (via `apify/instagram-scraper`)
- **TikTok**: Video + Commenti (via `clockworks/tiktok-scraper` + `clockworks/tiktok-comments-scraper`)
- **YouTube**: Video + Commenti (via `streamers/youtube-scraper` + `streamers/youtube-comments-scraper`)

### 📈 Analisi Metriche
- **KPI Principali**: Likes, commenti, share, views, engagement rate
- **Metriche Aggregate**: Cross-social comparison
- **Top Content**: Post più performanti con thumbnail
- **Hashtag Analysis**: Top hashtags utilizzati
- **Content Type Distribution**: Analisi tipologia contenuti

### 🤖 Analisi AI (Opzionale)
- **Sentiment Analysis**: Positivo/Neutro/Negativo con percentuali
- **Word Cloud**: Parole più ricorrenti (con rimozione stopwords italiane)
- **AI Insights**:
  - Punti di forza
  - Punti di debolezza
  - Suggerimenti strategici
  - Temi ricorrenti

### 📥 Export Multi-Formato
- **PDF**: Report professionale con layout MOCA
- **CSV**: Metriche esportabili
- **XLSX**: Tabelle strutturate multi-sheet
- **JSON**: Dati RAW completi

### 💾 Storico Analisi
- Salvataggio automatico analisi
- Ricaricamento analisi precedenti
- Filtro per brand e data
- Export storico CSV

### 🎨 Dashboard Interattiva
- UI moderna con Streamlit
- Tabs per social + vista aggregata
- Grafici interattivi Plotly
- Design brand MOCA (colori, logo, font)
- Dark/Light mode ready

### ⚡ Performance
- Progress bar dinamica
- Scraping in batch ottimizzato
- Retry automatico con exponential backoff
- Rate limiting intelligente
- Logging dettagliato

---

## 🔧 Requisiti

### Sistema
- **macOS** 10.14+ (Mojave o successivo)
- Python 3.8+
- 4GB RAM minimo
- Connessione internet stabile

### API Keys
- **Apify API Token** (obbligatorio) - [Ottieni qui](https://console.apify.com/account/integrations)
- **OpenAI API Key** (opzionale, per analisi AI) - [Ottieni qui](https://platform.openai.com/api-keys)

---

## 📦 Installazione

### 1. Clone Repository

```bash
git clone https://github.com/mocainteractive/social-brand-analyzer.git
cd social-brand-analyzer
```

### 2. Crea Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 4. Verifica Installazione

```bash
python main.py --version
```

---

## 🚀 Utilizzo

### Modalità 1: Dashboard Web (Consigliata)

Avvia la dashboard interattiva:

```bash
python main.py --mode dashboard
```

La dashboard si aprirà automaticamente su `http://localhost:8501`

**Workflow Dashboard:**

1. **Sidebar**: Inserisci API Keys (Apify + OpenAI opzionale)
2. **Configurazione**:
   - Nome brand
   - Selezione social (Instagram/TikTok/YouTube)
   - Modalità URL (auto-discovery o manuale)
   - Parametri scraping (post per social, commenti per post)
3. **Avvia Analisi**: Click su "🚀 Avvia Analisi"
4. **Visualizza Risultati**: Tabs per social + vista aggregata
5. **Export**: PDF, CSV, XLSX, JSON

### Modalità 2: CLI Interattiva

Avvia modalità terminale:

```bash
python main.py --mode cli
```

Segui le istruzioni interattive per:
- Inserire API keys
- Configurare brand e social
- Scegliere modalità URL
- Impostare parametri scraping
- Esportare risultati

### Esempio Rapido

```bash
# Dashboard (default)
python main.py

# CLI
python main.py --mode cli
```

---

## 🏗️ Architettura

Il progetto segue il pattern **MVC** (Model-View-Controller):

```
social-brand-analyzer/
│
├── main.py                      # Entry point
├── config.py                    # Configurazione centralizzata
├── requirements.txt
│
├── models/                      # MODEL - Business Logic
│   ├── scrapers/               # Scraping logic
│   │   ├── base_scraper.py    # Classe astratta (DRY)
│   │   ├── instagram_scraper.py
│   │   ├── tiktok_scraper.py
│   │   └── youtube_scraper.py
│   │
│   ├── analyzers/              # Analisi & AI
│   │   ├── metrics_calculator.py
│   │   └── ai_analyzer.py
│   │
│   └── storage/                # Persistenza
│       └── storage_manager.py
│
├── controllers/                 # CONTROLLER - Orchestrazione
│   ├── orchestrator.py         # Orchestratore principale
│   ├── url_finder.py           # Auto-discovery URL
│   └── export_manager.py       # Export multi-formato
│
├── views/                       # VIEW - UI/Dashboard
│   ├── dashboard_app.py        # Dashboard Streamlit
│   └── components/             # Componenti riusabili
│       ├── metrics_display.py
│       └── ai_display.py
│
├── utils/                       # Utilities
│   ├── colors.py               # Colori brand MOCA
│   ├── logger.py               # Logging centralizzato
│   ├── progress_tracker.py     # Progress bar dinamica
│   └── validators.py           # Validatori input
│
└── storage/                     # Storage locale
    ├── results/                # Analisi salvate
    └── exports/                # File esportati
```

### Principi Architetturali

- **KISS**: Soluzioni semplici e dirette
- **DRY**: Componenti riusabili (base_scraper, UI components)
- **Separation of Concerns**: MVC chiaro
- **Single Responsibility**: Ogni classe ha un compito preciso

---

## 🔌 API e Servizi

### Apify Actors Utilizzati

| Social    | Actor                                  | Scopo           |
|-----------|----------------------------------------|-----------------|
| Instagram | `apify/instagram-scraper`             | Post + Commenti |
| TikTok    | `clockworks/tiktok-scraper`           | Video           |
| TikTok    | `clockworks/tiktok-comments-scraper`  | Commenti        |
| YouTube   | `streamers/youtube-scraper`           | Video           |
| YouTube   | `streamers/youtube-comments-scraper`  | Commenti        |
| Search    | `apify/google-search-scraper`         | Auto-discovery  |

### OpenAI (Opzionale)

- **Modello**: `gpt-4o-mini` (economico e veloce)
- **Utilizzo**:
  - Sentiment analysis batch
  - Estrazione insight strategici
  - Categorizzazione temi

---

## 📥 Export

### Formati Supportati

#### 1. PDF
- Report professionale multi-pagina
- Layout brand MOCA (colori, logo)
- Tabelle metriche
- Top posts con thumbnail
- Sezione per ogni social

#### 2. CSV
- Metriche aggregate per social
- Compatibile Excel (UTF-8 BOM)
- Formato: Brand, Social, Post, Commenti, Likes, ER

#### 3. XLSX
- Multi-sheet Excel
- Sheets:
  - Overview
  - Instagram / TikTok / YouTube
  - Top Posts
  - Commenti RAW
- Formattazione tabelle

#### 4. JSON
- Dati RAW completi
- Struttura gerarchica
- Include metadata e timestamp

### Posizione File

Tutti gli export vengono salvati in:

```
storage/exports/
├── report_20240101_120000.pdf
├── metrics_20240101_120000.csv
├── report_20240101_120000.xlsx
└── data_20240101_120000.json
```

---

## ⚙️ Configurazione

### File: `config.py`

Personalizza parametri in `config.py`:

#### Brand Colors
```python
BRAND_COLORS = {
    'primary_red': '#E52217',
    'light_red': '#FFE7E6',
    'black': '#191919',
    'gray': '#8A8A8A'
}
```

#### Scraping Defaults
```python
DEFAULT_MAX_POSTS = 10
DEFAULT_MAX_COMMENTS = 50
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # secondi
```

#### AI Settings
```python
OPENAI_MODEL = 'gpt-4o-mini'
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.3
```

#### Wordcloud
```python
WORDCLOUD_CONFIG = {
    'width': 1200,
    'height': 600,
    'background_color': 'white',
    'colormap': 'Reds',  # Tema MOCA
    'max_words': 100
}
```

---

## 🐛 Troubleshooting

### Errore: "Token Apify non valido"
- Verifica che il token inizi con `apify_api_`
- Controlla su [Apify Console](https://console.apify.com/account/integrations)

### Errore: "Modulo streamlit non trovato"
```bash
pip install -r requirements.txt
```

### Dashboard non si apre
```bash
streamlit run views/dashboard_app.py
```

### Scraping fallisce
- Verifica connessione internet
- Controlla crediti Apify rimanenti
- Riduci numero post/commenti

---

## 📊 Metriche Calcolate

### Post Metrics
- **Total Posts**: Numero post analizzati
- **Total Likes**: Somma likes
- **Total Comments**: Somma commenti
- **Total Shares**: Somma condivisioni
- **Total Views**: Somma visualizzazioni
- **Avg Engagement Rate**: `((likes + comments + shares) / views) * 100`

### Performance Levels
- **Low**: < 1% engagement
- **Medium**: 1-3% engagement
- **High**: 3-5% engagement
- **Excellent**: > 5% engagement

### Comment Metrics
- Total commenti
- Lunghezza media commento
- Likes sui commenti
- Top commentatori

---

## 🎨 Branding MOCA

### Colori
- **Rosso Primario**: `#E52217`
- **Rosso Chiaro**: `#FFE7E6`
- **Nero**: `#191919`
- **Grigio**: `#8A8A8A`

### Font
- **Principale**: Figtree
- **Fallback**: Helvetica, Arial

### Logo
- Favicon: [MOCA Logo](https://mocainteractive.com/wp-content/uploads/2025/04/cropped-moca-instagram-icona-1-192x192.png)

---

## 📝 Licenza

© 2024 MOCA Interactive. Tutti i diritti riservati.

---

## 🤝 Supporto

Per domande o supporto:
- Email: info@mocainteractive.com
- Website: https://mocainteractive.com

---

## 🚀 Roadmap Future

- [ ] Supporto Facebook Pages
- [ ] Supporto LinkedIn Company
- [ ] Export PowerPoint
- [ ] Scheduler analisi automatiche
- [ ] API REST per integrazione
- [ ] App macOS standalone (PyInstaller)
- [ ] Multi-brand comparison
- [ ] Historical trend analysis

---

**Fatto con ❤️ da MOCA Interactive**
