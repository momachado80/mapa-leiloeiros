"""
Extrator de Tabelas de Leiloeiros com Correção de Colunas
Extrai corretamente nomes e emails do PDF da JUCE-SP, evitando mistura de colunas.
"""
import pdfplumber
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd

class PDFTableExtractorFixed:
    """Extrai tabelas de leiloeiros do PDF com correção de colunas"""
    
    def __init__(self, pdf_path: str = "docs/Leiloeiros de SP.pdf"):
        self.pdf_path = Path(pdf_path)
        self.all_data = []
        
    def extract_table_with_fixed_columns(self, page) -> List[List[str]]:
        """
        Extrai tabela usando coordenadas X fixas para delimitar colunas.
        A tabela tem aproximadamente estas colunas:
        Col 1: Nome (x: 50-200)
        Col 2: Matrícula (x: 200-300)
        Col 3: Logradouro (x: 300-450)
        Col 4: Telefone (x: 450-550)
        Col 5: Email (x: 550-700)
        """
        # Define bounding boxes para cada coluna
        bboxes = [
            (50, 0, 200, page.height),    # Coluna 1: Nome
            (200, 0, 300, page.height),   # Coluna 2: Matrícula
            (300, 0, 450, page.height),   # Coluna 3: Logradouro
            (450, 0, 550, page.height),   # Coluna 4: Telefone
            (550, 0, 700, page.height),   # Coluna 5: Email
        ]
        
        table_data = []
        
        # Extrai texto de cada coluna separadamente
        for bbox in bboxes:
            cropped = page.within_bbox(bbox)
            text = cropped.extract_text()
            if text:
                lines = text.split('\n')
                table_data.append(lines)
            else:
                table_data.append([])
        
        # Transpõe os dados para ter linhas em vez de colunas
        max_rows = max(len(col) for col in table_data)
        rows = []
        
        for i in range(max_rows):
            row = []
            for col in table_data:
                if i < len(col):
                    row.append(col[i].strip())
                else:
                    row.append("")
            rows.append(row)
        
        return rows
    
    def extract_all_tables(self) -> List[Dict]:
        """
        Extrai todas as tabelas do PDF.
        """
        print(f"📄 Extraindo tabelas de: {self.pdf_path.name}")
        
        if not self.pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {self.pdf_path}")
            return []
        
        all_leiloeiros = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"📖 Total de páginas: {total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"   🔍 Processando página {page_num}/{total_pages}...")
                    
                    # Extrai tabela com colunas fixas
                    table_rows = self.extract_table_with_fixed_columns(page)
                    
                    # Processa cada linha
                    for row in table_rows:
                        if len(row) >= 5:  # Temos pelo menos 5 colunas
                            nome = row[0]
                            email = row[4] if len(row) > 4 else ""
                            
                            # Limpa o nome (remove números de matrícula no final)
                            nome_limpo = self.clean_nome(nome)
                            
                            # Extrai email válido
                            email_limpo = self.extract_email_from_text(email)
                            
                            if nome_limpo and nome_limpo.strip():
                                leiloeiro = {
                                    'nome': nome_limpo,
                                    'email': email_limpo if email_limpo else "",
                                    'email_corporativo': self.is_corporate_email(email_limpo) if email_limpo else False,
                                    'site': self.extract_site_from_email(email_limpo) if email_limpo else "",
                                    'fonte': 'pdf_tabela_extraida',
                                    'pagina': page_num,
                                    'linha_original': ' | '.join(row[:3])  # Para debug
                                }
                                all_leiloeiros.append(leiloeiro)
                    
                    # Limite para teste (remover depois)
                    if page_num >= 5:  # Processa apenas 5 páginas para teste
                        print(f"   ⚠ Limitando a {page_num} páginas para teste")
                        break
                
                print(f"✅ Total de leiloeiros extraídos: {len(all_leiloeiros)}")
                
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return all_leiloeiros
    
    def clean_nome(self, nome: str) -> str:
        """
        Limpa o nome do leiloeiro.
        Remove números de matrícula e caracteres estranhos no final.
        """
        if not nome:
            return ""
        
        # Remove números no final (matrícula)
        nome_limpo = re.sub(r'\s*\d+[/\-]?\d*\s*$', '', nome)
        
        # Remove caracteres especiais no final
        nome_limpo = re.sub(r'[^\w\sÀ-ÿ]\s*$', '', nome_limpo)
        
        # Remove espaços extras
        nome_limpo = nome_limpo.strip()
        
        # Se o nome for muito curto ou parecer endereço, descarta
        if len(nome_limpo) < 3 or self.looks_like_address(nome_limpo):
            return ""
        
        return nome_limpo
    
    def looks_like_address(self, text: str) -> bool:
        """
        Verifica se o texto parece um endereço em vez de um nome.
        """
        address_keywords = [
            'RUA', 'AVENIDA', 'AV.', 'ALAMEDA', 'TRAVESSA', 'RODOVIA',
            'KM', 'Nº', 'N°', 'N.', 'S/N', 'APTO', 'APARTAMENTO',
            'SALA', 'ANDAR', 'BLOCO', 'CONJUNTO', 'LOTE', 'QUADRA'
        ]
        
        text_upper = text.upper()
        for keyword in address_keywords:
            if keyword in text_upper:
                return True
        
        # Verifica padrões de endereço
        if re.search(r'\d+\s*[-/]\s*\d+', text):  # Números com híbar
            return True
        
        return False
    
    def extract_email_from_text(self, text: str) -> Optional[str]:
        """
        Extrai email válido do texto.
        """
        if not text:
            return None
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        
        if emails:
            return emails[0].lower()
        
        return None
    
    def is_corporate_email(self, email: str) -> bool:
        """
        Verifica se o email é corporativo (não genérico).
        """
        if not email:
            return False
        
        generic_domains = {
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
            'globo.com', 'live.com', 'msn.com', 'aol.com'
        }
        
        domain = email.split('@')[-1].lower()
        
        for generic in generic_domains:
            if domain.endswith(generic):
                return False
        
        return True
    
    def extract_site_from_email(self, email: str) -> Optional[str]:
        """
        Extrai site a partir do email corporativo.
        Para emails genéricos, retorna string vazia.
        """
        if not email or not self.is_corporate_email(email):
            return ""
        
        domain = email.split('@')[-1]
        domain_parts = domain.split('.')
        
        if len(domain_parts) >= 2:
            # Pega os últimos 2 ou 3 partes
            if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
                main_domain = '.'.join(domain_parts[-3:])
            else:
                main_domain = '.'.join(domain_parts[-2:])
            
            return f"https://www.{main_domain}"
        
        return ""
    
    def save_to_json(self, data: List[Dict], output_path: str = "data/processed/leiloeiros_completos.json"):
        """
        Salva os dados em arquivo JSON.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Dados salvos em: {output_path}")
        print(f"📊 Estatísticas:")
        print(f"   - Total de leiloeiros: {len(data)}")
        
        # Conta emails
        emails = sum(1 for d in data if d['email'])
        print(f"   - Com email: {emails}")
        
        # Conta emails corporativos
        corporativos = sum(1 for d in data if d['email_corporativo'])
        print(f"   - Emails corporativos: {corporativos}")
        
        # Conta sites
        sites = sum(1 for d in data if d['site'])
        print(f"   - Com site: {sites}")
        
        return output_file
    
    def run_extraction(self):
        """
        Executa a extração completa.
        """
        print("=" * 70)
        print("🔧 EXTRATOR DE TABELAS COM CORREÇÃO DE COLUNAS")
        print("=" * 70)
        
        # Extrai dados
        data = self.extract_all_tables()
        
        if not data:
            print("❌ Nenhum dado extraído")
            return None
        
        # Salva em JSON
        output_path = self.save_to_json(data)
        
        # Cria DataFrame para análise
        df = pd.DataFrame(data)
        
        # Análise dos dados
        print("\n📈 ANÁLISE DOS DADOS EXTRAÍDOS:")
        print("-" * 50)
        
        # Top 10 nomes mais longos (para verificar se são nomes reais)
        df['nome_length'] = df['nome'].str.len()
        top_nomes = df.nlargest(10, 'nome_length')[['nome', 'email', 'site']]
        
        print("\n🔍 Top 10 nomes mais longos (verificação):")
        for idx, row in top_nomes.iterrows():
            print(f"   • {row['nome'][:50]}...")
            if row['email']:
                print(f"     📧 {row['email']}")
            if row['site']:
                print(f"     🌐 {row['site']}")
        
        # Distribuição por página
        print(f"\n📖 Distribuição por página:")
        page_counts = df['pagina'].value_counts().sort_index()
        for pagina, count in page_counts.items():
            print(f"   Página {pagina}: {count} leiloeiros")
        
        print("\n✅ Extração concluída com sucesso!")
        return output_path

def main():
    """Função principal"""
    extractor = PDFTableExtractorFixed()
    output_path = extractor.run_extraction()
    
    if output_path:
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Execute o ranqueamento com:")
        print(f"   python src/processors/rank_auctioneers_fixed.py")
    else:
        print("\n❌ Falha na extração")

if __name__ == "__main__":
    main()
