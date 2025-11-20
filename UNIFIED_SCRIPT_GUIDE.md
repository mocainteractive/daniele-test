# Guida Completa - Script Apps Script Unificato

## 📋 Panoramica

Questo script unificato combina **tutte le funzionalità** in un unico file Apps Script:

1. **GPT-4o Custom Function** - Usa GPT-4o direttamente nelle formule di Google Sheets
2. **Prompt Wizard** - Genera prompt AI in batch con wizard guidato
3. **Seedream Image Generator** - Genera immagini AI in batch

**File:** `seedream-complete-unified.gs`

---

## 🎯 Funzionalità Principali

### 1️⃣ GPT-4o Custom Function
Usa GPT-4o come formula nelle celle di Google Sheets:

```
=GPT4o("Scrivi una descrizione per:", A2, B2)
```

**Cosa fa:**
- Combina il prompt con i valori delle celle di riferimento
- Chiama l'API OpenAI GPT-4o-mini
- Restituisce la risposta direttamente nella cella

### 2️⃣ Prompt Wizard
Generazione batch di prompt AI con wizard guidato:

1. Configura il prompt base nel foglio "prompt3", cella A3
2. Seleziona il range di celle dove generare i prompt
3. Menu: **🧠 Prompt Studio** → **✨ Genera Prompt Batch**
4. Segui il wizard per selezionare le colonne variabili
5. Lo script genera i prompt in batch asincroni

**Caratteristiche:**
- Batch di 10 righe (configurabile)
- Lock mechanism per evitare conflitti
- Retry automatico (max 3 tentativi)
- Monitoraggio progresso in tempo reale

### 3️⃣ Seedream Image Generator
Generazione batch di immagini AI con Seedream:

1. Seleziona il range con i prompt nelle celle
2. Menu: **🎨 Seedream** → **🖼️ Genera Immagini Batch**
3. Scegli il formato (1:1, 3:4, 4:3, 16:9)
4. Lo script genera le immagini in batch asincroni
5. Gli URL delle immagini appaiono nella colonna successiva

**Caratteristiche:**
- Batch di 5 immagini (configurabile)
- Qualità 2K o 4K
- Lock mechanism
- Retry automatico per immagini fallite

---

## 🚀 Installazione

### Passo 1: Copia il Codice
1. Apri il tuo Google Sheets
2. **Estensioni** → **Apps Script**
3. Sostituisci tutto il codice esistente con `seedream-complete-unified.gs`
4. Salva (Ctrl+S o Cmd+S)

### Passo 2: Configura le API Keys

Hai **2 opzioni** per ogni API key:

#### **OPZIONE A: Nel Codice** (Più Semplice) ⭐

Trova queste righe in cima al file:

```javascript
// OpenAI API Key (per GPT-4o e Prompt Wizard)
const OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY_HERE';

// Seedream API Key (per generazione immagini)
const SEEDREAM_API_KEY = 'YOUR_SEEDREAM_API_KEY_HERE';
```

Sostituisci i placeholder con le tue chiavi:

```javascript
const OPENAI_API_KEY = 'sk-proj-abc123...';
const SEEDREAM_API_KEY = '96524572-ae47-...';
```

#### **OPZIONE B: Tramite Menu** (Più Sicuro) 🔒

1. Torna a Google Sheets
2. Menu: **⚙️ Configurazione** → **🔑 Configura API Keys**
3. Inserisci entrambe le chiavi nei popup
4. Le chiavi vengono salvate in modo criptato

**💡 Verifica Configurazione:**
Menu: **⚙️ Configurazione** → **ℹ️ Info API Keys**

---

## 📖 Menu Completo

### 🎨 Menu Seedream

| Voce | Descrizione |
|------|-------------|
| 🖼️ Genera Immagine | Genera singola immagine (WIP) |
| 🖼️ Genera Immagini Batch | Genera immagini in batch |
| ⚙️ Configura Seedream | Info configurazione |
| 🗑️ Cancella Trigger Seedream | Pulisci trigger Seedream |

### 🧠 Menu Prompt Studio

| Voce | Descrizione |
|------|-------------|
| ✨ Genera Prompt Batch (Wizard) | Avvia wizard prompt |
| 📊 Stato Processo Prompt | Vedi progresso |
| 🔄 Reset Processo Prompt | Reset processo |

### ⚙️ Menu Configurazione

| Voce | Descrizione |
|------|-------------|
| 🔑 Configura API Keys | Configura entrambe |
| 🔑 Configura OpenAI Key | Solo OpenAI |
| 🔑 Configura Seedream Key | Solo Seedream |
| ℹ️ Info API Keys | Verifica stato |

---

## 🔧 Configurazione Avanzata

### Batch Config - Prompt Wizard

```javascript
const PROMPT_BATCH_CONFIG = {
  SIZE: 10,             // ← Righe per batch
  MAX_RETRIES: 3,       // ← Tentativi massimi
  RETRY_DELAY_MS: 5000, // ← Attesa tra retry (5s)
  BATCH_DELAY_MS: 3000  // ← Attesa tra batch (3s)
};
```

**Quando modificare:**
- `SIZE: 5` se hai timeout frequenti
- `SIZE: 20` se tutto va veloce
- `BATCH_DELAY_MS: 5000` se hai rate limiting

### Batch Config - Seedream

```javascript
const SEEDREAM_BATCH_CONFIG = {
  SIZE: 5,              // ← Immagini per batch
  MAX_RETRIES: 3,       // ← Tentativi per immagine
  RETRY_DELAY_MS: 5000, // ← Attesa tra retry
  BATCH_DELAY_MS: 3000, // ← Attesa tra batch
  IMAGE_DELAY_MS: 2000  // ← Attesa tra immagini
};
```

**Quando modificare:**
- `SIZE: 3` se Seedream API è lenta
- `IMAGE_DELAY_MS: 3000` per evitare rate limiting
- `BATCH_DELAY_MS: 5000` per processamento più conservativo

### Lock Timeout

```javascript
const LOCK_TIMEOUT = 300000; // 5 minuti
```

Rilascio automatico del lock se un processo si blocca per più di 5 minuti.

---

## 📝 Esempi d'Uso

### Esempio 1: GPT-4o Formula

**Setup:**
| A | B | C |
|---|---|---|
| Nome | Città | Descrizione |
| Mario Rossi | Milano | =GPT4o("Scrivi una bio per:", A2, B2) |

**Risultato in C2:**
> "Mario Rossi è un professionista di Milano con esperienza..."

### Esempio 2: Prompt Wizard

**Setup foglio "prompt3":**
```
A3: "Genera una descrizione per una casa di lusso con le seguenti caratteristiche:"
```

**Setup foglio dati:**
| A | B | C | D (Risultato) |
|---|---|---|---|
| Tipo | Mq | Zona | [vuoto - qui verranno i prompt] |
| Villa | 200 | Centro | |
| Attico | 150 | Collina | |

**Esecuzione:**
1. Seleziona D2:D3
2. **🧠 Prompt Studio** → **✨ Genera Prompt Batch**
3. Inserisci colonne: `A,B,C`
4. Conferma

**Risultato:**
I prompt generati appariranno in D2:D3

### Esempio 3: Seedream Batch

**Setup:**
| A (Prompt) | B (Immagine) |
|------------|--------------|
| Modern luxury villa with pool | [vuoto] |
| Cozy apartment with city view | [vuoto] |

**Esecuzione:**
1. Seleziona A2:A3
2. **🎨 Seedream** → **🖼️ Genera Immagini Batch**
3. Scegli formato: `16:9`
4. Conferma

**Risultato:**
Gli URL delle immagini appariranno in B2:B3

---

## 🐛 Risoluzione Problemi

### Problema: "API Key non configurata"

**Soluzione:**
1. Verifica con: **⚙️ Configurazione** → **ℹ️ Info API Keys**
2. Se mancante, configura con: **🔑 Configura API Keys**
3. Oppure inserisci nel codice (riga 29-32)

### Problema: Formula GPT4o restituisce errore

**Cause possibili:**
- API Key OpenAI non configurata
- Credito OpenAI esaurito
- Prompt troppo lungo (limite API)

**Soluzione:**
1. Verifica API key con **ℹ️ Info API Keys**
2. Controlla credito su platform.openai.com
3. Riduci la lunghezza del prompt

### Problema: Processo si blocca a metà

**Per Prompt Wizard:**
1. **📊 Stato Processo Prompt** per vedere dove si è fermato
2. **🔄 Reset Processo Prompt** se bloccato
3. Controlla log: Apps Script → Esecuzioni

**Per Seedream:**
1. **🗑️ Cancella Trigger Seedream**
2. Controlla log: Apps Script → Esecuzioni
3. Riprova con batch più piccoli

### Problema: "Processo già in esecuzione"

**Causa:** Lock attivo da processo precedente

**Soluzione:**
1. Aspetta 5 minuti (auto-rilascio)
2. Oppure usa **🔄 Reset Processo**
3. Oppure **🗑️ Cancella Trigger**

### Problema: Troppi trigger attivi

**Soluzione:**
1. Apps Script → Trigger (icona orologio ⏰)
2. Cancella tutti i trigger `continuePromptBatch` e `processNextSeedreamBatch`
3. Oppure usa i menu di reset

---

## 🔒 Sicurezza

### API Keys - Best Practices

**✅ Cosa FARE:**
- Usa Opzione B (menu) se condividi il progetto
- Rigenera le key se le hai condivise accidentalmente
- Monitora l'uso sul dashboard OpenAI/Seedream

**❌ Cosa NON FARE:**
- Non commettere il file con le key nel codice su GitHub pubblico
- Non condividere lo script con le key hardcoded
- Non usare key con permessi illimitati

### Opzione A vs Opzione B

| | Opzione A (Codice) | Opzione B (Menu) |
|---|---|---|
| **Sicurezza** | ⚠️ Visibile | ✅ Criptata |
| **Facilità** | ✅ Immediata | ⚠️ Setup extra |
| **Condivisione** | ❌ Rimuovi prima | ✅ Safe |
| **Best per** | Uso personale | Team/progetti |

---

## 📊 Confronto con Versione Precedente

| Funzionalità | Vecchia | Unificata |
|--------------|---------|-----------|
| File separati | ✅ 3 file | ✅ 1 file |
| API key hardcoded | ❌ Sempre | ⚠️ Opzionale |
| Lock mechanism | ❌ Solo Prompt | ✅ Entrambi |
| Trigger cleanup | ❌ Nessuno | ✅ Automatico |
| Retry intelligente | ⚠️ Parziale | ✅ Completo |
| Menu unificato | ❌ No | ✅ Sì |
| Monitoraggio | ⚠️ Solo Prompt | ✅ Entrambi |
| Configurazione | ❌ Sparsa | ✅ Centralizzata |

---

## 🎓 Best Practices

### 1. Testa Prima su Piccoli Range
- GPT4o: Prova su 2-3 celle prima
- Prompt Wizard: Testa su 5-10 righe
- Seedream: Inizia con 2-3 immagini

### 2. Monitora i Processi
- Usa **📊 Stato Processo** durante l'esecuzione
- Controlla i log in Apps Script → Esecuzioni
- Non chiudere il browser durante processi lunghi

### 3. Gestione Errori
- Se un batch fallisce, controlla i log prima di riprovare
- Usa reset se il processo è bloccato da più di 5 minuti
- Riduci il batch size se hai problemi frequenti

### 4. Ottimizzazione
- Aumenta batch size gradualmente se tutto funziona
- Aumenta delay se hai rate limiting
- Monitora i costi API (OpenAI e Seedream hanno dashboard)

### 5. Backup
- Fai backup del foglio prima di grandi batch
- Salva versioni intermedie durante test
- Tieni traccia delle configurazioni che funzionano

---

## 🔄 Migrazione dalla Versione Precedente

Se hai già usato gli script separati:

### Step 1: Backup
1. Esporta il tuo Google Sheets attuale
2. Copia gli script vecchi in un file di backup

### Step 2: Pulizia
1. Apps Script → Trigger → Cancella TUTTI i trigger
2. Apps Script → Cancella tutto il codice vecchio

### Step 3: Installazione
1. Copia `seedream-complete-unified.gs` completo
2. Configura le API keys (vedi sopra)
3. Salva e ricarica il foglio

### Step 4: Test
1. Testa GPT4o con una formula semplice
2. Testa Prompt Wizard su 3-5 righe
3. Testa Seedream su 1-2 immagini

### Step 5: Produzione
Una volta che tutto funziona, puoi usare su range più grandi

---

## 💡 Tips & Tricks

### GPT4o Formula
```
// Prompt semplice
=GPT4o("Traduci in inglese:", A2)

// Prompt con contesto
=GPT4o("Scrivi meta description per:", A2, B2, C2)

// Prompt lungo
=GPT4o("Come esperto SEO, scrivi una meta description coinvolgente per questo prodotto:", A2)
```

### Prompt Wizard - Colonne Multiple
```
Colonne: A,B,C,E
Salta D se non serve
```

### Seedream - Formati Immagine
- **1:1** - Quadrato (Instagram post)
- **3:4** - Verticale (Instagram story)
- **4:3** - Orizzontale classico
- **16:9** - Widescreen (YouTube thumbnail)

---

## 📞 Supporto

### Controlla Prima:
1. Log in Apps Script → Esecuzioni
2. Stato con **📊 Stato Processo** o **ℹ️ Info API Keys**
3. Questa guida nella sezione "Risoluzione Problemi"

### Se Persiste:
1. Usa **🔄 Reset Processo** o **🗑️ Cancella Trigger**
2. Riavvia il browser
3. Prova con batch più piccoli
4. Verifica credito API

---

## ✅ Checklist Installazione

- [ ] Copiato codice unificato in Apps Script
- [ ] Salvato il progetto Apps Script
- [ ] Configurata OpenAI API Key
- [ ] Configurata Seedream API Key
- [ ] Verificato con "Info API Keys"
- [ ] Ricaricato il foglio Google Sheets
- [ ] Testato formula GPT4o (1 cella)
- [ ] Testato Prompt Wizard (3-5 righe)
- [ ] Testato Seedream (1-2 immagini)
- [ ] Tutto funziona! 🎉

---

## 🎉 Pronto all'Uso!

Ora hai un sistema completo e robusto per:
- ✅ Usare AI nelle formule
- ✅ Generare prompt in batch
- ✅ Generare immagini in batch
- ✅ Gestione automatica di errori e retry
- ✅ Monitoraggio in tempo reale

**Happy scripting! 🚀**
