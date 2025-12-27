"""
Configurações do projeto Mapa-Leiloeiros
"""

import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SRC_DIR = BASE_DIR / "src"
SCRAPERS_DIR = SRC_DIR / "scrapers"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Configurações de scraping
SCRAPING_CONFIG = {
    "juce_sp": {
        "base_url": "https://www.jucesponline.sp.gov.br",
        "search_url": "https://www.jucesponline.sp.gov.br/restrito/Leiloeiro/Leiloeiro/Listar",
        "max_pages": 10,
        "page_size": 10,
        "request_delay": 2,  # segundos entre requisições
        "timeout": 30000,  # milissegundos
    },
    # Outras juntas comerciais podem ser adicionadas aqui
}

# Configurações do banco de dados
DATABASE_CONFIG = {
    "sqlite": {
        "path": DATA_DIR / "leiloeiros.db",
        "table_leiloeiros": "leiloeiros",
        "table_metricas": "metricas_relevancia",
    }
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "scraping.log",
}

# Cria diretórios se não existirem
def setup_directories():
    """Cria todos os diretórios necessários para o projeto"""
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        SRC_DIR,
        SCRAPERS_DIR,
        NOTEBOOKS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Diretório criado/verificado: {directory}")

if __name__ == "__main__":
    setup_directories()
    print("Configuração do projeto concluída!")
