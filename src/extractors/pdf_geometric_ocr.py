"""
Extrator Geométrico com OCR - Processa PDFs escaneados com coordenadas fixas
"""
import pdfplumber
import pytesseract
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
from PIL import Image

class PDFGeometricOCRExtractor:
    """Extrai leiloeiros de PDFs escaneados usando OCR com coordenadas fixas"""
    
    def __init__(self, pdf_path: str = "docs/Leiloeiros de SP.pdf"):
        self.pdf_path = Path(pdf_path)
        
    def extract_with_ocr_crop(self, page, left_percent: float = 0.3, right_percent: float = 0.7) -> Tuple[List[str], List[str]]:
        """
        Extrai texto com OCR usando corte vertical:
        - Esquerda (0-30%): Nomes
        - Direita (70-100%): Emails
        """
        # Converte página para imagem
        im = page.to_image(resolution=150)
        pil_image = im.original
        
        # Obtém dimensões
        width, height = pil_image.size
        
        # Define áreas de corte
        left_box = (0, 0, int(width * left_percent), height)
        right_box = (int(width * right_percent), 0, width, height)
        
        # Corta imagens
        left_image = pil_image.crop(left_box)
        right_image = pil_image.crop(right_box)
        
        # Aplica OCR nas áreas cortadas
        left_text = pytesseract.image_to_string(left_image, lang='por')
        right_text = pytesseract.image_to_string(right_image, lang='por')
        
        # Processa nomes (área esquerda)
        names = []
        for line in left_text.split('\n'):
            line = line.strip()
            if line and len(line) > 2:
                # Remove números no final (matrícula)
                clean_line = re.sub(r'\s*\d+[/\-]?\d*\s*$', '', line)
                clean_line = clean_line.strip()
                if clean_line and len(clean_line) > 2:
                    names.append(clean_line)
        
        # Processa emails (área direita)
        emails = []
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_matches = re.findall(email_pattern, right_text)
        emails.extend([email.lower() for email in email_matches])
        
        return names, emails
    
    def is_address(self, text: str) -> bool:
        """Verifica se o texto parece um endereço"""
        address_keywords = [
            'RUA', 'AVENIDA', 'AV.', 'ALAMEDA', 'TRAVESSA',
            'KM', 'Nº', 'N°', 'S/N', 'APTO', 'SALA', 'ANDAR'
        ]
        
        text_upper = text.upper()
        for keyword in address_keywords:
            if keyword in text_upper:
                return True
        
        # Verifica padrões de endereço
        if re.search(r'\d+\s*[-/]\s*\d+', text):
            return True
        
        return False
    
    def clean_name(self, name: str) -> str:
        """Limpa o nome do leiloeiro"""
        if not name:
            return ""
        
        # Remove caracteres especiais no início
        name = re.sub(r'^[_\W]+', '', name)
        
        # Remove números no final
        name = re.sub(r'[\d\s\-\./]+$', '', name)
        
        # Remove espaços extras
        name = name.strip()
        
        return name
    
    def extract_all_pages(self, page_limit: int = 5) -> List[Dict]:
        """Extrai dados de todas as páginas com OCR"""
        print(f"📄 Extraindo dados com OCR geométrico de: {self.pdf_path.name}")
        
        if not self.pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {self.pdf_path}")
            return []
        
        all_data = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(page_limit, total_pages)
                
                print(f"📖 Processando {pages_to_process} de {total_pages} páginas com OCR...")
                
                for page_num in range(pages_to_process):
                    print(f"   🔍 Página {page_num + 1}/{pages_to_process}...")
                    page = pdf.pages[page_num]
                    
                    # Extrai com OCR e corte
                    names, emails = self.extract_with_ocr_crop(page, left_percent=0.3, right_percent=0.7)
                    
                    # Processa cada nome
                    name_count = 0
                    for name in names:
                        # Limpa o nome
                        clean_name = self.clean_name(name)
                        
                        # Verifica se não é endereço
                        if (clean_name and len(clean_name) >= 3 and 
                            not self.is_address(clean_name) and
                            not clean_name.isspace()):
                            
                            # Tenta encontrar email correspondente
                            corresponding_email = ""
                            if emails:
                                # Usa round-robin para distribuir emails
                                email_idx = name_count % len(emails) if emails else 0
                                corresponding_email = emails[email_idx] if emails else ""
                            
                            record = {
                                'nome': clean_name,
                                'email': corresponding_email,
                                'pagina': page_num + 1,
                                'fonte': 'pdf_geometric_ocr'
                            }
                            
                            all_data.append(record)
                            name_count += 1
                    
                    print(f"   ✅ {len(names)} nomes brutos, {name_count} nomes válidos, {len(emails)} emails")
                
                print(f"\n✅ Total extraído: {len(all_data)} registros válidos")
                
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return all_data
    
    def save_raw_data(self, data: List[Dict], output_path: str = "data/processed/leiloeiros_geometric_ocr.json"):
        """Salva dados brutos em JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Dados salvos em: {output_path}")
        print(f"📊 Estatísticas:")
        print(f"   - Total de registros: {len(data)}")
        
        with_email = sum(1 for d in data if d['email'])
        print(f"   - Com email: {with_email}")
        print(f"   - Sem email: {len(data) - with_email}")
        
        # Primeiros 10 nomes para verificação
        print(f"\n🔍 Primeiros 10 registros:")
        for i, record in enumerate(data[:10], 1):
            print(f"   {i}. {record['nome'][:40]}...")
            if record['email']:
                print(f"      📧 {record['email']}")
        
        return output_file
    
    def run_extraction(self, page_limit: int = 10):
        """Executa extração completa"""
        print("=" * 70)
        print("🔧 EXTRATOR GEOMÉTRICO COM OCR - COORDENADAS FIXAS")
        print("=" * 70)
        
        # Extrai dados
        raw_data = self.extract_all_pages(page_limit=page_limit)
        
        if not raw_data:
            print("❌ Nenhum dado extraído")
            return None
        
        # Salva dados brutos
        output_path = self.save_raw_data(raw_data)
        
        # Análise
        print("\n📈 ANÁLISE DOS DADOS:")
        print("-" * 50)
        
        df = pd.DataFrame(raw_data)
        
        # Distribuição por página
        print(f"\n📖 Distribuição por página:")
        page_counts = df['pagina'].value_counts().sort_index()
        for pagina, count in page_counts.items():
            print(f"   Página {pagina}: {count} leiloeiros")
        
        # Nomes mais longos
        print(f"\n🔍 Nomes mais longos (verificação):")
        df['nome_length'] = df['nome'].str.len()
        top_names = df.nlargest(5, 'nome_length')[['nome', 'pagina']]
        for idx, row in top_names.iterrows():
            print(f"   • {row['nome'][:50]}... (Página {row['pagina']})")
        
        print(f"\n🎯 Extração concluída com {len(df)} registros")
        print("✅ Use esses dados brutos para a classificação inclusiva")
        
        return output_path

def main():
    """Função principal"""
    extractor = PDFGeometricOCRExtractor()
    
    # Processa mais páginas para obter mais dados
    output_path = extractor.run_extraction(page_limit=10)
    
    if output_path:
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Execute a classificação inclusiva")
        print(f"   python src/processors/rank_final.py")
    else:
        print("\n❌ Falha na extração")

if __name__ == "__main__":
    main()
