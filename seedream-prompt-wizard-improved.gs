/**
 * Script completo Seedream + Prompt Wizard + batch asincrono con trigger
 * VERSIONE MIGLIORATA - Compatibile con grandi quantità di righe
 *
 * Miglioramenti:
 * - Gestione corretta dei trigger (cancellazione automatica)
 * - Lock mechanism per evitare esecuzioni concorrenti
 * - Migliore gestione errori e retry
 * - Progress tracking visibile
 * - API key in PropertiesService (più sicuro)
 */

const BATCH_CONFIG = {
  SIZE: 10,             // Dimensione batch consigliata
  MAX_RETRIES: 3,       // Tentativi per batch fallito
  RETRY_DELAY_MS: 5000, // Ritardo tra retry
  BATCH_DELAY_MS: 3000  // Ritardo tra batch successivi
};

const LOCK_TIMEOUT = 300000; // 5 minuti timeout per il lock

// ====================== MENU ======================
function onOpen() {
  const ui = SpreadsheetApp.getUi();

  ui.createMenu('🎨 Seedream')
    .addItem('Genera Immagine', 'generateImageFromSelection')
    .addItem('Genera Immagini Batch', 'generateImagesBatch')
    .addToUi();

  ui.createMenu('🧠 Prompt Studio')
    .addItem('Genera Prompt Batch (Wizard)', 'promptWizardStep1')
    .addItem('⚙️ Configura API Key', 'setupApiKey')
    .addItem('🔄 Reset Processo', 'resetProcess')
    .addItem('📊 Stato Processo', 'showProcessStatus')
    .addToUi();
}

// ====================== SETUP ======================
function setupApiKey() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt(
    'Configura API Key OpenAI',
    'Inserisci la tua API Key OpenAI:\n(Verrà salvata in modo sicuro)',
    ui.ButtonSet.OK_CANCEL
  );

  if (response.getSelectedButton() === ui.Button.OK) {
    const apiKey = response.getResponseText().trim();
    if (apiKey) {
      PropertiesService.getScriptProperties().setProperty('OPENAI_API_KEY', apiKey);
      ui.alert('API Key salvata con successo!');
    } else {
      ui.alert('API Key non valida.');
    }
  }
}

function resetProcess() {
  const ui = SpreadsheetApp.getUi();
  const confirm = ui.alert(
    'Reset Processo',
    'Vuoi resettare il processo corrente e cancellare tutti i trigger?',
    ui.ButtonSet.YES_NO
  );

  if (confirm === ui.Button.YES) {
    cleanupTriggers();
    releaseLock();
    clearProcessProperties();
    ui.alert('Processo resettato con successo!');
  }
}

function showProcessStatus() {
  const ui = SpreadsheetApp.getUi();
  const props = PropertiesService.getScriptProperties();

  const currentIndex = props.getProperty("CURRENT_INDEX");
  const rowsData = props.getProperty("ROWS_DATA");
  const retryCount = props.getProperty("RETRY_COUNT") || "0";
  const isLocked = props.getProperty("PROCESS_LOCK");

  if (!currentIndex || !rowsData) {
    ui.alert('Nessun processo in corso.');
    return;
  }

  const data = JSON.parse(rowsData);
  const progress = Math.round((parseInt(currentIndex) / data.length) * 100);
  const triggers = ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'continueBatch');

  ui.alert(
    'Stato Processo',
    `Progresso: ${currentIndex} / ${data.length} righe (${progress}%)\n` +
    `Retry correnti: ${retryCount}\n` +
    `Lock attivo: ${isLocked ? 'Sì' : 'No'}\n` +
    `Trigger attivi: ${triggers.length}`,
    ui.ButtonSet.OK
  );
}

// ====================== LOCK MANAGEMENT ======================
function acquireLock() {
  const props = PropertiesService.getScriptProperties();
  const lock = props.getProperty("PROCESS_LOCK");
  const now = new Date().getTime();

  if (lock) {
    const lockTime = parseInt(lock, 10);
    // Se il lock è troppo vecchio, lo rilasciamo (stale lock)
    if (now - lockTime > LOCK_TIMEOUT) {
      Logger.log("Lock stale rilevato, rilascio forzato");
      releaseLock();
      return true;
    }
    return false;
  }

  props.setProperty("PROCESS_LOCK", now.toString());
  return true;
}

function releaseLock() {
  PropertiesService.getScriptProperties().deleteProperty("PROCESS_LOCK");
}

// ====================== TRIGGER MANAGEMENT ======================
function cleanupTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'continueBatch') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

function createNextBatchTrigger(delayMs) {
  // Prima pulisci eventuali trigger esistenti
  cleanupTriggers();

  // Poi crea il nuovo trigger
  ScriptApp.newTrigger("continueBatch")
    .timeBased()
    .after(delayMs)
    .create();
}

// ====================== WIZARD ======================
function promptWizardStep1() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const promptSheet = ss.getSheetByName('prompt3');

  // Verifica API Key
  const apiKey = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');
  if (!apiKey) {
    const setup = ui.alert(
      'API Key Mancante',
      'Non hai ancora configurato la tua API Key OpenAI.\nVuoi configurarla ora?',
      ui.ButtonSet.YES_NO
    );
    if (setup === ui.Button.YES) {
      setupApiKey();
      return;
    } else {
      return;
    }
  }

  if (!promptSheet) {
    ui.alert('Errore: il foglio "prompt3" non esiste!');
    return;
  }

  const basePrompt = promptSheet.getRange('A3').getValue().toString().trim();
  if (!basePrompt) {
    ui.alert('Errore: la cella A3 del foglio "prompt3" è vuota!');
    return;
  }

  PropertiesService.getScriptProperties().setProperty('PROMPT_BASE', basePrompt);
  promptWizardStep2();
}

function promptWizardStep2() {
  const ui = SpreadsheetApp.getUi();
  const sheet = SpreadsheetApp.getActiveSheet();
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];

  const headerList = headers.map((h, i) => `${String.fromCharCode(65 + i)} – ${h}`).join('\n');
  const response = ui.prompt(
    'Seleziona Colonne Variabili',
    'Queste sono le colonne disponibili:\n\n' + headerList + '\n\nInserisci le lettere delle colonne da usare (es: A,C,E):',
    ui.ButtonSet.OK_CANCEL
  );

  if (response.getSelectedButton() !== ui.Button.OK) return;

  const cols = response.getResponseText()
    .toUpperCase()
    .split(',')
    .map(c => c.trim())
    .filter(c => /^[A-Z]$/.test(c));

  if (cols.length === 0) {
    ui.alert('Seleziona almeno una colonna valida.');
    return;
  }

  PropertiesService.getScriptProperties().setProperty('PROMPT_COLS', JSON.stringify(cols));
  promptWizardStep3();
}

function promptWizardStep3() {
  const ui = SpreadsheetApp.getUi();
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const numRows = range.getNumRows();

  const basePrompt = PropertiesService.getScriptProperties().getProperty('PROMPT_BASE');
  const cols = JSON.parse(PropertiesService.getScriptProperties().getProperty('PROMPT_COLS'));

  const numBatches = Math.ceil(numRows / BATCH_CONFIG.SIZE);
  const estimatedTime = Math.ceil((numBatches * BATCH_CONFIG.BATCH_DELAY_MS) / 1000 / 60); // in minuti

  const confirm = ui.alert(
    'Conferma Generazione',
    `Stai per generare ${numRows} prompt in batch di ${BATCH_CONFIG.SIZE} righe.\n` +
    `Prompt base: ${basePrompt.substring(0, 50)}...\n` +
    `Colonne variabili: ${cols.join(', ')}\n` +
    `Numero batch: ${numBatches}\n` +
    `Tempo stimato: ~${estimatedTime} minuti\n\nProcedere?`,
    ui.ButtonSet.YES_NO
  );

  if (confirm !== ui.Button.YES) return;

  startPromptGeneration();
}

// ====================== BATCH ASINCRONO ======================
function startPromptGeneration() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const data = range.getValues();

  const basePrompt = PropertiesService.getScriptProperties().getProperty("PROMPT_BASE");
  const cols = JSON.parse(PropertiesService.getScriptProperties().getProperty("PROMPT_COLS"));

  // Pulisci trigger esistenti
  cleanupTriggers();

  // Resetta le properties
  const props = PropertiesService.getScriptProperties();
  props.setProperty("ROWS_DATA", JSON.stringify(data));
  props.setProperty("BASE_PROMPT", basePrompt);
  props.setProperty("COLS", JSON.stringify(cols));
  props.setProperty("OUTPUT_RANGE", range.getA1Notation());
  props.setProperty("CURRENT_INDEX", "0");
  props.setProperty("RETRY_COUNT", "0");
  props.setProperty("SHEET_NAME", sheet.getName());
  props.setProperty("TOTAL_ROWS", data.length.toString());

  // Avvia il primo batch
  continueBatch();
}

function continueBatch() {
  // Tenta di acquisire il lock
  if (!acquireLock()) {
    Logger.log("Processo già in esecuzione, skip");
    return;
  }

  try {
    const props = PropertiesService.getScriptProperties();
    const data = JSON.parse(props.getProperty("ROWS_DATA"));
    const basePrompt = props.getProperty("BASE_PROMPT");
    const cols = JSON.parse(props.getProperty("COLS"));
    const outputRange = props.getProperty("OUTPUT_RANGE");
    const sheetName = props.getProperty("SHEET_NAME");
    const index = parseInt(props.getProperty("CURRENT_INDEX"), 10);
    const retryCount = parseInt(props.getProperty("RETRY_COUNT") || "0", 10);

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);

    if (!sheet) {
      throw new Error("Foglio non trovato: " + sheetName);
    }

    // Verifica se abbiamo finito
    if (index >= data.length) {
      Logger.log("Generazione completata!");
      cleanupTriggers();
      clearProcessProperties();
      releaseLock();

      // Notifica utente (opzionale, può causare errori se non c'è UI)
      try {
        SpreadsheetApp.getUi().alert("Generazione completata!");
      } catch (e) {
        Logger.log("Impossibile mostrare alert: " + e.message);
      }
      return;
    }

    // Calcola il batch corrente
    const batchEnd = Math.min(index + BATCH_CONFIG.SIZE, data.length);
    const batch = data.slice(index, batchEnd);

    Logger.log(`Processing batch: righe ${index + 1}-${batchEnd} di ${data.length}`);

    // Genera i prompt per questo batch
    const prompts = generatePromptsForBatch(batch, basePrompt, cols);

    // Scrivi i risultati
    const range = sheet.getRange(outputRange);
    const writeValues = prompts.map(p => [p]);
    range.offset(index, 0, writeValues.length, 1).setValues(writeValues);

    // Aggiorna l'indice e resetta retry count
    props.setProperty("CURRENT_INDEX", batchEnd.toString());
    props.setProperty("RETRY_COUNT", "0");

    Logger.log(`Batch completato. Prossimo indice: ${batchEnd}`);

    // Rilascia il lock
    releaseLock();

    // Se ci sono ancora righe da processare, crea il trigger per il prossimo batch
    if (batchEnd < data.length) {
      createNextBatchTrigger(BATCH_CONFIG.BATCH_DELAY_MS);
    } else {
      // Pulizia finale
      cleanupTriggers();
      clearProcessProperties();
    }

  } catch (error) {
    Logger.log(`Errore nel batch: ${error.message}`);

    const props = PropertiesService.getScriptProperties();
    const retryCount = parseInt(props.getProperty("RETRY_COUNT") || "0", 10);

    // Rilascia il lock
    releaseLock();

    if (retryCount < BATCH_CONFIG.MAX_RETRIES) {
      // Incrementa retry count e riprova
      props.setProperty("RETRY_COUNT", (retryCount + 1).toString());
      Logger.log(`Retry ${retryCount + 1}/${BATCH_CONFIG.MAX_RETRIES}`);

      createNextBatchTrigger(BATCH_CONFIG.RETRY_DELAY_MS);
    } else {
      // Troppi retry, ferma il processo
      Logger.log("Troppi retry, processo interrotto");
      cleanupTriggers();

      // Salva lo stato di errore
      props.setProperty("LAST_ERROR", error.message);
      props.setProperty("ERROR_TIME", new Date().toString());

      try {
        SpreadsheetApp.getUi().alert(
          `Errore critico al batch:\n${error.message}\n\nProcesso interrotto. Usa 'Reset Processo' per ripartire.`
        );
      } catch (e) {
        Logger.log("Impossibile mostrare alert: " + e.message);
      }
    }
  }
}

function clearProcessProperties() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty("ROWS_DATA");
  props.deleteProperty("BASE_PROMPT");
  props.deleteProperty("COLS");
  props.deleteProperty("OUTPUT_RANGE");
  props.deleteProperty("CURRENT_INDEX");
  props.deleteProperty("RETRY_COUNT");
  props.deleteProperty("SHEET_NAME");
  props.deleteProperty("TOTAL_ROWS");
  props.deleteProperty("LAST_ERROR");
  props.deleteProperty("ERROR_TIME");
}

// ====================== GENERAZIONE PROMPT ======================
function generatePromptsForBatch(batch, basePrompt, cols) {
  // Costruisci i dati delle righe in base alle colonne selezionate
  const rowsData = batch.map((row, i) => {
    const rowData = cols.map(col => {
      const colIndex = col.charCodeAt(0) - 65; // A=0, B=1, etc.
      return `${col}: ${row[colIndex] || ''}`;
    }).join(', ');
    return `Riga ${i + 1}: ${rowData}`;
  }).join('\n');

  const generationPrompt = `
Genera ${batch.length} prompt di immagine in serie, tutti diversi tra loro.

Regole fondamentali:
- NON ripetere luce, punto di vista, lente o atmosfera in righe consecutive.
- Usa sempre varietà nei materiali, dettagli e contesto.
- Ogni prompt deve iniziare con:
"Immagine fotografica iperrealistica in formato quadrato. Nessun effetto plastico o digitale: resa fotografica naturale, stile editoriale per sito immobiliare di lusso. Non devono comparire persone o scritte di alcun tipo."
- Ogni prompt deve essere composto da 3–5 frasi.
- Deve essere usata una sola delle seguenti categorie in modo variabile:
  tipo di lente / luce / punto di vista / condizione atmosferica.
- Non devono comparire esseri umani o scritte di alcun tipo
- Le luci devono avere distribuzione uniforme.

Prompt base:
${basePrompt}

Dati riga per riga:
${rowsData}

IMPORTANTE: Genera esattamente ${batch.length} prompt separati da "---". Nient'altro.
`;

  const apiResult = GPT4oQuery(generationPrompt);

  const prompts = apiResult
    .split('---')
    .map(p => p.trim())
    .filter(p => p.length > 0);

  // Se non abbiamo abbastanza prompt, riempi con errori
  while (prompts.length < batch.length) {
    prompts.push("ERROR: Prompt non generato correttamente");
  }

  return prompts.slice(0, batch.length);
}

// ====================== GPT-4o API ======================
function GPT4oQuery(prompt) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');

  if (!apiKey) {
    throw new Error('API Key OpenAI non configurata. Usa il menu "Configura API Key".');
  }

  const url = 'https://api.openai.com/v1/chat/completions';

  const payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.7
  };

  const options = {
    "method": "post",
    "contentType": "application/json",
    "headers": {
      "Authorization": "Bearer " + apiKey
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const statusCode = response.getResponseCode();

    if (statusCode !== 200) {
      throw new Error(`API Error ${statusCode}: ${response.getContentText()}`);
    }

    const json = JSON.parse(response.getContentText());
    return json.choices[0].message.content.trim();
  } catch (error) {
    Logger.log(`GPT API Error: ${error.message}`);
    throw error;
  }
}

// ====================== FUNZIONI PLACEHOLDER ======================
// Queste funzioni sono referenziate nel menu ma non erano definite nel codice originale
// Aggiungile se necessario
function generateImageFromSelection() {
  SpreadsheetApp.getUi().alert('Funzione non ancora implementata');
}

function generateImagesBatch() {
  SpreadsheetApp.getUi().alert('Funzione non ancora implementata');
}
