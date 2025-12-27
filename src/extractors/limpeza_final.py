"""
Limpeza Final de Leiloeiros - Extração Direta de Tabela com PDFPlumber
Extrai dados limpos do PDF com recorte preciso e filtros rigorosos.
"""
import pdfplumber
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

class PDFTableExtractor:
    """Extrai tabela de leiloeiros com recorte preciso e limpeza rigorosa"""
    
    def __init__(self, pdf_path: str = "docs/Leiloeiros de SP.pdf"):
        self.pdf_path = Path(pdf_path)
        self.noise_patterns = [
            'Adriano Duarte',
            'duarte.adriano',
            'Licensed to',
            '28255301828',
            'Nome',
            'Matrícula',
            'MATRÍCULA',
            'NOME',
            'CPF',
            'CNPJ'
        ]
        
    def is_noise(self, text: str) -> bool:
        """Verifica se o texto é ruído/marca d'água"""
        if not text or pd.isna(text):
            return True
        
        text_lower = str(text).lower()
        
        # Verifica padrões de ruído
        for pattern in self.noise_patterns:
            if pattern.lower() in text_lower:
                return True
        
        # Verifica se é cabeçalho da tabela
        if text_lower in ['nome', 'matrícula', 'matricula', 'cpf', 'cnpj']:
            return True
        
        return False
    
    def is_address(self, text: str) -> bool:
        """Verifica se o texto parece um endereço"""
        if not text or pd.isna(text):
            return False
        
        text_upper = str(text).upper()
        address_keywords = [
            'RUA', 'AV', 'AVENIDA', 'ALAMEDA', 'TRAVESSA', 'RODOVIA',
            'KM', 'Nº', 'N°', 'S/N', 'APTO', 'APARTAMENTO', 'SALA',
            'ANDAR', 'BLOCO', 'CONJUNTO', 'LOTE', 'QUADRA', 'CEP',
            'BAIRRO', 'CIDADE', 'ESTADO', 'LOGRADOURO'
        ]
        
        for keyword in address_keywords:
            if keyword in text_upper:
                return True
        
        return False
    
    def extract_text_from_page(self, page) -> str:
        """
        Extrai texto de uma página com recorte preciso
        """
        page_height = page.height
        page_width = page.width
        
        # Define bounding box que ignora 15% do topo e 10% da base
        top_margin = page_height * 0.15  # 15% para cabeçalho
        bottom_margin = page_height * 0.90  # 10% para rodapé
        
        bbox = (0, top_margin, page_width, bottom_margin)
        
        # Extrai texto da área recortada
        cropped_page = page.within_bbox(bbox)
        text = cropped_page.extract_text()
        
        return text if text else ""
    
    def find_email_column(self, row: List[str]) -> Optional[int]:
        """Encontra a coluna que contém email"""
        if not row:
            return None
        
        for i, cell in enumerate(row):
            if cell and '@' in str(cell):
                return i
        
        return None
    
    def clean_name(self, name: str) -> str:
        """Limpa o nome do leiloeiro"""
        if not name or pd.isna(name):
            return ""
        
        name_str = str(name)
        
        # Remove números no final
        name_str = re.sub(r'[\d\s\-\./]+$', '', name_str)
        
        # Remove caracteres especiais no início
        name_str = re.sub(r'^[_\W]+', '', name_str)
        
        # Remove espaços extras
        name_str = name_str.strip()
        
        # Capitaliza se tudo for minúsculo
        if name_str and name_str.islower():
            words = name_str.split()
            capitalized_words = [word.capitalize() for word in words]
            name_str = ' '.join(capitalized_words)
        
        return name_str
    
    def extract_email(self, text: str) -> str:
        """Extrai email do texto"""
        if not text:
            return ""
        
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            email = email_match.group(0).lower()
            email = re.sub(r'\s+', '', email)
            return email
        
        return ""
    
    def process_text(self, text: str, page_num: int) -> List[Dict]:
        """Processa texto extraído para encontrar leiloeiros"""
        processed_rows = []
        
        if not text:
            return processed_rows
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Ignora linhas vazias
            if not line:
                continue
            
            # Ignora ruído
            if self.is_noise(line):
                continue
            
            # Ignora endereços
            if self.is_address(line):
                continue
            
            # Procura email na linha
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line)
            email = email_match.group(0).lower() if email_match else ""
            
            # Remove email da linha para obter nome
            nome_line = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', line)
            nome_line = nome_line.strip()
            
            # Se não tem email, tenta identificar nome
            if not email and len(nome_line) > 3:
                # Verifica se parece um nome (não tem números, não é muito curto)
                if not re.search(r'\d', nome_line) and len(nome_line.split()) >= 2:
                    nome_limpo = self.clean_name(nome_line)
                    if nome_limpo and len(nome_limpo) > 3:
                        record = {
                            'nome': nome_limpo,
                            'email': "",
                            'pagina': page_num,
                            'fonte': 'pdf_text_extractor'
                        }
                        processed_rows.append(record)
            elif email:
                # Tem email, extrai nome
                nome_limpo = self.clean_name(nome_line)
                if not nome_limpo or len(nome_limpo) < 3:
                    # Se não conseguiu extrair nome, usa parte do email
                    nome_parts = email.split('@')[0].split('.')
                    nome_limpo = ' '.join([part.capitalize() for part in nome_parts if part])
                
                if nome_limpo and len(nome_limpo) > 3:
                    record = {
                        'nome': nome_limpo,
                        'email': email,
                        'pagina': page_num,
                        'fonte': 'pdf_text_extractor'
                    }
                    processed_rows.append(record)
        
        return processed_rows
    
    def extract_all_pages(self) -> List[Dict]:
        """Extrai dados de todas as páginas"""
        print(f"📄 Extraindo texto de: {self.pdf_path.name}")
        
        if not self.pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {self.pdf_path}")
            return []
        
        all_data = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                print(f"📖 Processando {total_pages} páginas...")
                
                for page_num in range(total_pages):
                    print(f"   🔍 Página {page_num + 1}/{total_pages}...")
                    page = pdf.pages[page_num]
                    
                    # Extrai texto da página
                    text = self.extract_text_from_page(page)
                    
                    if text:
                        # Processa texto
                        processed_rows = self.process_text(text, page_num + 1)
                        all_data.extend(processed_rows)
                        print(f"   ✅ {len(processed_rows)} leiloeiros encontrados")
                    else:
                        print(f"   ⚠️  Nenhum texto extraído")
                
                print(f"\n✅ Total extraído: {len(all_data)} registros")
                
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return all_data
    
    def deduplicate_data(self, data: List[Dict]) -> List[Dict]:
        """Remove duplicados baseado no nome e email"""
        print("\n🔍 Removendo duplicados...")
        
        seen_records = set()
        unique_data = []
        
        for record in data:
            nome = record['nome']
            email = record['email']
            
            # Cria chave única
            record_key = f"{nome}_{email}"
            
            if record_key not in seen_records:
                seen_records.add(record_key)
                unique_data.append(record)
        
        print(f"✅ Após deduplicação: {len(unique_data)} registros únicos")
        return unique_data
    
    def save_results(self, data: List[Dict], output_path: str = "data/processed/lista_final_600.json"):
        """Salva resultados em JSON"""
        print(f"\n💾 Salvando dados finais...")
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dados salvos em: {output_path}")
        
        # Estatísticas
        df = pd.DataFrame(data)
        
        total = len(df)
        com_email = df[df['email'] != ''].shape[0]
        
        print(f"\n📊 Estatísticas finais:")
        print(f"   - Total de leiloeiros: {total}")
        print(f"   - Com email: {com_email} ({com_email/total*100:.1f}%)")
        print(f"   - Sem email: {total - com_email} ({(total - com_email)/total*100:.1f}%)")
        
        # Primeiros 10 registros para verificação
        print(f"\n🔍 Primeiros 10 registros:")
        for i, record in enumerate(data[:10], 1):
            print(f"   {i}. {record['nome'][:30]}...")
            if record['email']:
                print(f"      📧 {record['email']}")
        
        return output_file
    
    def run_extraction(self):
        """Executa extração completa"""
        print("=" * 70)
        print("🔧 LIMPEZA FINAL - EXTRAÇÃO DE TABELA COM PDFPLUMBER")
        print("=" * 70)
        
        # Extrai dados
        raw_data = self.extract_all_pages()
        
        if not raw_data:
            print("❌ Nenhum dado extraído")
            return None
        
        # Remove duplicados
        unique_data = self.deduplicate_data(raw_data)
        
        # Salva resultados
        output_path = self.save_results(unique_data)
        
        # Análise adicional
        print("\n📈 ANÁLISE DETALHADA:")
        print("-" * 50)
        
        df = pd.DataFrame(unique_data)
        
        # Distribuição por página
        print(f"\n📖 Distribuição por página:")
        page_counts = df['pagina'].value_counts().sort_index()
        for pagina, count in page_counts.items():
            print(f"   Página {pagina}: {count} leiloeiros")
        
        # Nomes mais comuns
        print(f"\n🔍 Nomes mais frequentes:")
        nome_counts = df['nome'].value_counts().head(5)
        for nome, count in nome_counts.items():
            print(f"   • {nome[:25]}...: {count} ocorrências")
        
        print(f"\n🎯 Meta: ~600 leiloeiros")
        print(f"📊 Atual: {len(unique_data)} leiloeiros extraídos")
        
        print("\n✅ Extração final concluída!")
        return output_path

def main():
    """Função principal"""
    extractor = PDFTableExtractor()
    output_path = extractor.run_extraction()
    
    if output_path:
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Execute o enriquecimento e classificação")
        print(f"   python src/processors/enrich_clean_data.py")
        print(f"   python src/processors/rank_final.py")
    else:
        print("\n❌ Falha na extração")

if __name__ == "__main__":
    main()
