# Guida alla Migrazione - Script Apps Script Migliorato

## 🎯 Problemi Risolti

Il tuo script originale aveva questi problemi critici:

### 1. **Trigger Duplicati**
- **Problema**: Ogni esecuzione di `continueBatch()` creava un nuovo trigger senza cancellare quelli precedenti
- **Effetto**: Accumulo di trigger che si eseguono contemporaneamente, causando conflitti e blocchi
- **Soluzione**: Implementata la funzione `cleanupTriggers()` che cancella tutti i trigger esistenti prima di crearne uno nuovo

### 2. **Esecuzioni Concorrenti**
- **Problema**: Nessun meccanismo per prevenire multiple esecuzioni simultanee
- **Effetto**: Due batch che scrivono sulla stessa cella contemporaneamente, dati corrotti
- **Soluzione**: Implementato un sistema di lock con `acquireLock()` e `releaseLock()`

### 3. **Gestione Errori Inadeguata**
- **Problema**: In caso di errore, creava un nuovo trigger senza incrementare l'indice
- **Effetto**: Loop infiniti sullo stesso batch fallito
- **Soluzione**: Contatore di retry (`RETRY_COUNT`) con limite massimo di tentativi

### 4. **API Key Esposta**
- **Problema**: API Key hardcoded nel codice
- **Effetto**: Rischio di sicurezza, difficile aggiornare la key
- **Soluzione**: API Key salvata in `PropertiesService` (criptato)

### 5. **Mancanza di Monitoraggio**
- **Problema**: Impossibile vedere lo stato del processo in esecuzione
- **Effetto**: L'utente non sa se lo script sta funzionando o è bloccato
- **Soluzione**: Funzioni `showProcessStatus()` e `resetProcess()` nel menu

## 🚀 Come Migrare

### Passo 1: Copia il Nuovo Codice
1. Apri il tuo Google Sheets
2. Vai su **Estensioni** → **Apps Script**
3. Sostituisci TUTTO il codice esistente con il contenuto di `seedream-prompt-wizard-improved.gs`
4. Salva (Ctrl+S o Cmd+S)

### Passo 2: Configura l'API Key (IMPORTANTE!)

Hai **2 opzioni** per configurare l'API Key:

#### **OPZIONE A: Nel Codice (Più Semplice)** ⭐
1. In Apps Script, trova la sezione in alto:
```javascript
const OPENAI_API_KEY = 'YOUR_API_KEY_HERE';
```
2. Sostituisci `'YOUR_API_KEY_HERE'` con la tua API Key:
```javascript
const OPENAI_API_KEY = 'sk-proj-abc123...';
```
3. Salva (Ctrl+S)

#### **OPZIONE B: Tramite Menu (Più Sicuro)** 🔒
1. Lascia `OPENAI_API_KEY = 'YOUR_API_KEY_HERE';` nel codice
2. Torna al tuo Google Sheets
3. Apri il menu **🧠 Prompt Studio** → **⚙️ Configura API Key**
4. Inserisci la tua API Key OpenAI
5. Clicca OK

**💡 Quale scegliere?**
- **Opzione A**: Più semplice, key sempre disponibile
- **Opzione B**: Più sicura, key criptata (non visibile nel codice)

**⚠️ IMPORTANTE**: Non condividere mai il tuo script con altri se hai inserito la key nel codice!

### Passo 3: Reset dei Trigger Esistenti
Se hai già eseguito lo script vecchio, potrebbero esserci trigger attivi:

1. Vai su **Estensioni** → **Apps Script**
2. Clicca sull'icona dell'orologio ⏰ (Trigger) nella barra laterale
3. Elimina TUTTI i trigger esistenti per la funzione `continueBatch`
4. Oppure usa il menu **🧠 Prompt Studio** → **🔄 Reset Processo**

### Passo 4: Testa il Nuovo Script
1. Seleziona un piccolo range di celle (es. 5-10 righe)
2. Esegui **🧠 Prompt Studio** → **Genera Prompt Batch (Wizard)**
3. Segui i passaggi del wizard
4. Monitora il progresso con **📊 Stato Processo**

## 🆕 Nuove Funzionalità

### Menu Aggiornato
```
🧠 Prompt Studio
├── Genera Prompt Batch (Wizard)    [Stesso workflow di prima]
├── ⚙️ Configura API Key            [NUOVO - Gestione sicura API key]
├── 🔄 Reset Processo                [NUOVO - Reset in caso di problemi]
└── 📊 Stato Processo                [NUOVO - Vedi progresso in tempo reale]
```

### Monitoraggio in Tempo Reale
Durante l'esecuzione, puoi:
- Cliccare su **📊 Stato Processo** per vedere:
  - Quante righe sono state processate
  - Percentuale di completamento
  - Numero di retry in corso
  - Se il processo è bloccato (lock attivo)
  - Quanti trigger sono attivi

### Gestione Intelligente degli Errori
- **Retry automatico**: Se un batch fallisce, riprova fino a 3 volte
- **Stale lock detection**: Se il processo si blocca per più di 5 minuti, rilascia automaticamente il lock
- **Error logging**: Tutti gli errori vengono salvati nei log (vedi Apps Script → Esecuzioni)

## 🔧 Configurazioni Avanzate

Nel file `seedream-prompt-wizard-improved.gs`, puoi modificare queste costanti:

```javascript
const BATCH_CONFIG = {
  SIZE: 10,             // Righe per batch (aumenta se sei veloce, diminuisci se hai timeout)
  MAX_RETRIES: 3,       // Tentativi prima di arrendersi
  RETRY_DELAY_MS: 5000, // Attesa tra retry (5 secondi)
  BATCH_DELAY_MS: 3000  // Attesa tra batch (3 secondi)
};

const LOCK_TIMEOUT = 300000; // 5 minuti - rilascio lock automatico
```

### Quando Modificare:

**Aumenta `BATCH_SIZE`** se:
- Hai una connessione veloce
- L'API risponde rapidamente
- Vuoi finire più velocemente

**Diminuisci `BATCH_SIZE`** se:
- Hai timeout frequenti
- L'API è lenta
- Ogni prompt è molto complesso

**Aumenta `BATCH_DELAY_MS`** se:
- Hai limiti di rate limiting dall'API OpenAI
- Vuoi essere più conservativo

## 🐛 Risoluzione Problemi

### Problema: "Processo già in esecuzione"
**Soluzione**:
1. Aspetta qualche minuto (potrebbe essere un lock valido)
2. Usa **🔄 Reset Processo** dal menu
3. Controlla i trigger in Apps Script e cancellali manualmente

### Problema: "API Key non configurata"
**Soluzione**:
Usa **⚙️ Configura API Key** dal menu

### Problema: Script si blocca a metà
**Soluzione**:
1. Verifica lo stato con **📊 Stato Processo**
2. Controlla i log in Apps Script → Esecuzioni
3. Se bloccato da più di 5 minuti, usa **🔄 Reset Processo**
4. Riprova con un `BATCH_SIZE` più piccolo

### Problema: "Troppi trigger attivi"
**Soluzione**:
1. Vai in Apps Script → Trigger (icona orologio)
2. Cancella TUTTI i trigger `continueBatch`
3. Usa **🔄 Reset Processo**

### Problema: Prompt generati sono vuoti o "ERROR"
**Soluzione**:
- Verifica che l'API Key sia valida
- Controlla il credito nel tuo account OpenAI
- Guarda i log in Apps Script per vedere l'errore esatto

## 📊 Confronto Versioni

| Funzionalità | Vecchia Versione | Nuova Versione |
|--------------|------------------|----------------|
| Trigger management | ❌ Accumulo trigger | ✅ Pulizia automatica |
| Lock mechanism | ❌ Nessuno | ✅ Presente |
| Retry logic | ⚠️ Loop infiniti | ✅ Max 3 tentativi |
| API Key security | ❌ Hardcoded | ✅ PropertiesService |
| Progress tracking | ❌ Nessuno | ✅ Menu di stato |
| Error handling | ⚠️ Base | ✅ Completo |
| Stale lock recovery | ❌ No | ✅ Auto dopo 5 min |

## ✅ Checklist Migrazione

- [ ] Copiato nuovo codice in Apps Script
- [ ] Salvato il progetto Apps Script
- [ ] Configurata API Key con il menu
- [ ] Cancellati tutti i trigger vecchi
- [ ] Testato su un piccolo range (5-10 righe)
- [ ] Verificato che i prompt vengano generati correttamente
- [ ] Testato su un range più grande

## 🎓 Best Practices

1. **Testa sempre su poche righe prima** di processare centinaia di celle
2. **Monitora il processo** con "Stato Processo" durante l'esecuzione
3. **Non chiudere il browser** durante l'esecuzione (non è necessario, ma è buona pratica tenere il tab aperto)
4. **Controlla i log** in Apps Script → Esecuzioni se qualcosa va storto
5. **Usa Reset Processo** se qualcosa si blocca, invece di creare nuovi trigger manualmente

## 📞 Supporto

Se hai problemi:
1. Controlla i log in Apps Script → Esecuzioni
2. Usa "Stato Processo" per capire dove è bloccato
3. Cerca l'errore nei log e confrontalo con questa guida
4. Come ultima risorsa, usa "Reset Processo" e riparti da zero

## 🔒 Sicurezza API Key

La nuova versione offre **2 modi** per gestire l'API Key:

### Opzione 1: Nel Codice (OPENAI_API_KEY)
```javascript
const OPENAI_API_KEY = 'sk-proj-abc123...';
```
✅ **Pro**: Semplice, sempre disponibile
❌ **Contro**: Visibile nel codice, meno sicuro se condiviso

### Opzione 2: PropertiesService (Menu)
L'API Key viene salvata con `PropertiesService`, che:
- È specifico per il tuo account Google
- Non è visibile nel codice
- È criptato da Google
- Può essere aggiornato facilmente dal menu

✅ **Pro**: Più sicuro, non visibile
❌ **Contro**: Richiede un passo extra di configurazione

**IMPORTANTE - Regole di Sicurezza**:
1. ⚠️ **Non condividere MAI** il codice se contiene la API Key
2. ⚠️ Se usi l'Opzione 1 e condividi il progetto, **rimuovi la key** prima
3. ⚠️ Se hai accidentalmente condiviso la key, **rigenerala subito** su OpenAI
4. ✅ Se usi l'Opzione 2 (PropertiesService), puoi condividere il codice tranquillamente
