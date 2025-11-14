"""
Sistema di progress tracking dinamico per mostrare avanzamento operazioni
"""
import time
from datetime import datetime, timedelta
from utils.colors import TerminalColors


class ProgressTracker:
    """Tracker per progress bar dinamica"""

    def __init__(self, total_steps, description="Processing"):
        """
        Inizializza tracker

        Args:
            total_steps: Numero totale di step
            description: Descrizione generale
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = datetime.now()
        self.step_descriptions = []

    def update(self, step_description=None, increment=1):
        """
        Aggiorna progress

        Args:
            step_description: Descrizione dello step corrente
            increment: Incremento step (default 1)
        """
        self.current_step += increment

        if step_description:
            self.step_descriptions.append(step_description)

        self._print_progress(step_description or "Processing...")

    def _print_progress(self, current_description):
        """Stampa barra di progresso"""
        # Calcola percentuale
        percentage = min(100, int((self.current_step / self.total_steps) * 100))

        # Stima tempo rimanente
        elapsed = datetime.now() - self.start_time
        if self.current_step > 0:
            avg_time_per_step = elapsed.total_seconds() / self.current_step
            remaining_steps = self.total_steps - self.current_step
            eta_seconds = avg_time_per_step * remaining_steps
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "Calculating..."

        # Barra di progresso
        bar_length = 40
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        # Stampa
        print(f"\r{TerminalColors.RED}[{bar}] {percentage}%{TerminalColors.RESET} "
              f"{TerminalColors.GRAY}| Step {self.current_step}/{self.total_steps}{TerminalColors.RESET} "
              f"{TerminalColors.GRAY}| ETA: {eta}{TerminalColors.RESET} "
              f"\n{TerminalColors.GRAY}▶ {current_description}{TerminalColors.RESET}",
              end='\r', flush=True)

    def complete(self, final_message="Completed!"):
        """Completa il progress"""
        self.current_step = self.total_steps
        elapsed = datetime.now() - self.start_time

        print(f"\n{TerminalColors.RED}✓ {final_message}{TerminalColors.RESET} "
              f"{TerminalColors.GRAY}(Tempo totale: {str(elapsed).split('.')[0]}){TerminalColors.RESET}\n")

    def set_step(self, step, description):
        """Imposta step specifico"""
        self.current_step = step
        self.update(description, increment=0)


class MultiPhaseProgress:
    """Progress tracker multi-fase per operazioni complesse"""

    def __init__(self, phases):
        """
        Inizializza tracker multi-fase

        Args:
            phases: Lista di dict con 'name' e 'steps'
                    es. [{'name': 'Scraping', 'steps': 3}, {'name': 'Analysis', 'steps': 2}]
        """
        self.phases = phases
        self.current_phase_idx = 0
        self.total_steps = sum(p['steps'] for p in phases)
        self.completed_steps = 0
        self.start_time = datetime.now()

    def start_phase(self, phase_name):
        """Inizia una fase"""
        # Trova fase
        for idx, phase in enumerate(self.phases):
            if phase['name'] == phase_name:
                self.current_phase_idx = idx
                break

        print(f"\n{TerminalColors.RED}{'='*70}{TerminalColors.RESET}")
        print(f"{TerminalColors.RED}FASE {self.current_phase_idx + 1}/{len(self.phases)}: "
              f"{phase_name.upper()}{TerminalColors.RESET}")
        print(f"{TerminalColors.RED}{'='*70}{TerminalColors.RESET}\n")

    def update(self, description):
        """Aggiorna progress nella fase corrente"""
        self.completed_steps += 1

        # Calcola percentuale globale
        percentage = int((self.completed_steps / self.total_steps) * 100)

        # Barra
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)

        # ETA
        elapsed = datetime.now() - self.start_time
        if self.completed_steps > 0:
            eta_seconds = (elapsed.total_seconds() / self.completed_steps) * (self.total_steps - self.completed_steps)
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "..."

        # Stampa
        print(f"{TerminalColors.RED}[{bar}] {percentage}%{TerminalColors.RESET} "
              f"{TerminalColors.GRAY}| {self.completed_steps}/{self.total_steps} steps | ETA: {eta}{TerminalColors.RESET}")
        print(f"{TerminalColors.GRAY}▶ {description}{TerminalColors.RESET}\n")

    def complete(self):
        """Completa tutte le fasi"""
        elapsed = datetime.now() - self.start_time

        print(f"\n{TerminalColors.RED}{'='*70}{TerminalColors.RESET}")
        print(f"{TerminalColors.RED}✓ PROCESSO COMPLETATO!{TerminalColors.RESET}")
        print(f"{TerminalColors.GRAY}Tempo totale: {str(elapsed).split('.')[0]}{TerminalColors.RESET}")
        print(f"{TerminalColors.RED}{'='*70}{TerminalColors.RESET}\n")


def show_spinner(message, duration=1):
    """Mostra spinner animato"""
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    idx = 0

    while time.time() < end_time:
        print(f"\r{TerminalColors.RED}{spinner[idx % len(spinner)]}{TerminalColors.RESET} "
              f"{TerminalColors.GRAY}{message}{TerminalColors.RESET}", end='', flush=True)
        time.sleep(0.1)
        idx += 1

    print(f"\r{TerminalColors.RED}✓{TerminalColors.RESET} {TerminalColors.GRAY}{message}{TerminalColors.RESET}")
