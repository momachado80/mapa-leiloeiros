"""
Extrator Direto de Leiloeiros do PDF da JUCE-SP
Extrai todos os dados sem filtrar emails genéricos.
"""
import pdfplumber
import re
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd

class PDFDirectExtractor:
    """Extrai todos os leiloeiros do PDF, incluindo emails genéricos"""
    
    def __init__(self, pdf_path: str = "docs/Leiloeiros de SP.pdf"):
        self.pdf_path = Path(pdf_path)
        
    def extract_all_text(self) -> str:
        """Extrai todo o texto do PDF"""
        print(f"📄 Extraindo texto de: {self.pdf_path.name}")
        
        if not self.pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {self.pdf_path}")
            return ""
        
        all_text = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"📖 Total de páginas: {total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"   📖 Processando página {page_num}/{total_pages}...")
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
                    
                    # Processa apenas algumas páginas para teste
                    if page_num >= 3:  # Teste com 3 páginas
                        print(f"   ⚠ Limitando a {page_num} páginas para teste")
                        break
                
                return "\n".join(all_text)
                
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""
    
    def extract_leiloeiros_from_text(self, text: str) -> List[Dict]:
        """
        Extrai leiloeiros do texto usando heurísticas.
        Assume que cada leiloeiro está em uma linha com padrão:
        NOME [MATRÍCULA] [LOGRADOURO] [TELEFONE] [EMAIL]
        """
        print("\n🔍 Extraindo leiloeiros do texto...")
        
        lines = text.split('\n')
        leiloeiros = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Tenta extrair email
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line)
            if email_match:
                email = email_match.group(0).lower()
                
                # Extrai nome (tudo antes do email, removendo números no final)
                nome_part = line[:email_match.start()].strip()
                
                # Remove números de matrícula no final
                nome = re.sub(r'\s*\d+[/\-]?\d*\s*$', '', nome_part)
                nome = nome.strip()
                
                # Se o nome for muito curto ou parecer endereço, tenta outra abordagem
                if len(nome) < 3 or self.looks_like_address(nome):
                    # Tenta pegar a primeira parte da linha como nome
                    nome = line.split()[0] if line.split() else "N/A"
                
                # Verifica se é email corporativo
                is_corporate = self.is_corporate_email(email)
                
                # Extrai site se for email corporativo
                site = self.extract_site_from_email(email) if is_corporate else ""
                
                leiloeiro = {
                    'nome': nome,
                    'email': email,
                    'email_corporativo': is_corporate,
                    'site': site,
                    'fonte': 'pdf_direto',
                    'linha_original': line[:100]  # Para debug
                }
                
                leiloeiros.append(leiloeiro)
        
        print(f"✅ Leiloeiros encontrados: {len(leiloeiros)}")
        return leiloeiros
    
    def looks_like_address(self, text: str) -> bool:
        """Verifica se o texto parece um endereço"""
        address_keywords = [
            'RUA', 'AVENIDA', 'AV.', 'ALAMEDA', 'TRAVESSA',
            'KM', 'Nº', 'N°', 'S/N', 'APTO', 'SALA'
        ]
        
        text_upper = text.upper()
        for keyword in address_keywords:
            if keyword in text_upper:
                return True
        
        return False
    
    def is_corporate_email(self, email: str) -> bool:
        """Verifica se o email é corporativo"""
        generic_domains = {
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
            'globo.com', 'live.com', 'msn.com', 'aol.com'
        }
        
        domain = email.split('@')[-1].lower()
        return not any(domain.endswith(generic) for generic in generic_domains)
    
    def extract_site_from_email(self, email: str) -> str:
        """Extrai site do email corporativo"""
        if not self.is_corporate_email(email):
            return ""
        
        domain = email.split('@')[-1]
        domain_parts = domain.split('.')
        
        if len(domain_parts) >= 2:
            if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
                main_domain = '.'.join(domain_parts[-3:])
            else:
                main_domain = '.'.join(domain_parts[-2:])
            
            return f"https://www.{main_domain}"
        
        return ""
    
    def save_to_json(self, data: List[Dict], output_path: str = "data/processed/leiloeiros_todos.json"):
        """Salva dados em JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Dados salvos em: {output_path}")
        print(f"📊 Estatísticas:")
        print(f"   - Total de leiloeiros: {len(data)}")
        
        emails = sum(1 for d in data if d['email'])
        corporativos = sum(1 for d in data if d['email_corporativo'])
        sites = sum(1 for d in data if d['site'])
        
        print(f"   - Com email: {emails}")
        print(f"   - Emails corporativos: {corporativos}")
        print(f"   - Com site: {sites}")
        
        return output_file
    
    def run_extraction(self):
        """Executa extração completa"""
        print("=" * 70)
        print("🔧 EXTRATOR DIRETO DE LEILOEIROS - TODOS OS DADOS")
        print("=" * 70)
        
        # Extrai texto
        text = self.extract_all_text()
        if not text:
            print("❌ Nenhum texto extraído")
            return None
        
        print(f"✅ Texto extraído: {len(text)} caracteres")
        
        # Extrai leiloeiros
        leiloeiros = self.extract_leiloeiros_from_text(text)
        if not leiloeiros:
            print("❌ Nenhum leiloeiro encontrado")
            return None
        
        # Salva em JSON
        output_path = self.save_to_json(leiloeiros)
        
        # Análise
        print("\n📈 ANÁLISE DOS DADOS:")
        print("-" * 50)
        
        df = pd.DataFrame(leiloeiros)
        
        # Primeiros 10 leiloeiros
        print("\n🔍 Primeiros 10 leiloeiros:")
        for idx, row in df.head(10).iterrows():
            print(f"   {idx+1}. {row['nome'][:40]}...")
            print(f"      📧 {row['email']}")
            if row['site']:
                print(f"      🌐 {row['site']}")
        
        # Distribuição de emails
        print(f"\n📧 Distribuição de emails:")
        generic_count = len(df) - df['email_corporativo'].sum()
        print(f"   - Genéricos: {generic_count}")
        print(f"   - Corporativos: {df['email_corporativo'].sum()}")
        
        print("\n✅ Extração concluída!")
        return output_path

def main():
    """Função principal"""
    extractor = PDFDirectExtractor()
    output_path = extractor.run_extraction()
    
    if output_path:
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Execute o ranqueamento")
    else:
        print("\n❌ Falha na extração")

if __name__ == "__main__":
    main()
