"""
Limpeza Final com OCR - Extração de PDF escaneado com pytesseract
"""
import pdfplumber
import pytesseract
from PIL import Image
import json
import re
from pathlib import Path
from typing import List, Dict
import pandas as pd

class PDFOCRExtractor:
    """Extrai leiloeiros de PDF escaneado usando OCR"""
    
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
            'CNPJ',
            'Posse',
            'POSSE'
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
        if text_lower in ['nome', 'matrícula', 'matricula', 'cpf', 'cnpj', 'posse']:
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
            'BAIRRO', 'CIDADE', 'ESTADO', 'LOGRADOURO', 'ENDEREÇO'
        ]
        
        for keyword in address_keywords:
            if keyword in text_upper:
                return True
        
        return False
    
    def extract_text_with_ocr(self, page, resolution: int = 200) -> str:
        """
        Extrai texto de uma página usando OCR
        """
        # Converte página para imagem
        im = page.to_image(resolution=resolution)
        pil_image = im.original
        
        # Obtém dimensões
        width, height = pil_image.size
        
        # Define bounding box que ignora 15% do topo e 10% da base
        top_margin = int(height * 0.15)  # 15% para cabeçalho
        bottom_margin = int(height * 0.90)  # 10% para rodapé
        
        bbox = (0, top_margin, width, bottom_margin)
        
        # Corta imagem
        cropped_image = pil_image.crop(bbox)
        
        # Aplica OCR
        try:
            text = pytesseract.image_to_string(cropped_image, lang='por')
        except:
            # Se falhar, tenta sem idioma
            text = pytesseract.image_to_string(cropped_image)
        
        return text
    
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
    
    def process_ocr_text(self, text: str, page_num: int) -> List[Dict]:
        """Processa texto OCR para encontrar leiloeiros"""
        processed_rows = []
        
        if not text:
            return processed_rows
        
        lines = text.split('\n')
        
        current_name = ""
        current_email = ""
        
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
            email = self.extract_email(line)
            
            if email:
                # Linha tem email
                if current_name:
                    # Tem nome acumulado, cria registro
                    nome_limpo = self.clean_name(current_name)
                    if nome_limpo and len(nome_limpo) > 3:
                        record = {
                            'nome': nome_limpo,
                            'email': email,
                            'pagina': page_num,
                            'fonte': 'pdf_ocr_extractor'
                        }
                        processed_rows.append(record)
                    
                    # Reseta acumuladores
                    current_name = ""
                    current_email = ""
                else:
                    # Não tem nome acumulado, tenta extrair nome da linha
                    nome_line = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', line)
                    nome_line = nome_line.strip()
                    
                    nome_limpo = self.clean_name(nome_line)
                    if not nome_limpo or len(nome_limpo) < 3:
                        # Usa parte do email como nome
                        nome_parts = email.split('@')[0].split('.')
                        nome_limpo = ' '.join([part.capitalize() for part in nome_parts if part])
                    
                    if nome_limpo and len(nome_limpo) > 3:
                        record = {
                            'nome': nome_limpo,
                            'email': email,
                            'pagina': page_num,
                            'fonte': 'pdf_ocr_extractor'
                        }
                        processed_rows.append(record)
            else:
                # Linha não tem email, pode ser nome
                if len(line) > 3 and not re.search(r'\d', line):
                    # Acumula nome (pode ser nome completo em várias linhas)
                    if current_name:
                        current_name += " " + line
                    else:
                        current_name = line
        
        # Processa último nome acumulado (se houver)
        if current_name and not current_email:
            nome_limpo = self.clean_name(current_name)
            if nome_limpo and len(nome_limpo) > 3:
                record = {
                    'nome': nome_limpo,
                    'email': "",
                    'pagina': page_num,
                    'fonte': 'pdf_ocr_extractor'
                }
                processed_rows.append(record)
        
        return processed_rows
    
    def extract_all_pages(self, page_limit: int = 10) -> List[Dict]:
        """Extrai dados de todas as páginas com OCR"""
        print(f"📄 Extraindo com OCR de: {self.pdf_path.name}")
        
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
                    
                    # Extrai texto com OCR
                    text = self.extract_text_with_ocr(page)
                    
                    if text:
                        # Processa texto OCR
                        processed_rows = self.process_ocr_text(text, page_num + 1)
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
    
    def run_extraction(self, page_limit: int = 10):
        """Executa extração completa"""
        print("=" * 70)
        print("🔧 LIMPEZA FINAL COM OCR - EXTRAÇÃO DE PDF ESCANEADO")
        print("=" * 70)
        
        # Extrai dados
        raw_data = self.extract_all_pages(page_limit=page_limit)
        
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
        
        print("\n✅ Extração final com OCR concluída!")
        return output_path

def main():
    """Função principal"""
    extractor = PDFOCRExtractor()
    
    # Processa mais páginas para tentar obter mais dados
    output_path = extractor.run_extraction(page_limit=10)
    
    if output_path:
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Execute o enriquecimento e classificação")
        print(f"   python src/processors/enrich_clean_data.py")
        print(f"   python src/processors/rank_final.py")
    else:
        print("\n❌ Falha na extração")

if __name__ == "__main__":
    main()
