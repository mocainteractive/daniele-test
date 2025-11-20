# Apps Script Files - Guida Rapida

## 🎯 Quale File Usare?

### ⭐ **CONSIGLIATO: Script Unificato**

**File:** `seedream-complete-unified.gs`

✅ **Include tutto:**
- GPT-4o custom function
- Prompt Wizard batch
- Seedream image generation batch

✅ **Vantaggi:**
- 1 solo file da gestire
- API keys configurabili
- Lock mechanism completo
- Trigger management automatico
- Menu organizzato

📖 **Documentazione:** `UNIFIED_SCRIPT_GUIDE.md`

---

### 📁 File Alternativi (Legacy)

#### 1. `seedream-prompt-wizard-improved.gs`
- ✅ Solo Prompt Wizard
- ✅ Miglioramenti applicati (lock, trigger, API key)
- ⚠️ Non include Seedream o GPT4o function

📖 **Documentazione:** `APPSCRIPT_MIGRATION_GUIDE.md`

---

## 🚀 Quick Start

### Per Script Unificato (Consigliato)

1. **Copia il codice:**
   - Apri Google Sheets
   - Estensioni → Apps Script
   - Copia tutto da `seedream-complete-unified.gs`
   - Salva

2. **Configura API Keys:**

   **Opzione A (Semplice):**
   ```javascript
   const OPENAI_API_KEY = 'sk-proj-...';      // Riga 29
   const SEEDREAM_API_KEY = '96524572-...';   // Riga 32
   ```

   **Opzione B (Sicuro):**
   - Menu: ⚙️ Configurazione → 🔑 Configura API Keys

3. **Ricarica il foglio**
   - Chiudi e riapri Google Sheets
   - Vedrai i 3 nuovi menu

4. **Testa:**
   - Formula: `=GPT4o("Test:", A1)`
   - Prompt Wizard: Seleziona celle → 🧠 Prompt Studio
   - Seedream: Seleziona celle → 🎨 Seedream

---

## 📚 Documentazione Completa

### Script Unificato
- **Guida Completa:** `UNIFIED_SCRIPT_GUIDE.md` (tutto quello che ti serve!)
- **Modifiche Applicate:** `UNIFIED_CHANGES.md` (cosa è cambiato rispetto agli script separati)

### Script Legacy (Prompt Wizard)
- **Guida Migrazione:** `APPSCRIPT_MIGRATION_GUIDE.md`
- **Riepilogo Modifiche:** `CHANGES_SUMMARY.md`

---

## 🎨 Menu Disponibili (Script Unificato)

### 🎨 Seedream
- 🖼️ Genera Immagine (WIP)
- 🖼️ Genera Immagini Batch ⭐
- ⚙️ Configura Seedream
- 🗑️ Cancella Trigger Seedream

### 🧠 Prompt Studio
- ✨ Genera Prompt Batch (Wizard) ⭐
- 📊 Stato Processo Prompt
- 🔄 Reset Processo Prompt

### ⚙️ Configurazione
- 🔑 Configura API Keys ⭐
- 🔑 Configura OpenAI Key
- 🔑 Configura Seedream Key
- ℹ️ Info API Keys

---

## ⚡ Funzionalità Principali

### 1. GPT-4o Custom Function
```
=GPT4o("Prompt", A1, B1, ...)
```
Usa OpenAI GPT-4o direttamente nelle formule!

### 2. Prompt Wizard
1. Configura prompt base in foglio "prompt3", cella A3
2. Seleziona range di output
3. 🧠 Prompt Studio → ✨ Genera Prompt Batch
4. Seleziona colonne variabili
5. I prompt vengono generati in batch asincroni

### 3. Seedream Image Generation
1. Seleziona celle con prompt
2. 🎨 Seedream → 🖼️ Genera Immagini Batch
3. Scegli formato (1:1, 3:4, 4:3, 16:9)
4. Le immagini vengono generate in batch
5. URL appaiono nella colonna successiva

---

## 🔒 Sicurezza API Keys

### Opzione A: Nel Codice
```javascript
const OPENAI_API_KEY = 'sk-proj-...';
const SEEDREAM_API_KEY = '96524572-...';
```
✅ Semplice, immediato
❌ Non condividere il codice!

### Opzione B: Tramite Menu
1. ⚙️ Configurazione → 🔑 Configura API Keys
2. Inserisci le chiavi nei popup
3. Salvate in modo sicuro (criptate)

✅ Sicuro, condivisibile
⚠️ Ogni utente configura le sue

**Verifica:** ⚙️ Configurazione → ℹ️ Info API Keys

---

## 🐛 Problemi Comuni

### "API Key non configurata"
→ ⚙️ Configurazione → 🔑 Configura API Keys

### Processo si blocca
→ 🔄 Reset Processo o 🗑️ Cancella Trigger

### Formula GPT4o non funziona
→ Verifica API key OpenAI e credito

### Immagini non vengono generate
→ Verifica API key Seedream

---

## 🔧 Configurazione Avanzata

Modifica queste costanti nel file `.gs`:

```javascript
// Prompt Wizard
const PROMPT_BATCH_CONFIG = {
  SIZE: 10,             // Righe per batch
  MAX_RETRIES: 3,       // Tentativi
  RETRY_DELAY_MS: 5000,
  BATCH_DELAY_MS: 3000
};

// Seedream
const SEEDREAM_BATCH_CONFIG = {
  SIZE: 5,              // Immagini per batch
  MAX_RETRIES: 3,
  RETRY_DELAY_MS: 5000,
  BATCH_DELAY_MS: 3000,
  IMAGE_DELAY_MS: 2000  // Tra immagini
};
```

---

## 📊 Confronto File

| | Unificato | Prompt Wizard (Legacy) |
|---|---|---|
| **GPT4o Function** | ✅ | ❌ |
| **Prompt Wizard** | ✅ | ✅ |
| **Seedream Batch** | ✅ | ❌ |
| **Lock Mechanism** | ✅ Completo | ✅ Solo Prompt |
| **Trigger Cleanup** | ✅ | ✅ |
| **API Key Config** | ✅ Doppia | ✅ Solo OpenAI |
| **Menu** | ✅ 3 organizzati | ✅ 1 solo |

**Raccomandazione:** Usa sempre lo script unificato a meno che tu non abbia bisogno solo del Prompt Wizard.

---

## ✅ Checklist Installazione

Script Unificato:
- [ ] Copiato `seedream-complete-unified.gs`
- [ ] Configurato OpenAI API Key
- [ ] Configurato Seedream API Key
- [ ] Ricaricato foglio
- [ ] Testato GPT4o formula
- [ ] Testato Prompt Wizard
- [ ] Testato Seedream
- [ ] Letto `UNIFIED_SCRIPT_GUIDE.md`

Script Prompt Wizard (solo se serve):
- [ ] Copiato `seedream-prompt-wizard-improved.gs`
- [ ] Configurato OpenAI API Key
- [ ] Ricaricato foglio
- [ ] Testato su piccolo range
- [ ] Letto `APPSCRIPT_MIGRATION_GUIDE.md`

---

## 🎓 Risorse

### Documentazione
- 📘 **Guida Completa Unificato:** `UNIFIED_SCRIPT_GUIDE.md`
- 📗 **Modifiche Unificato:** `UNIFIED_CHANGES.md`
- 📙 **Migrazione Prompt Wizard:** `APPSCRIPT_MIGRATION_GUIDE.md`
- 📕 **Modifiche Prompt Wizard:** `CHANGES_SUMMARY.md`

### Script
- ⭐ **Unificato (Consigliato):** `seedream-complete-unified.gs`
- 📝 **Prompt Wizard (Legacy):** `seedream-prompt-wizard-improved.gs`

### Supporto
- Controlla log: Apps Script → Esecuzioni
- Verifica stato: Menu → Stato Processo
- Leggi troubleshooting nelle guide

---

## 🎉 Pronto!

Scegli lo script che fa per te e inizia! 🚀

**Consiglio:** Inizia con lo **script unificato** per avere tutte le funzionalità.

Happy coding! ✨
