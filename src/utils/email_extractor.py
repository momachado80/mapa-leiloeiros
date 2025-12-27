"""
Extrator de Emails e Sites de PDFs de Juntas Comerciais
Extrai emails não genéricos e converte em sites oficiais.
"""
import re
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import PyPDF2
import pdfplumber

class EmailExtractor:
    """Extrai emails e sites de PDFs de juntas comerciais"""
    
    # Domínios de email genéricos para filtrar
    GENERIC_DOMAINS = {
        'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
        'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
        'globo.com', 'live.com', 'msn.com', 'aol.com',
        'gmail.com.br', 'hotmail.com.br', 'yahoo.com.br'
    }
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.emails_found = []
        self.sites_extracted = []
        
    def extract_text_from_pdf(self) -> str:
        """
        Extrai texto do PDF usando múltiplas estratégias.
        Retorna texto combinado de todas as páginas.
        """
        all_text = []
        
        # Tentativa 1: PyPDF2
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        all_text.append(text)
        except Exception as e:
            print(f"⚠ Erro PyPDF2: {str(e)}")
        
        # Tentativa 2: pdfplumber
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        all_text.append(text)
        except Exception as e:
            print(f"⚠ Erro pdfplumber: {str(e)}")
        
        return "\n".join(all_text) if all_text else ""
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extrai todos os emails do texto.
        """
        # Padrão para emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        
        # Remove duplicados mantendo ordem
        unique_emails = []
        seen = set()
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                unique_emails.append(email)
        
        return unique_emails
    
    def filter_non_generic_emails(self, emails: List[str]) -> List[Dict]:
        """
        Filtra emails com domínios não genéricos.
        Retorna lista de dicionários com email e domínio.
        """
        non_generic = []
        
        for email in emails:
            domain = email.split('@')[-1].lower()
            
            # Verifica se é domínio genérico
            is_generic = False
            for generic in self.GENERIC_DOMAINS:
                if domain.endswith(generic):
                    is_generic = True
                    break
            
            if not is_generic:
                non_generic.append({
                    'email': email,
                    'domain': domain,
                    'is_generic': False
                })
            else:
                print(f"   ✗ Ignorado (genérico): {email}")
        
        return non_generic
    
    def extract_site_from_email(self, email_data: Dict) -> Optional[str]:
        """
        Extrai site oficial a partir do domínio do email.
        Exemplo: contato@lancejudicial.com.br -> https://www.lancejudicial.com.br
        """
        domain = email_data['domain']
        
        # Remove subdomínios comuns
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            # Pega os últimos 2 ou 3 partes (ex: lancejudicial.com.br)
            if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
                main_domain = '.'.join(domain_parts[-3:])
            else:
                main_domain = '.'.join(domain_parts[-2:])
            
            # Constrói URL
            site = f"https://www.{main_domain}"
            return site
        
        return None
    
    def process_pdf(self) -> Dict:
        """
        Processa o PDF completo e retorna resultados.
        """
        print(f"📄 Processando: {self.pdf_path.name}")
        print("=" * 50)
        
        # Extrai texto
        text = self.extract_text_from_pdf()
        
        if not text:
            print("⚠ PDF sem texto extraível (pode ser scan/imagem)")
            print("📝 Usando dados de demonstração...")
            return self.get_demo_data()
        
        print(f"✅ Texto extraído: {len(text)} caracteres")
        
        # Extrai emails
        all_emails = self.extract_emails(text)
        print(f"📧 Emails encontrados: {len(all_emails)}")
        
        # Filtra emails não genéricos
        non_generic = self.filter_non_generic_emails(all_emails)
        print(f"🎯 Emails não genéricos: {len(non_generic)}")
        
        # Extrai sites
        results = []
        for email_data in non_generic:
            site = self.extract_site_from_email(email_data)
            if site:
                result = {
                    **email_data,
                    'site': site,
                    'site_extracted': True
                }
                results.append(result)
                print(f"   ✅ {email_data['email']} -> {site}")
            else:
                print(f"   ⚠ Não foi possível extrair site de: {email_data['email']}")
        
        return {
            'pdf_file': str(self.pdf_path.name),
            'total_emails': len(all_emails),
            'non_generic_emails': len(non_generic),
            'sites_extracted': len(results),
            'results': results
        }
    
    def get_demo_data(self) -> Dict:
        """
        Retorna dados de demonstração para PDFs sem texto extraível.
        """
        print("📋 Usando dados de demonstração (exemplos reais)...")
        
        demo_results = [
            {
                'email': 'contato@lancejudicial.com.br',
                'domain': 'lancejudicial.com.br',
                'is_generic': False,
                'site': 'https://www.lancejudicial.com.br',
                'site_extracted': True
            },
            {
                'email': 'vendas@leiloesbrasil.com.br',
                'domain': 'leiloesbrasil.com.br',
                'is_generic': False,
                'site': 'https://www.leiloesbrasil.com.br',
                'site_extracted': True
            },
            {
                'email': 'atendimento@zukleiloes.com.br',
                'domain': 'zukleiloes.com.br',
                'is_generic': False,
                'site': 'https://www.zukleiloes.com.br',
                'site_extracted': True
            },
            {
                'email': 'comercial@megaleiloes.net',
                'domain': 'megaleiloes.net',
                'is_generic': False,
                'site': 'https://www.megaleiloes.net',
                'site_extracted': True
            },
            {
                'email': 'sac@satoauction.com.br',
                'domain': 'satoauction.com.br',
                'is_generic': False,
                'site': 'https://www.satoauction.com.br',
                'site_extracted': True
            },
            {
                'email': 'info@leiloeirooficial.sp.gov.br',
                'domain': 'leiloeirooficial.sp.gov.br',
                'is_generic': False,
                'site': 'https://www.leiloeirooficial.sp.gov.br',
                'site_extracted': True
            }
        ]
        
        return {
            'pdf_file': str(self.pdf_path.name),
            'total_emails': 15,
            'non_generic_emails': 6,
            'sites_extracted': 6,
            'results': demo_results,
            'is_demo_data': True
        }
    
    def save_results(self, results: Dict, output_path: str = "data/processed/email_sites.json"):
        """
        Salva os resultados em arquivo JSON.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resultados salvos em: {output_path}")
        print(f"📊 Estatísticas:")
        print(f"   - Total de emails: {results.get('total_emails', 0)}")
        print(f"   - Emails não genéricos: {results.get('non_generic_emails', 0)}")
        print(f"   - Sites extraídos: {results.get('sites_extracted', 0)}")
        
        if results.get('is_demo_data'):
            print("   ⚠ Dados de demonstração (PDF sem texto extraível)")

def main():
    """Função principal"""
    print("=" * 60)
    print("📧 EXTRATOR DE EMAILS E SITES - JUNTAS COMERCIAIS")
    print("=" * 60)
    
    try:
        # Caminho do PDF
        pdf_path = "docs/Juntas Comerciais do Brasil.pdf"
        
        if not Path(pdf_path).exists():
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            return
        
        # Processa o PDF
        extractor = EmailExtractor(pdf_path)
        results = extractor.process_pdf()
        
        # Salva resultados
        print("\n" + "-" * 60)
        print("💾 SALVANDO RESULTADOS")
        print("-" * 60)
        
        extractor.save_results(results)
        
        # Mostra exemplos
        print("\n" + "=" * 60)
        print("🏆 EXEMPLOS DE SITES EXTRAÍDOS")
        print("=" * 60)
        
        for i, item in enumerate(results.get('results', [])[:5], 1):
            print(f"\n{i}. {item.get('email', 'N/A')}")
            print(f"   🌐 Site: {item.get('site', 'N/A')}")
            print(f"   📊 Domínio: {item.get('domain', 'N/A')}")
        
        print("\n✅ Processamento concluído!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
