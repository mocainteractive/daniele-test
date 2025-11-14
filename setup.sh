#!/bin/bash
# MOCA Social Brand Analyzer - Quick Setup Script

set -e  # Exit on error

# Colors
RED='\033[91m'
GRAY='\033[38;2;138;138;138m'
RESET='\033[0m'

echo ""
echo -e "${RED}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║                                                                   ║${RESET}"
echo -e "${RED}║          🎯 MOCA SOCIAL BRAND ANALYZER - SETUP                   ║${RESET}"
echo -e "${RED}║                                                                   ║${RESET}"
echo -e "${RED}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Check Python version
echo -e "${GRAY}Verificando Python...${RESET}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 non trovato. Installa Python 3.8+${RESET}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${RED}✓ Python ${PYTHON_VERSION} trovato${RESET}"

# Create virtual environment
echo ""
echo -e "${GRAY}Creando virtual environment...${RESET}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${RED}✓ Virtual environment creato${RESET}"
else
    echo -e "${GRAY}Virtual environment già esistente${RESET}"
fi

# Activate virtual environment
echo ""
echo -e "${GRAY}Attivando virtual environment...${RESET}"
source venv/bin/activate

# Upgrade pip
echo ""
echo -e "${GRAY}Aggiornando pip...${RESET}"
pip install --upgrade pip -q

# Install dependencies
echo ""
echo -e "${GRAY}Installando dipendenze...${RESET}"
pip install -r requirements.txt -q

echo -e "${RED}✓ Dipendenze installate${RESET}"

# Create storage directories
echo ""
echo -e "${GRAY}Creando directory storage...${RESET}"
mkdir -p storage/results storage/exports storage/logs

echo -e "${RED}✓ Directory create${RESET}"

# Make main.py executable
chmod +x main.py

# Success
echo ""
echo -e "${RED}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${RED}║                  ✅ SETUP COMPLETATO!                             ║${RESET}"
echo -e "${RED}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

echo -e "${GRAY}Per avviare la dashboard:${RESET}"
echo -e "  ${RED}source venv/bin/activate${RESET}"
echo -e "  ${RED}python main.py${RESET}"
echo ""

echo -e "${GRAY}Per avviare la CLI:${RESET}"
echo -e "  ${RED}source venv/bin/activate${RESET}"
echo -e "  ${RED}python main.py --mode cli${RESET}"
echo ""

echo -e "${GRAY}Per maggiori informazioni consulta README_NEW.md${RESET}"
echo ""
