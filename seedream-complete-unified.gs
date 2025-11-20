/**
 * Script Apps Script Completo - Seedream + Prompt Wizard + GPT-4o
 * VERSIONE UNIFICATA - Tutte le funzionalità in un unico file
 *
 * Funzionalità:
 * - GPT-4o custom function per formule Google Sheets
 * - Prompt Wizard con generazione batch asincrona
 * - Seedream image generation con batch asincrono
 * - Gestione robusta di trigger, lock e retry
 * - API key configurabili (placeholder o menu)
 *
 * Autore: Claude AI Assistant
 * Versione: 2.0 Unified
 */

// ====================== CONFIGURATION ======================

// PROMPT WIZARD BATCH CONFIG
const PROMPT_BATCH_CONFIG = {
  SIZE: 10,             // Righe per batch
  MAX_RETRIES: 3,       // Tentativi per batch fallito
  RETRY_DELAY_MS: 5000, // Ritardo tra retry
  BATCH_DELAY_MS: 3000  // Ritardo tra batch successivi
};

// SEEDREAM BATCH CONFIG
const SEEDREAM_BATCH_CONFIG = {
  SIZE: 5,              // Immagini per batch
  MAX_RETRIES: 3,       // Tentativi per immagine fallita
  RETRY_DELAY_MS: 5000, // Ritardo tra retry
  BATCH_DELAY_MS: 3000, // Ritardo tra batch
  IMAGE_DELAY_MS: 2000  // Ritardo tra singole immagini
};

const LOCK_TIMEOUT = 300000; // 5 minuti timeout per il lock

// ====================== API KEYS CONFIGURATION ======================
// OPZIONE 1: Inserisci le tue API Key qui (meno sicuro ma più semplice)

// OpenAI API Key (per GPT-4o e Prompt Wizard)
const OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY_HERE';

// Seedream API Key (per generazione immagini)
const SEEDREAM_API_KEY = 'YOUR_SEEDREAM_API_KEY_HERE';

// OPZIONE 2: Lascia vuote le costanti sopra e usa il menu
// "⚙️ Configura API Keys" per salvarle in modo sicuro
//
// Lo script controlla prima le costanti sopra, poi PropertiesService
// =====================================================================

// ====================== MENU ======================
function onOpen() {
  const ui = SpreadsheetApp.getUi();

  ui.createMenu('🎨 Seedream')
    .addItem('🖼️ Genera Immagine', 'generateImageFromSelection')
    .addItem('🖼️ Genera Immagini Batch', 'generateImagesBatch')
    .addSeparator()
    .addItem('⚙️ Configura Seedream', 'configureSeedreamBatchSettings')
    .addItem('🗑️ Cancella Trigger Seedream', 'deleteAllSeedreamTriggers')
    .addToUi();

  ui.createMenu('🧠 Prompt Studio')
    .addItem('✨ Genera Prompt Batch (Wizard)', 'promptWizardStep1')
    .addSeparator()
    .addItem('📊 Stato Processo Prompt', 'showPromptProcessStatus')
    .addItem('🔄 Reset Processo Prompt', 'resetPromptProcess')
    .addToUi();

  ui.createMenu('⚙️ Configurazione')
    .addItem('🔑 Configura API Keys', 'setupApiKeys')
    .addItem('🔑 Configura OpenAI Key', 'setupOpenAIKey')
    .addItem('🔑 Configura Seedream Key', 'setupSeedreamKey')
    .addSeparator()
    .addItem('ℹ️ Info API Keys', 'showApiKeysInfo')
    .addToUi();
}

// ====================== SETUP & UTILITIES ======================

function setupApiKeys() {
  const ui = SpreadsheetApp.getUi();
  const result = ui.alert(
    'Configura API Keys',
    'Vuoi configurare entrambe le API keys (OpenAI e Seedream)?',
    ui.ButtonSet.YES_NO
  );

  if (result === ui.Button.YES) {
    setupOpenAIKey();
    setupSeedreamKey();
  }
}

function setupOpenAIKey() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt(
    'Configura API Key OpenAI',
    'Inserisci la tua API Key OpenAI (per GPT-4o e Prompt Wizard):\n(Verrà salvata in modo sicuro)',
    ui.ButtonSet.OK_CANCEL
  );

  if (response.getSelectedButton() === ui.Button.OK) {
    const apiKey = response.getResponseText().trim();
    if (apiKey) {
      PropertiesService.getScriptProperties().setProperty('OPENAI_API_KEY', apiKey);
      ui.alert('✅ OpenAI API Key salvata con successo!');
    } else {
      ui.alert('❌ API Key non valida.');
    }
  }
}

function setupSeedreamKey() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt(
    'Configura API Key Seedream',
    'Inserisci la tua API Key Seedream (per generazione immagini):\n(Verrà salvata in modo sicuro)',
    ui.ButtonSet.OK_CANCEL
  );

  if (response.getSelectedButton() === ui.Button.OK) {
    const apiKey = response.getResponseText().trim();
    if (apiKey) {
      PropertiesService.getScriptProperties().setProperty('SEEDREAM_API_KEY', apiKey);
      ui.alert('✅ Seedream API Key salvata con successo!');
    } else {
      ui.alert('❌ API Key non valida.');
    }
  }
}

function showApiKeysInfo() {
  const ui = SpreadsheetApp.getUi();
  const props = PropertiesService.getScriptProperties();

  const openAIConfigured = getOpenAIApiKey() && getOpenAIApiKey() !== 'YOUR_OPENAI_API_KEY_HERE';
  const seedreamConfigured = getSeedreamApiKey() && getSeedreamApiKey() !== 'YOUR_SEEDREAM_API_KEY_HERE';

  ui.alert(
    'Stato API Keys',
    `OpenAI API Key: ${openAIConfigured ? '✅ Configurata' : '❌ Non configurata'}\n` +
    `Seedream API Key: ${seedreamConfigured ? '✅ Configurata' : '❌ Non configurata'}\n\n` +
    `Usa il menu "Configura API Keys" per impostarle.`,
    ui.ButtonSet.OK
  );
}

function getOpenAIApiKey() {
  let apiKey = OPENAI_API_KEY;
  if (!apiKey || apiKey === 'YOUR_OPENAI_API_KEY_HERE') {
    apiKey = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');
  }
  return apiKey;
}

function getSeedreamApiKey() {
  let apiKey = SEEDREAM_API_KEY;
  if (!apiKey || apiKey === 'YOUR_SEEDREAM_API_KEY_HERE') {
    apiKey = PropertiesService.getScriptProperties().getProperty('SEEDREAM_API_KEY');
  }
  return apiKey;
}

// ====================== LOCK MANAGEMENT ======================

function acquirePromptLock() {
  const props = PropertiesService.getScriptProperties();
  const lock = props.getProperty("PROMPT_PROCESS_LOCK");
  const now = new Date().getTime();

  if (lock) {
    const lockTime = parseInt(lock, 10);
    if (now - lockTime > LOCK_TIMEOUT) {
      Logger.log("Prompt lock stale rilevato, rilascio forzato");
      releasePromptLock();
      return true;
    }
    return false;
  }

  props.setProperty("PROMPT_PROCESS_LOCK", now.toString());
  return true;
}

function releasePromptLock() {
  PropertiesService.getScriptProperties().deleteProperty("PROMPT_PROCESS_LOCK");
}

function acquireSeedreamLock() {
  const props = PropertiesService.getScriptProperties();
  const lock = props.getProperty("SEEDREAM_PROCESS_LOCK");
  const now = new Date().getTime();

  if (lock) {
    const lockTime = parseInt(lock, 10);
    if (now - lockTime > LOCK_TIMEOUT) {
      Logger.log("Seedream lock stale rilevato, rilascio forzato");
      releaseSeedreamLock();
      return true;
    }
    return false;
  }

  props.setProperty("SEEDREAM_PROCESS_LOCK", now.toString());
  return true;
}

function releaseSeedreamLock() {
  PropertiesService.getScriptProperties().deleteProperty("SEEDREAM_PROCESS_LOCK");
}

// ====================== TRIGGER MANAGEMENT ======================

function cleanupPromptTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'continuePromptBatch') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

function createNextPromptBatchTrigger(delayMs) {
  cleanupPromptTriggers();
  ScriptApp.newTrigger("continuePromptBatch")
    .timeBased()
    .after(delayMs)
    .create();
}

function cleanupSeedreamTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'processNextSeedreamBatch') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

function createNextSeedreamBatchTrigger(delayMs) {
  cleanupSeedreamTriggers();
  ScriptApp.newTrigger("processNextSeedreamBatch")
    .timeBased()
    .after(delayMs)
    .create();
}

function deleteAllSeedreamTriggers() {
  cleanupSeedreamTriggers();
  SpreadsheetApp.getActiveSpreadsheet().toast('✅ Trigger Seedream cancellati', 'Seedream', 3);
}

// ====================== GPT-4o CUSTOM FUNCTION ======================

/**
 * Risponde a query utilizzando il modello GPT-4o di OpenAI basato sui valori delle celle fornite.
 *
 * @param {string} prompt Il prompt di testo a cui l'IA dovrebbe rispondere.
 * @param {...string} refValues I valori delle celle aggiuntive per arricchire il prompt.
 * @return Risposta generata dall'IA basata sul prompt combinato.
 * @customfunction
 */
function GPT4o(prompt, ...refValues) {
  if (!prompt) return "Inserisci un prompt per generare una risposta.";
  if (refValues.length == 0) return "Aggiungi almeno un riferimento per arricchire il prompt.";

  var combinedPrompt = prompt + " " + refValues.join(" ");
  return GPT4oQuery(combinedPrompt);
}

// ====================== PROMPT WIZARD ======================

function resetPromptProcess() {
  const ui = SpreadsheetApp.getUi();
  const confirm = ui.alert(
    'Reset Processo Prompt',
    'Vuoi resettare il processo corrente e cancellare tutti i trigger?',
    ui.ButtonSet.YES_NO
  );

  if (confirm === ui.Button.YES) {
    cleanupPromptTriggers();
    releasePromptLock();
    clearPromptProcessProperties();
    ui.alert('✅ Processo prompt resettato con successo!');
  }
}

function showPromptProcessStatus() {
  const ui = SpreadsheetApp.getUi();
  const props = PropertiesService.getScriptProperties();

  const currentIndex = props.getProperty("PROMPT_CURRENT_INDEX");
  const rowsData = props.getProperty("PROMPT_ROWS_DATA");
  const retryCount = props.getProperty("PROMPT_RETRY_COUNT") || "0";
  const isLocked = props.getProperty("PROMPT_PROCESS_LOCK");

  if (!currentIndex || !rowsData) {
    ui.alert('Nessun processo prompt in corso.');
    return;
  }

  const data = JSON.parse(rowsData);
  const progress = Math.round((parseInt(currentIndex) / data.length) * 100);
  const triggers = ScriptApp.getProjectTriggers().filter(t => t.getHandlerFunction() === 'continuePromptBatch');

  ui.alert(
    'Stato Processo Prompt',
    `Progresso: ${currentIndex} / ${data.length} righe (${progress}%)\n` +
    `Retry correnti: ${retryCount}\n` +
    `Lock attivo: ${isLocked ? 'Sì' : 'No'}\n` +
    `Trigger attivi: ${triggers.length}`,
    ui.ButtonSet.OK
  );
}

function promptWizardStep1() {
  const ui = SpreadsheetApp.getUi();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const promptSheet = ss.getSheetByName('prompt3');

  // Verifica API Key
  const apiKey = getOpenAIApiKey();
  if (!apiKey || apiKey === 'YOUR_OPENAI_API_KEY_HERE') {
    const setup = ui.alert(
      'API Key OpenAI Mancante',
      'Non hai ancora configurato la tua API Key OpenAI.\n\nPuoi:\n1. Inserirla nella costante OPENAI_API_KEY nel codice\n2. Configurarla tramite menu\n\nVuoi configurarla tramite menu ora?',
      ui.ButtonSet.YES_NO
    );
    if (setup === ui.Button.YES) {
      setupOpenAIKey();
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

  const numBatches = Math.ceil(numRows / PROMPT_BATCH_CONFIG.SIZE);
  const estimatedTime = Math.ceil((numBatches * PROMPT_BATCH_CONFIG.BATCH_DELAY_MS) / 1000 / 60);

  const confirm = ui.alert(
    'Conferma Generazione Prompt',
    `Stai per generare ${numRows} prompt in batch di ${PROMPT_BATCH_CONFIG.SIZE} righe.\n` +
    `Prompt base: ${basePrompt.substring(0, 50)}...\n` +
    `Colonne variabili: ${cols.join(', ')}\n` +
    `Numero batch: ${numBatches}\n` +
    `Tempo stimato: ~${estimatedTime} minuti\n\nProcedere?`,
    ui.ButtonSet.YES_NO
  );

  if (confirm !== ui.Button.YES) return;

  startPromptGeneration();
}

function startPromptGeneration() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const data = range.getValues();

  const basePrompt = PropertiesService.getScriptProperties().getProperty("PROMPT_BASE");
  const cols = JSON.parse(PropertiesService.getScriptProperties().getProperty("PROMPT_COLS"));

  cleanupPromptTriggers();

  const props = PropertiesService.getScriptProperties();
  props.setProperty("PROMPT_ROWS_DATA", JSON.stringify(data));
  props.setProperty("PROMPT_BASE_PROMPT", basePrompt);
  props.setProperty("PROMPT_COLS", JSON.stringify(cols));
  props.setProperty("PROMPT_OUTPUT_RANGE", range.getA1Notation());
  props.setProperty("PROMPT_CURRENT_INDEX", "0");
  props.setProperty("PROMPT_RETRY_COUNT", "0");
  props.setProperty("PROMPT_SHEET_NAME", sheet.getName());
  props.setProperty("PROMPT_TOTAL_ROWS", data.length.toString());

  continuePromptBatch();
}

function continuePromptBatch() {
  if (!acquirePromptLock()) {
    Logger.log("Processo prompt già in esecuzione, skip");
    return;
  }

  try {
    const props = PropertiesService.getScriptProperties();
    const data = JSON.parse(props.getProperty("PROMPT_ROWS_DATA"));
    const basePrompt = props.getProperty("PROMPT_BASE_PROMPT");
    const cols = JSON.parse(props.getProperty("PROMPT_COLS"));
    const outputRange = props.getProperty("PROMPT_OUTPUT_RANGE");
    const sheetName = props.getProperty("PROMPT_SHEET_NAME");
    const index = parseInt(props.getProperty("PROMPT_CURRENT_INDEX"), 10);
    const retryCount = parseInt(props.getProperty("PROMPT_RETRY_COUNT") || "0", 10);

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);

    if (!sheet) {
      throw new Error("Foglio non trovato: " + sheetName);
    }

    if (index >= data.length) {
      Logger.log("Generazione prompt completata!");
      cleanupPromptTriggers();
      clearPromptProcessProperties();
      releasePromptLock();

      try {
        SpreadsheetApp.getUi().alert("✅ Generazione prompt completata!");
      } catch (e) {
        Logger.log("Impossibile mostrare alert: " + e.message);
      }
      return;
    }

    const batchEnd = Math.min(index + PROMPT_BATCH_CONFIG.SIZE, data.length);
    const batch = data.slice(index, batchEnd);

    Logger.log(`Processing prompt batch: righe ${index + 1}-${batchEnd} di ${data.length}`);

    const prompts = generatePromptsForBatch(batch, basePrompt, cols);

    const range = sheet.getRange(outputRange);
    const writeValues = prompts.map(p => [p]);
    range.offset(index, 0, writeValues.length, 1).setValues(writeValues);

    props.setProperty("PROMPT_CURRENT_INDEX", batchEnd.toString());
    props.setProperty("PROMPT_RETRY_COUNT", "0");

    Logger.log(`Prompt batch completato. Prossimo indice: ${batchEnd}`);

    releasePromptLock();

    if (batchEnd < data.length) {
      createNextPromptBatchTrigger(PROMPT_BATCH_CONFIG.BATCH_DELAY_MS);
    } else {
      cleanupPromptTriggers();
      clearPromptProcessProperties();
    }

  } catch (error) {
    Logger.log(`Errore nel prompt batch: ${error.message}`);

    const props = PropertiesService.getScriptProperties();
    const retryCount = parseInt(props.getProperty("PROMPT_RETRY_COUNT") || "0", 10);

    releasePromptLock();

    if (retryCount < PROMPT_BATCH_CONFIG.MAX_RETRIES) {
      props.setProperty("PROMPT_RETRY_COUNT", (retryCount + 1).toString());
      Logger.log(`Prompt retry ${retryCount + 1}/${PROMPT_BATCH_CONFIG.MAX_RETRIES}`);

      createNextPromptBatchTrigger(PROMPT_BATCH_CONFIG.RETRY_DELAY_MS);
    } else {
      Logger.log("Troppi prompt retry, processo interrotto");
      cleanupPromptTriggers();

      props.setProperty("PROMPT_LAST_ERROR", error.message);
      props.setProperty("PROMPT_ERROR_TIME", new Date().toString());

      try {
        SpreadsheetApp.getUi().alert(
          `❌ Errore critico al prompt batch:\n${error.message}\n\nProcesso interrotto. Usa 'Reset Processo' per ripartire.`
        );
      } catch (e) {
        Logger.log("Impossibile mostrare alert: " + e.message);
      }
    }
  }
}

function clearPromptProcessProperties() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty("PROMPT_ROWS_DATA");
  props.deleteProperty("PROMPT_BASE_PROMPT");
  props.deleteProperty("PROMPT_COLS");
  props.deleteProperty("PROMPT_OUTPUT_RANGE");
  props.deleteProperty("PROMPT_CURRENT_INDEX");
  props.deleteProperty("PROMPT_RETRY_COUNT");
  props.deleteProperty("PROMPT_SHEET_NAME");
  props.deleteProperty("PROMPT_TOTAL_ROWS");
  props.deleteProperty("PROMPT_LAST_ERROR");
  props.deleteProperty("PROMPT_ERROR_TIME");
}

function generatePromptsForBatch(batch, basePrompt, cols) {
  const rowsData = batch.map((row, i) => {
    const rowData = cols.map(col => {
      const colIndex = col.charCodeAt(0) - 65;
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

  while (prompts.length < batch.length) {
    prompts.push("ERROR: Prompt non generato correttamente");
  }

  return prompts.slice(0, batch.length);
}

// ====================== SEEDREAM IMAGE GENERATION ======================

function generateImageFromSelection() {
  SpreadsheetApp.getUi().alert('🚧 Funzione singola immagine non ancora implementata.\n\nUsa "Genera Immagini Batch" per generare più immagini.');
}

function generateImagesBatch() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const values = range.getValues();
  const ui = SpreadsheetApp.getUi();

  // Verifica API Key
  const apiKey = getSeedreamApiKey();
  if (!apiKey || apiKey === 'YOUR_SEEDREAM_API_KEY_HERE') {
    const setup = ui.alert(
      'API Key Seedream Mancante',
      'Non hai ancora configurato la tua API Key Seedream.\n\nPuoi:\n1. Inserirla nella costante SEEDREAM_API_KEY nel codice\n2. Configurarla tramite menu\n\nVuoi configurarla tramite menu ora?',
      ui.ButtonSet.YES_NO
    );
    if (setup === ui.Button.YES) {
      setupSeedreamKey();
      return;
    } else {
      return;
    }
  }

  const quality = '2K';

  const ratioResponse = ui.prompt(
    'Formato Immagini',
    'Scegli formato per tutte le immagini:\n- 1:1\n- 3:4\n- 4:3\n- 16:9',
    ui.ButtonSet.OK_CANCEL
  );
  if (ratioResponse.getSelectedButton() !== ui.Button.OK) return;
  const ratio = ratioResponse.getResponseText() || '1:1';
  const size = getSizeFromQualityAndRatio_(quality, ratio);

  cleanupSeedreamTriggers();

  const props = PropertiesService.getScriptProperties();
  props.setProperty('SEEDREAM_BATCH_DATA', JSON.stringify(values));
  props.setProperty('SEEDREAM_BATCH_INDEX', '0');
  props.setProperty('SEEDREAM_BATCH_RETRY_COUNT', '0');
  props.setProperty('SEEDREAM_BATCH_RATIO', ratio);
  props.setProperty('SEEDREAM_BATCH_SIZE_FINAL', size);
  props.setProperty('SEEDREAM_BATCH_RANGE', range.getA1Notation());
  props.setProperty('SEEDREAM_BATCH_SHEET_NAME', sheet.getName());

  processNextSeedreamBatch();
}

function processNextSeedreamBatch() {
  if (!acquireSeedreamLock()) {
    Logger.log("Processo Seedream già in esecuzione, skip");
    return;
  }

  try {
    const props = PropertiesService.getScriptProperties();
    const data = JSON.parse(props.getProperty('SEEDREAM_BATCH_DATA'));
    const currentIndex = parseInt(props.getProperty('SEEDREAM_BATCH_INDEX'), 10);
    const retryCount = parseInt(props.getProperty('SEEDREAM_BATCH_RETRY_COUNT') || '0', 10);
    const size = props.getProperty('SEEDREAM_BATCH_SIZE_FINAL');
    const rangeNotation = props.getProperty('SEEDREAM_BATCH_RANGE');
    const sheetName = props.getProperty('SEEDREAM_BATCH_SHEET_NAME');

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
    if (!sheet) {
      throw new Error("Foglio non trovato: " + sheetName);
    }

    const range = sheet.getRange(rangeNotation);
    const API_KEY = getSeedreamApiKey();

    if (currentIndex >= data.length) {
      Logger.log('Generazione immagini Seedream completata!');
      cleanupSeedreamTriggers();
      clearSeedreamProcessProperties();
      releaseSeedreamLock();

      try {
        SpreadsheetApp.getActiveSpreadsheet().toast('✅ Generazione completata!', 'Seedream', 5);
      } catch (e) {
        Logger.log("Impossibile mostrare toast: " + e.message);
      }
      return;
    }

    const batchEnd = Math.min(currentIndex + SEEDREAM_BATCH_CONFIG.SIZE, data.length);
    const batch = data.slice(currentIndex, batchEnd);

    Logger.log(`Processing Seedream batch: immagini ${currentIndex + 1}-${batchEnd} di ${data.length}`);

    const results = [];

    batch.forEach((row, i) => {
      const prompt = row[0];
      if (!prompt || prompt === '') {
        results.push(['']);
        return;
      }
      const result = generateImageWithRetry_(API_KEY, prompt, size, currentIndex + i + 1, data.length);
      results.push([result.success ? result.url : result.error]);
      Utilities.sleep(SEEDREAM_BATCH_CONFIG.IMAGE_DELAY_MS);
    });

    range.offset(currentIndex, 1, results.length, 1).setValues(results);

    props.setProperty('SEEDREAM_BATCH_INDEX', batchEnd.toString());
    props.setProperty('SEEDREAM_BATCH_RETRY_COUNT', '0');

    Logger.log(`Seedream batch completato. Prossimo indice: ${batchEnd}`);

    releaseSeedreamLock();

    if (batchEnd < data.length) {
      createNextSeedreamBatchTrigger(SEEDREAM_BATCH_CONFIG.BATCH_DELAY_MS);
    } else {
      cleanupSeedreamTriggers();
      clearSeedreamProcessProperties();
    }

  } catch (error) {
    Logger.log(`Errore nel Seedream batch: ${error.message}`);

    const props = PropertiesService.getScriptProperties();
    const retryCount = parseInt(props.getProperty('SEEDREAM_BATCH_RETRY_COUNT') || '0', 10);

    releaseSeedreamLock();

    if (retryCount < SEEDREAM_BATCH_CONFIG.MAX_RETRIES) {
      props.setProperty('SEEDREAM_BATCH_RETRY_COUNT', (retryCount + 1).toString());
      Logger.log(`Seedream retry ${retryCount + 1}/${SEEDREAM_BATCH_CONFIG.MAX_RETRIES}`);

      createNextSeedreamBatchTrigger(SEEDREAM_BATCH_CONFIG.RETRY_DELAY_MS);
    } else {
      Logger.log("Troppi Seedream retry, processo interrotto");
      cleanupSeedreamTriggers();

      props.setProperty('SEEDREAM_LAST_ERROR', error.message);
      props.setProperty('SEEDREAM_ERROR_TIME', new Date().toString());

      try {
        SpreadsheetApp.getUi().alert(
          `❌ Errore critico Seedream:\n${error.message}\n\nProcesso interrotto. Cancella trigger e riprova.`
        );
      } catch (e) {
        Logger.log("Impossibile mostrare alert: " + e.message);
      }
    }
  }
}

function clearSeedreamProcessProperties() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('SEEDREAM_BATCH_DATA');
  props.deleteProperty('SEEDREAM_BATCH_INDEX');
  props.deleteProperty('SEEDREAM_BATCH_RETRY_COUNT');
  props.deleteProperty('SEEDREAM_BATCH_RATIO');
  props.deleteProperty('SEEDREAM_BATCH_SIZE_FINAL');
  props.deleteProperty('SEEDREAM_BATCH_RANGE');
  props.deleteProperty('SEEDREAM_BATCH_SHEET_NAME');
  props.deleteProperty('SEEDREAM_LAST_ERROR');
  props.deleteProperty('SEEDREAM_ERROR_TIME');
}

function configureSeedreamBatchSettings() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt(
    'Configurazione Batch Seedream',
    `Configurazione attuale:\n` +
    `- Dimensione batch: ${SEEDREAM_BATCH_CONFIG.SIZE}\n` +
    `- Delay immagini: ${SEEDREAM_BATCH_CONFIG.IMAGE_DELAY_MS}ms\n` +
    `- Delay batch: ${SEEDREAM_BATCH_CONFIG.BATCH_DELAY_MS}ms\n` +
    `- Max retry: ${SEEDREAM_BATCH_CONFIG.MAX_RETRIES}\n` +
    `- Retry delay: ${SEEDREAM_BATCH_CONFIG.RETRY_DELAY_MS}ms\n\n` +
    `Nota: Per modificare, cambia le costanti nel codice.`,
    ui.ButtonSet.OK
  );
}

// ====================== SEEDREAM UTILITIES ======================

function getSizeFromQualityAndRatio_(quality, ratio) {
  const ratioClean = ratio.replace(/\s/g, '');
  const qualityMap = { '2K': 2048, '4K': 4096 };
  const baseSize = qualityMap[quality] || 2048;
  const ratioMap = {
    '1:1': `${baseSize}x${baseSize}`,
    '3:4': `${Math.round(baseSize * 0.75)}x${baseSize}`,
    '4:3': `${baseSize}x${Math.round(baseSize * 0.75)}`,
    '16:9': `${baseSize}x${Math.round(baseSize * 0.5625)}`
  };
  return ratioMap[ratioClean] || ratioMap['1:1'];
}

function generateImageWithRetry_(apiKey, prompt, size, imageNum, totalImages) {
  let lastError;
  for (let attempt = 1; attempt <= SEEDREAM_BATCH_CONFIG.MAX_RETRIES; attempt++) {
    try {
      const url = callSeedreamApi_(apiKey, prompt, size);
      return { success: true, url: url };
    } catch (error) {
      lastError = error;
      if (attempt < SEEDREAM_BATCH_CONFIG.MAX_RETRIES) {
        Utilities.sleep(SEEDREAM_BATCH_CONFIG.RETRY_DELAY_MS);
      }
    }
  }
  return {
    success: false,
    error: `[ERRORE dopo ${SEEDREAM_BATCH_CONFIG.MAX_RETRIES} tentativi: ${lastError.message}]`
  };
}

// ====================== API FUNCTIONS ======================

function GPT4oQuery(prompt) {
  const apiKey = getOpenAIApiKey();

  if (!apiKey || apiKey === 'YOUR_OPENAI_API_KEY_HERE') {
    throw new Error('API Key OpenAI non configurata. Inseriscila nella costante OPENAI_API_KEY o usa il menu "Configura API Keys".');
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

function callSeedreamApi_(apiKey, prompt, size) {
  const endpoint = 'https://ark.ap-southeast.bytepluses.com/api/v3/images/generations';
  const payload = {
    model: 'seedream-4-0-250828',
    prompt: prompt,
    size: size,
    response_format: 'url',
    stream: false,
    watermark: false
  };
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'Authorization': 'Bearer ' + apiKey },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(endpoint, options);
  const statusCode = response.getResponseCode();
  const responseText = response.getContentText();

  if (statusCode !== 200) {
    throw new Error('Seedream API HTTP ' + statusCode + ': ' + responseText);
  }

  const result = JSON.parse(responseText);
  if (!result.data || !result.data[0] || !result.data[0].url) {
    throw new Error('URL non trovato nella risposta Seedream API');
  }

  return result.data[0].url;
}
