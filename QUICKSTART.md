# 🚀 Quick Start - MOCA Social Brand Analyzer

Guida rapida per iniziare in 5 minuti!

---

## ⚡ Setup Rapido (Opzione 1 - Automatico)

```bash
# 1. Esegui script di setup
./setup.sh

# 2. Attiva virtual environment
source venv/bin/activate

# 3. Avvia dashboard
python main.py
```

---

## 🔧 Setup Manuale (Opzione 2)

```bash
# 1. Crea virtual environment
python3 -m venv venv

# 2. Attiva virtual environment
source venv/bin/activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Avvia applicazione
python main.py
```

---

## 🎯 Primo Utilizzo - Dashboard

### 1. Configura API Keys

Nella **sidebar**:
- Inserisci il tuo **Apify API Token**
  - Ottieni qui: https://console.apify.com/account/integrations
- (Opzionale) Inserisci **OpenAI API Key** per analisi AI
  - Ottieni qui: https://platform.openai.com/api-keys

### 2. Configura Analisi

Nel **main panel**:
- **Nome Brand**: es. "Moca Interactive"
- **Social da analizzare**: Seleziona Instagram, TikTok, YouTube
- **Modalità URL**:
  - **Auto-discovery**: Ricerca automatica (consigliato)
  - **Manuale**: Inserisci URL profili
- **Parametri**:
  - Post per social: 10 (consigliato)
  - Commenti per post: 50 (consigliato)

### 3. Avvia Analisi

- Click su **🚀 Avvia Analisi**
- Attendi completamento (1-5 minuti dipende da social e parametri)

### 4. Visualizza Risultati

- **Tab per Social**: Metriche, grafici, top posts per Instagram/TikTok/YouTube
- **Tab Aggregata**: Vista cross-social comparativa
- **AI Analysis** (se abilitata): Sentiment, wordcloud, insights

### 5. Export Risultati

Click su:
- **📄 Esporta PDF**: Report professionale
- **📊 Esporta CSV**: Metriche Excel
- **📑 Esporta XLSX**: File Excel multi-sheet
- **💾 Esporta JSON**: Dati RAW

---

## 💻 Primo Utilizzo - CLI

```bash
# Avvia modalità CLI
python main.py --mode cli

# Segui le istruzioni interattive:
# 1. Inserisci API Keys
# 2. Configura brand e social
# 3. Scegli modalità URL
# 4. Imposta parametri
# 5. Esporta risultati
```

---

## 📊 Esempio Analisi Completa

```bash
# Dashboard (consigliato)
python main.py

# Configurazione esempio:
# - Brand: "Moca Interactive"
# - Social: Instagram + YouTube
# - Auto-discovery: Sì
# - Post per social: 10
# - Commenti: 50
# - AI: Abilitata
```

**Risultati attesi:**
- ✅ 20 post totali analizzati (10 IG + 10 YT)
- ✅ ~1000 commenti raccolti
- ✅ Metriche complete (engagement, likes, views)
- ✅ Sentiment analysis
- ✅ Wordcloud parole chiave
- ✅ Insight strategici AI
- ✅ Export PDF + Excel

**Tempo stimato:** 3-5 minuti

---

## 🆘 Troubleshooting Rapido

### Errore: "Modulo non trovato"
```bash
pip install -r requirements.txt
```

### Errore: "Token non valido"
- Verifica che token Apify inizi con `apify_api_`
- Verifica che token OpenAI inizi con `sk-`

### Dashboard non si apre
```bash
streamlit run views/dashboard_app.py
```

### Scraping fallisce
- Controlla connessione internet
- Verifica crediti Apify: https://console.apify.com/billing
- Riduci numero post/commenti

---

## 📚 Prossimi Passi

1. **Leggi README completo**: `README_NEW.md`
2. **Esplora configurazione**: `config.py`
3. **Personalizza branding**: Modifica colori in `config.py`
4. **Storico analisi**: Vedi `storage/results/`
5. **Export**: Trova file in `storage/exports/`

---

## 💡 Tips

### Performance
- Inizia con **10 post + 50 commenti** per test rapidi
- Aumenta gradualmente per analisi più approfondite
- Auto-discovery è più lento ma più accurato

### AI Analysis
- OpenAI API costa ~$0.002 per 1000 commenti
- Disabilita AI per test rapidi e gratuiti
- Abilita AI per insight strategici avanzati

### Storage
- Ogni analisi viene salvata automaticamente
- Ricarica analisi da dashboard: `Carica Analisi Precedente`
- Export illimitati da analisi salvate

---

## 🎯 Obiettivi Tipici

### Test Veloce (2 min)
```
Brand: Test Brand
Social: 1 social
Post: 5
Commenti: 20
AI: No
```

### Analisi Standard (5 min)
```
Brand: Il tuo brand
Social: 2-3 social
Post: 10
Commenti: 50
AI: Sì
```

### Analisi Approfondita (15 min)
```
Brand: Brand importante
Social: 3 social
Post: 30
Commenti: 100
AI: Sì
```

---

## 📞 Supporto

- Documentazione completa: `README_NEW.md`
- Issues: https://github.com/mocainteractive/social-brand-analyzer/issues
- Email: info@mocainteractive.com

---

**Buona analisi! 🚀**
