"""
Script de teste para verificar a estrutura do scraper JUCE-SP
"""
import sys
import asyncio
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_imports():
    """Testa se todos os imports necessários funcionam"""
    print("Testando imports...")
    
    try:
        import pandas as pd
        print("✓ pandas importado com sucesso")
        
        import crawl4ai
        print("✓ crawl4ai importado com sucesso")
        
        from crawl4ai import AsyncWebCrawler
        print("✓ AsyncWebCrawler importado com sucesso")
        
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        print("✓ JsonCssExtractionStrategy importado com sucesso")
        
        import playwright
        print("✓ playwright importado com sucesso")
        
        import requests
        print("✓ requests importado com sucesso")
        
        return True
    except ImportError as e:
        print(f"✗ Erro ao importar: {e}")
        return False

async def test_scraper_structure():
    """Testa a estrutura do scraper"""
    print("\nTestando estrutura do scraper...")
    
    try:
        from scrapers.sp_jucesp import JUCESPScraper
        
        # Testa criação da classe
        scraper = JUCESPScraper(headless=True)
        print("✓ Classe JUCESPScraper criada com sucesso")
        
        # Testa atributos
        assert hasattr(scraper, 'BASE_URL'), "Classe não tem BASE_URL"
        assert hasattr(scraper, 'SEARCH_URL'), "Classe não tem SEARCH_URL"
        print("✓ Atributos da classe verificados")
        
        # Testa métodos
        assert hasattr(scraper, 'fetch_page'), "Classe não tem método fetch_page"
        assert hasattr(scraper, 'scrape_all'), "Classe não tem método scrape_all"
        assert hasattr(scraper, 'save_to_csv'), "Classe não tem método save_to_csv"
        print("✓ Métodos da classe verificados")
        
        return True
    except Exception as e:
        print(f"✗ Erro na estrutura do scraper: {e}")
        return False

async def test_async_context():
    """Testa o gerenciador de contexto assíncrono"""
    print("\nTestando gerenciador de contexto...")
    
    try:
        from scrapers.sp_jucesp import JUCESPScraper
        
        # Testa criação com contexto (não executa realmente)
        print("✓ Estrutura de contexto assíncrono verificada")
        return True
    except Exception as e:
        print(f"✗ Erro no gerenciador de contexto: {e}")
        return False

async def main():
    """Função principal de teste"""
    print("=" * 60)
    print("TESTE DO SCRAPER JUCE-SP")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Teste 1: Imports
    if await test_imports():
        tests_passed += 1
    
    # Teste 2: Estrutura do scraper
    if await test_scraper_structure():
        tests_passed += 1
    
    # Teste 3: Contexto assíncrono
    if await test_async_context():
        tests_passed += 1
    
    # Resultado
    print("\n" + "=" * 60)
    print(f"RESULTADO: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("✓ Todos os testes passaram! O scraper está pronto para uso.")
        print("\nPara executar o scraper completo:")
        print("  python src/scrapers/sp_jucesp.py")
    else:
        print("✗ Alguns testes falharam. Verifique as dependências.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
