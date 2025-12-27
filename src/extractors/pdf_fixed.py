"""
Extrator Limpo de Leiloeiros - Regras Rígidas Anti-Ruído
Extrai apenas nomes válidos ignorando marca d'água e cabeçalhos.
"""
import pdfplumber
import re
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd

class PDFCleanExtractor:
    """Extrai leiloeiros com regras rígidas anti-ruído"""
    
    def __init__(self, pdf_path: str = "docs/Leiloeiros de SP.pdf"):
        self.pdf_path = Path(pdf_path)
        self.noise_patterns = [
            'Adriano Duarte',
            'duarte.adriano',
            'Licensed to',
            '28255301828',
            'Matricula',
            'Posse',
            'MATRÍCULA',
            'POSSE',
            'NOME',
            'NOME DO LEILOEIRO'
        ]
        
    def is_noise(self, text: str) -> bool:
        """Verifica se o texto é ruído/marca d'água"""
        if not text:
            return True
        
        text_lower = text.lower()
        
        # Verifica padrões de ruído
        for pattern in self.noise_patterns:
            if pattern.lower() in text_lower:
                return True
        
        # Verifica se é muito curto
        if len(text.strip()) < 3:
            return True
        
        # Verifica se contém números (nomes não devem ter números)
        if re.search(r'\d', text):
            return True
        
        # Verifica se é cabeçalho da tabela
        if text_lower in ['matricula', 'posse', 'nome', 'nome do leiloeiro']:
            return True
        
        return False
    
    def extract_names_from_page(self, page) -> List[str]:
        """
        Extrai nomes de uma página com bounding box que ignora cabeçalho/rodapé
        """
        page_height = page.height
        page_width = page.width
        
        # Define bounding box que ignora 10% do topo (cabeçalho) e 10% da base (rodapé)
        top_margin = page_height * 0.10
        bottom_margin = page_height * 0.90
        
        bbox = (0, top_margin, page_width * 0.35, bottom_margin)  # Apenas primeira coluna
        
        # Extrai texto da área definida
        cropped_page = page.within_bbox(bbox)
        text = cropped_page.extract_text() or ""
        
        # Processa linhas
        names = []
        for line in text.split('\n'):
            line = line.strip()
            
            # Ignora ruído
            if self.is_noise(line):
                continue
            
            # Remove espaços extras
            line = re.sub(r'\s+', ' ', line)
            
            # Remove números e caracteres especiais
            clean_line = re.sub(r'[\d\-/\.]+', '', line)
            clean_line = clean_line.strip()
            
            # Validação final
            if (clean_line and 
                len(clean_line) > 3 and 
                not re.search(r'\d', clean_line) and
                not self.is_noise(clean_line)):
                
                # Capitaliza nome
                words = clean_line.split()
                capitalized_words = []
                for word in words:
                    if word and len(word) > 1:
                        if word.isupper():
                            capitalized_words.append(word.title())
                        elif word.islower():
                            capitalized_words.append(word.capitalize())
                        else:
                            capitalized_words.append(word)
                
                final_name = ' '.join(capitalized_words)
                if final_name and len(final_name) > 3:
                    names.append(final_name)
        
        return names
    
    def extract_all_pages(self, page_limit: int = 19) -> List[Dict]:
        """Extrai dados de todas as páginas"""
        print(f"📄 Extraindo dados limpos de: {self.pdf_path.name}")
        
        if not self.pdf_path.exists():
            print(f"❌ Arquivo não encontrado: {self.pdf_path}")
            return []
        
        all_data = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(page_limit, total_pages)
                
                print(f"📖 Processando {pages_to_process} de {total_pages} páginas...")
                
                for page_num in range(pages_to_process):
                    print(f"   🔍 Página {page_num + 1}/{pages_to_process}...")
                    page = pdf.pages[page_num]
                    
                    # Extrai nomes da página
                    names = self.extract_names_from_page(page)
                    
                    # Adiciona cada nome como registro
                    for name in names:
                        record = {
                            'nome': name,
                            'email': "",  # Vazio por padrão
                            'site': None,  # Null como solicitado
                            'pagina': page_num + 1,
                            'fonte': 'pdf_clean_extractor'
                        }
                        all_data.append(record)
                    
                    print(f"   ✅ {len(names)} nomes válidos encontrados")
                
                print(f"\n✅ Total extraído: {len(all_data)} registros")
                
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return all_data
    
    def deduplicate_data(self, data: List[Dict]) -> List[Dict]:
        """Remove duplicados baseado no nome"""
        print("\n🔍 Removendo duplicados...")
        
        seen_names = set()
        unique_data = []
        
        for record in data:
            nome = record['nome']
            if nome not in seen_names:
                seen_names.add(nome)
                unique_data.append(record)
        
        print(f"✅ Após deduplicação: {len(unique_data)} registros únicos")
        return unique_data
    
    def save_raw_data(self, data: List[Dict], output_path: str = "data/processed/leiloeiros_limpos.json"):
        """Salva dados brutos em JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Dados limpos salvos em: {output_path}")
        print(f"📊 Estatísticas brutas:")
        print(f"   - Total de registros: {len(data)}")
        
        # Primeiros 10 nomes para verificação
        print(f"\n🔍 Primeiros 10 nomes extraídos:")
        for i, record in enumerate(data[:10], 1):
            print(f"   {i}. {record['nome']}")
        
        return output_file
    
    def run_extraction(self):
        """Executa extração completa"""
        print("=" * 70)
        print("🔧 EXTRATOR LIMPO - REGRAS RÍGIDAS ANTI-RUÍDO")
        print("=" * 70)
        
        # Extrai dados
        raw_data = self.extract_all_pages(page_limit=19)  # Processa todas as páginas
        
        if not raw_data:
            print("❌ Nenhum dado extraído")
            return None
        
        # Remove duplicados
        unique_data = self.deduplicate_data(raw_data)
        
        # Salva dados brutos
        output_path = self.save_raw_data(unique_data)
        
        # Análise
        print("\n📈 ANÁLISE DOS DADOS LIMPOS:")
        print("-" * 50)
        
        df = pd.DataFrame(unique_data)
        
        # Distribuição por página
        print(f"\n📖 Distribuição por página:")
        page_counts = df['pagina'].value_counts().sort_index()
        for pagina, count in page_counts.items():
            print(f"   Página {pagina}: {count} leiloeiros")
        
        # Nomes mais longos (para verificação)
        print(f"\n🔍 Nomes mais longos (verificação de qualidade):")
        df['nome_length'] = df['nome'].str.len()
        top_long_names = df.nlargest(5, 'nome_length')[['nome', 'pagina']]
        for idx, row in top_long_names.iterrows():
            print(f"   • {row['nome']} (Página {row['pagina']})")
        
        print(f"\n🎯 Meta: ~613 leiloeiros")
        print(f"📊 Atual: {len(unique_data)} leiloeiros extraídos")
        
        print("\n✅ Extração limpa concluída!")
        return output_path

def main():
    """Função principal"""
    extractor = PDFCleanExtractor()
    output_path = extractor.run_extraction()
    
    if output_path:
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Enriquecer com emails e sites")
        print(f"   python src/processors/enrich_leiloeiros.py")
    else:
        print("\n❌ Falha na extração")

if __name__ == "__main__":
    main()
