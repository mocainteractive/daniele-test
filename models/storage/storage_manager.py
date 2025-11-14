"""
Gestione storage e storico delle analisi
"""
import json
import csv
from datetime import datetime
from pathlib import Path
import uuid
from config import RESULTS_DIR, EXPORTS_DIR, CSV_ENCODING
from utils.logger import Logger


class StorageManager:
    """Manager per salvataggio e caricamento analisi"""

    def __init__(self, storage_dir=None, logger=None):
        """
        Inizializza storage manager

        Args:
            storage_dir: Directory storage (default da config)
            logger: Logger opzionale
        """
        self.results_dir = Path(storage_dir) if storage_dir else RESULTS_DIR
        self.exports_dir = EXPORTS_DIR
        self.logger = logger or Logger.get_logger(self.__class__.__name__)

        # Crea cartelle se non esistono
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def save_analysis(self, brand_name, social_urls, results, enable_ai=False):
        """
        Salva analisi completa

        Args:
            brand_name: Nome brand
            social_urls: Dict URL social
            results: Risultati completi
            enable_ai: Se AI era abilitata

        Returns:
            analysis_id: ID univoco analisi
        """
        analysis_id = self._generate_analysis_id()

        analysis_data = {
            'id': analysis_id,
            'timestamp': datetime.now().isoformat(),
            'brand_name': brand_name,
            'social_urls': social_urls,
            'ai_enabled': enable_ai,
            'results': results
        }

        # Salva file JSON
        filepath = self.results_dir / f"{analysis_id}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"✓ Analisi salvata: {filepath}")

        # Aggiorna indice
        self._update_index(analysis_data)

        return analysis_id

    def load_analysis(self, analysis_id):
        """
        Carica analisi da ID

        Args:
            analysis_id: ID analisi

        Returns:
            Dict con dati analisi o None
        """
        filepath = self.results_dir / f"{analysis_id}.json"

        if not filepath.exists():
            self.logger.error(f"Analisi {analysis_id} non trovata")
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.logger.info(f"✓ Analisi caricata: {analysis_id}")
        return data

    def list_analyses(self, brand_name=None, limit=None):
        """
        Lista tutte le analisi salvate

        Args:
            brand_name: Filtra per brand (opzionale)
            limit: Limita risultati (opzionale)

        Returns:
            Lista analisi ordinate per data (più recenti prima)
        """
        index = self._load_index()

        # Filtra per brand se specificato
        if brand_name:
            index = [a for a in index if a.get('brand_name', '').lower() == brand_name.lower()]

        # Ordina per timestamp (più recenti prima)
        index.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Limita se richiesto
        if limit:
            index = index[:limit]

        return index

    def delete_analysis(self, analysis_id):
        """
        Elimina analisi

        Args:
            analysis_id: ID analisi

        Returns:
            bool: True se eliminata
        """
        filepath = self.results_dir / f"{analysis_id}.json"

        if not filepath.exists():
            self.logger.error(f"Analisi {analysis_id} non trovata")
            return False

        # Elimina file
        filepath.unlink()

        # Aggiorna indice
        self._remove_from_index(analysis_id)

        self.logger.info(f"✓ Analisi eliminata: {analysis_id}")
        return True

    def export_history_csv(self, output_filename=None):
        """
        Esporta storico analisi in CSV

        Args:
            output_filename: Nome file output (opzionale)

        Returns:
            Path del file esportato
        """
        if not output_filename:
            output_filename = f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        output_path = self.exports_dir / output_filename

        # Carica tutte le analisi
        all_analyses = self.list_analyses()

        # Scrivi CSV
        with open(output_path, 'w', encoding=CSV_ENCODING, newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'ID',
                'Data',
                'Brand',
                'Social',
                'Post Totali',
                'Commenti Totali',
                'Likes Totali',
                'Engagement Rate',
                'AI Abilitata'
            ])

            # Dati
            for analysis in all_analyses:
                # Carica dati completi
                full_data = self.load_analysis(analysis['id'])
                if not full_data:
                    continue

                results = full_data.get('results', {})
                agg_stats = results.get('aggregated_stats', {})

                writer.writerow([
                    analysis['id'],
                    analysis.get('timestamp', 'N/A'),
                    analysis.get('brand_name', 'N/A'),
                    ', '.join(analysis.get('social_urls', {}).keys()),
                    agg_stats.get('total_posts', 0),
                    agg_stats.get('total_comments', 0),
                    agg_stats.get('total_likes', 0),
                    f"{agg_stats.get('avg_engagement_rate', 0):.2f}%",
                    'Sì' if analysis.get('ai_enabled') else 'No'
                ])

        self.logger.info(f"✓ CSV esportato: {output_path}")
        return str(output_path)

    def _generate_analysis_id(self):
        """Genera ID univoco per analisi"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def _update_index(self, analysis_data):
        """Aggiorna indice analisi"""
        index = self._load_index()

        # Aggiungi nuova analisi
        index.append({
            'id': analysis_data['id'],
            'timestamp': analysis_data['timestamp'],
            'brand_name': analysis_data['brand_name'],
            'social_urls': analysis_data['social_urls'],
            'ai_enabled': analysis_data['ai_enabled']
        })

        # Salva indice
        self._save_index(index)

    def _remove_from_index(self, analysis_id):
        """Rimuovi analisi da indice"""
        index = self._load_index()
        index = [a for a in index if a['id'] != analysis_id]
        self._save_index(index)

    def _load_index(self):
        """Carica indice analisi"""
        index_file = self.results_dir / 'index.json'

        if not index_file.exists():
            return []

        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self, index):
        """Salva indice analisi"""
        index_file = self.results_dir / 'index.json'

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
