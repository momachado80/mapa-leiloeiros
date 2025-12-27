"""
Scraper para a Junta Comercial do Estado de São Paulo (JUCE-SP)
Extrai lista de leiloeiros com nome, matrícula e site.

Nota: Como a URL pública exata da lista de leiloeiros não foi identificada,
este script demonstra a estrutura completa e funcional do scraper.
Quando a URL correta for encontrada, basta atualizar a constante LEILOEIROS_URL.
"""
import asyncio
import json
import logging
from typing import List, Dict
from pathlib import Path

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JUCESPScraper:
    """Scraper para o site da JUCE-SP"""
    
    # URL de exemplo - atualizar quando a URL real for encontrada
    LEILOEIROS_URL = "https://www.jucesponline.sp.gov.br"
    
    def __init__(self, headless: bool = True, max_pages: int = 5):
        """
        Inicializa o scraper.
        
        Args:
            headless: Se True, executa o navegador em modo headless
            max_pages: Número máximo de páginas para percorrer na paginação
        """
        self.headless = headless
        self.max_pages = max_pages
        self.crawler = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.crawler = AsyncWebCrawler(headless=self.headless)
        await self.crawler.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.crawler:
            await self.crawler.close()
    
    async def scrape_single_page(self, page_num: int = 1) -> List[Dict]:
        """
        Extrai leiloeiros de uma única página.
        
        Args:
            page_num: Número da página
            
        Returns:
            Lista de dicionários com dados dos leiloeiros
        """
        print(f"📄 Processando página {page_num}...")
        
        try:
            # Para demonstração, usamos dados de exemplo
            # Em produção, substituir pela extração real da página
            
            # Exemplo de como seria a extração real:
            # strategy = JsonCssExtractionStrategy(
            #     css_selector="table tbody tr",
            #     schema={
            #         "nome": "td:nth-child(1)",
            #         "matricula": "td:nth-child(2)",
            #         "site": "td:nth-child(3) a@href"
            #     },
            #     multiple=True
            # )
            # 
            # result = await self.crawler.arun(
            #     url=f"{self.LEILOEIROS_URL}?page={page_num}",
            #     extraction_strategy=strategy,
            #     wait_for="table",
            #     timeout=30000
            # )
            
            # Simula delay de requisição
            await asyncio.sleep(0.5)
            
            # Dados de exemplo para demonstração
            if page_num == 1:
                return [
                    {"nome": "JOÃO DA SILVA LEILÕES LTDA", "matricula": "12345/SP", "site": "https://www.joaodasilvaleiloes.com.br"},
                    {"nome": "MARIA OLIVEIRA AUCTION ME", "matricula": "67890/SP", "site": "https://www.mariaoliveiraleiloes.com.br"},
                    {"nome": "CARLOS SOUZA LEILOEIRO OFICIAL", "matricula": "54321/SP", "site": "https://www.carlossouzaleiloeiro.com.br"},
                ]
            elif page_num == 2:
                return [
                    {"nome": "ANA COSTA LEILÕES E AVALIAÇÕES", "matricula": "98765/SP", "site": "https://www.anacostaleiloes.com.br"},
                    {"nome": "PEDRO ALVES LEILOEIRO REGISTRADO", "matricula": "13579/SP", "site": "https://www.pedroalvesleiloeiro.com.br"},
                    {"nome": "FERNANDA LIMA LEILÕES SPE", "matricula": "24680/SP", "site": "https://www.fernandalemaleiloes.com.br"},
                ]
            else:
                return []
                
        except Exception as e:
            print(f"✗ Erro na página {page_num}: {str(e)}")
            return []
    
    async def scrape_all_pages(self) -> List[Dict]:
        """
        Percorre todas as páginas de leiloeiros.
        
        Returns:
            Lista completa de leiloeiros de todas as páginas
        """
        print("🔍 Iniciando extração com paginação...")
        
        all_leiloeiros = []
        
        for page_num in range(1, self.max_pages + 1):
            page_leiloeiros = await self.scrape_single_page(page_num)
            
            if not page_leiloeiros:
                print(f"⏹️ Nenhum leiloeiro na página {page_num}. Parando paginação.")
                break
            
            all_leiloeiros.extend(page_leiloeiros)
            print(f"✅ Página {page_num}: {len(page_leiloeiros)} leiloeiros")
            
            # Simula delay entre páginas (evitar rate limiting)
            if page_num < self.max_pages and page_leiloeiros:
                await asyncio.sleep(1)
        
        return all_leiloeiros
    
    async def test_real_connection(self) -> bool:
        """
        Testa a conexão com o site real.
        
        Returns:
            True se a conexão for bem-sucedida
        """
        print("🌐 Testando conexão com o site da JUCE-SP...")
        
        try:
            result = await self.crawler.arun(
                url=self.LEILOEIROS_URL,
                timeout=10000
            )
            
            if result.success:
                print(f"✅ Conexão bem-sucedida! HTML recebido: {len(result.html)} caracteres")
                
                # Verifica se parece ser uma página de leiloeiros
                html_lower = result.html.lower()
                if any(term in html_lower for term in ['leiloeiro', 'jucesp', 'junta']):
                    print("✅ Site identificado como JUCE-SP")
                return True
            else:
                print(f"✗ Falha na conexão: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"✗ Erro de conexão: {str(e)}")
            return False
    
    def print_leiloeiros(self, leiloeiros: List[Dict]):
        """
        Imprime os leiloeiros no terminal para validação.
        
        Args:
            leiloeiros: Lista de dicionários com dados dos leiloeiros
        """
        if not leiloeiros:
            print("📭 Nenhum leiloeiro para exibir.")
            return
        
        print("\n" + "="*80)
        print("📋 LEILOEIROS EXTRAÍDOS")
        print("="*80)
        
        for i, leiloeiro in enumerate(leiloeiros, 1):
            print(f"\n{i}. {leiloeiro.get('nome', 'N/A')}")
            print(f"   📝 Matrícula: {leiloeiro.get('matricula', 'N/A')}")
            print(f"   🌐 Site: {leiloeiro.get('site', 'N/A')}")
        
        print(f"\n📊 Total: {len(leiloeiros)} leiloeiros")
    
    def save_to_json(self, leiloeiros: List[Dict], filename: str = "data/raw/leiloeiros_sp.json"):
        """
        Salva os leiloeiros em arquivo JSON.
        
        Args:
            leiloeiros: Lista de dicionários com dados dos leiloeiros
            filename: Nome do arquivo JSON
        """
        if not leiloeiros:
            print("📭 Nenhum dado para salvar.")
            return
        
        # Garante que o diretório existe
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Converte para JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(leiloeiros, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Dados salvos em: {filepath}")
        
        # Mostra estatísticas
        print(f"📈 Estatísticas:")
        print(f"   - Total de leiloeiros: {len(leiloeiros)}")
        print(f"   - Tamanho do arquivo: {filepath.stat().st_size} bytes")

async def main():
    """Função principal para execução do scraper"""
    print("=" * 60)
    print("🔍 SCRAPER JUCE-SP - Sistema de Extração de Leiloeiros")
    print("=" * 60)
    
    try:
        async with JUCESPScraper(headless=True, max_pages=3) as scraper:
            print("🚀 Inicializando scraper...")
            
            # Testa conexão com o site real
            connection_ok = await scraper.test_real_connection()
            
            if connection_ok:
                print("\n✅ Ambiente configurado corretamente!")
                print("📝 Para extração real, atualize a URL em LEILOEIROS_URL")
                print("   e implemente a lógica de extração em scrape_single_page()")
            
            print("\n" + "-" * 60)
            print("🔄 Iniciando extração de dados (modo demonstração)...")
            
            # Extrai os leiloeiros (modo demonstração)
            leiloeiros = await scraper.scrape_all_pages()
            
            # Imprime os resultados no terminal
            scraper.print_leiloeiros(leiloeiros)
            
            # Salva em JSON
            if leiloeiros:
                scraper.save_to_json(leiloeiros)
                print("\n✅ Scraping concluído com sucesso!")
                
                # Instruções para uso real
                print("\n" + "=" * 60)
                print("🚀 PRÓXIMOS PASSOS PARA USO REAL:")
                print("=" * 60)
                print("1. Identifique a URL exata da lista de leiloeiros da JUCE-SP")
                print("2. Atualize a constante LEILOEIROS_URL no código")
                print("3. Implemente a extração real em scrape_single_page()")
                print("4. Ajuste os seletores CSS conforme a estrutura da página")
                print("5. Teste com uma única página antes de executar a paginação completa")
            else:
                print("\n⚠ Scraping concluído, mas nenhum leiloeiro foi encontrado.")
                
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executa o scraper
    asyncio.run(main())
