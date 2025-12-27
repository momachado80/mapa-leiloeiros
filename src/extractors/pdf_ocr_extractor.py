"""
Extrator de Leiloeiros usando OCR - Processa PDFs escaneados
Extrai todos os dados incluindo emails genéricos.
"""
import pdfplumber
import pytesseract
import re
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd
from PIL import Image
import io

class PDFOCRExtractor:
    """Extrai leiloeiros de PDFs escaneados usando OCR"""
    
    def __init__(self, pdf_path: str = "docs/Leiloeiros de SP.pdf"):
        self.pdf_path = Path(pdf_path)
        
    def extract_text_with_ocr(self, page_limit: int = 5) -> str:
        """Extrai texto do PDF usando OCR"""
        print(f"📄 Extraindo texto com OCR de: {self.pdf_path.name}")
        
        if not self.pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {self.pdf_path}")
            return ""
        
        all_text = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(page_limit, total_pages)
                
                print(f"📖 Processando {pages_to_process} de {total_pages} páginas...")
                
                for page_num in range(pages_to_process):
                    print(f"   🔍 Página {page_num + 1}/{pages_to_process}...")
                    page = pdf.pages[page_num]
                    
                    # Converte página para imagem
                    im = page.to_image(resolution=150)
                    
                    # Extrai texto com OCR
                    ocr_text = pytesseract.image_to_string(im.original)
                    
                    if ocr_text and len(ocr_text.strip()) > 50:
                        all_text.append(ocr_text)
                        print(f"   ✅ OCR extraiu: {len(ocr_text)} caracteres")
                    else:
                        print(f"   ⚠ OCR não extraiu texto significativo")
                
                return "\n".join(all_text)
                
        except Exception as e:
            print(f"❌ Erro no OCR: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""
    
    def extract_leiloeiros_from_ocr_text(self, text: str) -> List[Dict]:
        """
        Extrai leiloeiros do texto OCR.
        Procura por padrões de email e tenta extrair nomes.
        """
        print("\n🔍 Extraindo leiloeiros do texto OCR...")
        
        lines = text.split('\n')
        leiloeiros = []
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Procura emails na linha
            email_matches = re.findall(email_pattern, line)
            
            for email in email_matches:
                email = email.lower()
                
                # Tenta extrair nome (texto antes do email)
                email_pos = line.find(email)
                if email_pos > 0:
                    nome_part = line[:email_pos].strip()
                    
                    # Remove números e caracteres especiais no final
                    nome = re.sub(r'[\d\s\-\./]+$', '', nome_part)
                    nome = nome.strip()
                    
                    # Se o nome for muito curto, tenta a linha anterior
                    if len(nome) < 3 and line_num > 0:
                        prev_line = lines[line_num - 1].strip()
                        if prev_line and len(prev_line) > 3:
                            nome = prev_line
                    
                    # Limpa o nome
                    nome = self.clean_nome(nome)
                    
                    if nome and len(nome) >= 3:
                        # Verifica se é email corporativo
                        is_corporate = self.is_corporate_email(email)
                        
                        # Extrai site se for email corporativo
                        site = self.extract_site_from_email(email) if is_corporate else ""
                        
                        leiloeiro = {
                            'nome': nome,
                            'email': email,
                            'email_corporativo': is_corporate,
                            'site': site,
                            'fonte': 'pdf_ocr',
                            'linha_ocr': line[:80]  # Para debug
                        }
                        
                        leiloeiros.append(leiloeiro)
        
        print(f"✅ Leiloeiros encontrados: {len(leiloeiros)}")
        return leiloeiros
    
    def clean_nome(self, nome: str) -> str:
        """Limpa o nome do leiloeiro"""
        if not nome:
            return ""
        
        # Remove números no final
        nome = re.sub(r'\s*\d+[/\-]?\d*\s*$', '', nome)
        
        # Remove caracteres especiais no final
        nome = re.sub(r'[^\w\sÀ-ÿ]\s*$', '', nome)
        
        # Remove palavras comuns de endereço
        address_words = ['RUA', 'AVENIDA', 'AV.', 'ALAMEDA', 'TRAVESSA', 
                        'KM', 'Nº', 'N°', 'S/N', 'APTO', 'SALA', 'ANDAR']
        
        nome_words = nome.upper().split()
        filtered_words = [word for word in nome_words if word not in address_words]
        
        if filtered_words:
            # Reconstroi mantendo o caso original das primeiras letras
            original_words = nome.split()
            cleaned_words = []
            
            for i, word in enumerate(original_words):
                if i < len(filtered_words) and word.upper() == filtered_words[i]:
                    cleaned_words.append(word)
            
            nome = ' '.join(cleaned_words)
        
        return nome.strip()
    
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
    
    def save_to_json(self, data: List[Dict], output_path: str = "data/processed/leiloeiros_ocr.json"):
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
    
    def run_extraction(self, page_limit: int = 10):
        """Executa extração completa"""
        print("=" * 70)
        print("🔧 EXTRATOR OCR DE LEILOEIROS - TODOS OS DADOS")
        print("=" * 70)
        
        # Extrai texto com OCR
        text = self.extract_text_with_ocr(page_limit)
        if not text:
            print("❌ Nenhum texto extraído com OCR")
            return None
        
        print(f"✅ Texto OCR extraído: {len(text)} caracteres")
        
        # Extrai leiloeiros
        leiloeiros = self.extract_leiloeiros_from_ocr_text(text)
        if not leiloeiros:
            print("❌ Nenhum leiloeiro encontrado")
            return None
        
        # Salva em JSON
        output_path = self.save_to_json(leiloeiros)
        
        # Análise
        print("\n📈 ANÁLISE DOS DADOS OCR:")
        print("-" * 50)
        
        df = pd.DataFrame(leiloeiros)
        
        # Primeiros 10 leiloeiros
        print("\n🔍 Primeiros 10 leiloeiros encontrados:")
        for idx, row in df.head(10).iterrows():
            print(f"   {idx+1}. {row['nome'][:50]}...")
            print(f"      📧 {row['email']}")
            if row['site']:
                print(f"      🌐 {row['site']}")
        
        # Distribuição
        print(f"\n📊 Distribuição:")
        print(f"   - Total: {len(df)}")
        print(f"   - Emails genéricos: {len(df) - df['email_corporativo'].sum()}")
        print(f"   - Emails corporativos: {df['email_corporativo'].sum()}")
        print(f"   - Com site: {df['site'].str.len().gt(0).sum()}")
        
        print("\n✅ Extração OCR concluída!")
        return output_path

def main():
    """Função principal"""
    extractor = PDFOCRExtractor()
    
    # Processa mais páginas para obter mais dados
    output_path = extractor.run_extraction(page_limit=10)
    
    if output_path:
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Execute o ranqueamento")
    else:
        print("\n❌ Falha na extração OCR")

if __name__ == "__main__":
    main()
