"""
Extrator de Dados de Leiloeiros de PDFs
Identifica automaticamente o PDF correto e extrai dados em massa.
"""
import pdfplumber
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys

class PDFLeiloeiroExtractor:
    """Extrai dados de leiloeiros de PDFs da pasta docs/"""
    
    # Domínios de email genéricos para filtrar
    GENERIC_DOMAINS = {
        'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
        'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
        'globo.com', 'live.com', 'msn.com', 'aol.com',
        'gmail.com.br', 'hotmail.com.br', 'yahoo.com.br'
    }
    
    def __init__(self, docs_path: str = "docs"):
        self.docs_path = Path(docs_path)
        self.pdf_files = []
        self.target_pdf = None
        self.extracted_data = []
        
    def list_pdfs(self) -> List[Path]:
        """Lista todos os PDFs na pasta docs/"""
        if not self.docs_path.exists():
            print(f"❌ Pasta não encontrada: {self.docs_path}")
            return []
        
        pdf_files = list(self.docs_path.glob("*.pdf"))
        print(f"📁 PDFs encontrados em {self.docs_path}: {len(pdf_files)}")
        
        for pdf in pdf_files:
            print(f"   - {pdf.name} ({pdf.stat().st_size / 1024 / 1024:.1f} MB)")
        
        self.pdf_files = pdf_files
        return pdf_files
    
    def identify_target_pdf(self) -> Optional[Path]:
        """
        Identifica o PDF que contém 'Matrícula' e 'Situação' na primeira página.
        Retorna o caminho do PDF alvo.
        """
        if not self.pdf_files:
            print("❌ Nenhum PDF para analisar")
            return None
        
        print("\n🔍 Identificando PDF de leiloeiros...")
        print("=" * 50)
        
        for pdf_path in self.pdf_files:
            print(f"\n📄 Analisando: {pdf_path.name}")
            
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    if len(pdf.pages) == 0:
                        print("   ⚠ PDF sem páginas")
                        continue
                    
                    # Extrai texto da primeira página
                    first_page = pdf.pages[0]
                    text = first_page.extract_text()
                    
                    if not text:
                        print("   ⚠ Primeira página sem texto extraível")
                        continue
                    
                    # Verifica palavras-chave
                    has_matricula = "Matrícula" in text or "matrícula" in text
                    has_situacao = "Situação" in text or "situação" in text
                    
                    print(f"   📝 Texto extraído: {len(text)} caracteres")
                    print(f"   🔑 'Matrícula' encontrado: {has_matricula}")
                    print(f"   🔑 'Situação' encontrado: {has_situacao}")
                    
                    if has_matricula and has_situacao:
                        print(f"   ✅ IDENTIFICADO! Este é o PDF de leiloeiros")
                        print(f"   📊 Total de páginas: {len(pdf.pages)}")
                        self.target_pdf = pdf_path
                        return pdf_path
                    else:
                        print("   ⚠ Não é o PDF de leiloeiros (ignorando)")
                        
            except Exception as e:
                print(f"   ❌ Erro ao processar {pdf_path.name}: {str(e)}")
        
        print("\n❌ Nenhum PDF com 'Matrícula' e 'Situação' encontrado")
        return None
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extrai todos os emails do texto"""
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
    
    def extract_names_from_text(self, text: str) -> List[str]:
        """
        Extrai nomes de leiloeiros do texto.
        Heurística: linhas que parecem nomes completos.
        """
        lines = text.split('\n')
        names = []
        
        for line in lines:
            line = line.strip()
            
            # Filtra linhas muito curtas ou muito longas
            if len(line) < 5 or len(line) > 100:
                continue
            
            # Deve conter pelo menos um espaço (nome e sobrenome)
            if ' ' not in line:
                continue
            
            # Não deve ser apenas números ou caracteres especiais
            if re.match(r'^[\d\s\-\.]+$', line):
                continue
            
            # Não deve conter palavras-chave de tabela
            table_keywords = ['Matrícula', 'Situação', 'E-mail', 'Telefone', 
                            'Endereço', 'Página', 'Total', 'Data']
            if any(keyword in line for keyword in table_keywords):
                continue
            
            # Parece um nome válido
            names.append(line)
        
        return names
    
    def is_corporate_email(self, email: str) -> bool:
        """Verifica se o email é corporativo (não genérico)"""
        domain = email.split('@')[-1].lower()
        
        for generic_domain in self.GENERIC_DOMAINS:
            if domain.endswith(generic_domain):
                return False
        
        return True
    
    def extract_site_from_email(self, email: str) -> Optional[str]:
        """Extrai site a partir do email corporativo"""
        if not self.is_corporate_email(email):
            return None
        
        domain = email.split('@')[-1]
        domain_parts = domain.split('.')
        
        if len(domain_parts) >= 2:
            # Pega os últimos 2 ou 3 partes (ex: leiloesx.com.br)
            if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
                main_domain = '.'.join(domain_parts[-3:])
            else:
                main_domain = '.'.join(domain_parts[-2:])
            
            return f"https://www.{main_domain}"
        
        return None
    
    def extract_data_from_pdf(self) -> List[Dict]:
        """Extrai dados de todas as páginas do PDF alvo"""
        if not self.target_pdf:
            print("❌ Nenhum PDF alvo identificado")
            return []
        
        print(f"\n📊 Extraindo dados de: {self.target_pdf.name}")
        print("=" * 50)
        
        all_data = []
        total_pages = 0
        
        try:
            with pdfplumber.open(self.target_pdf) as pdf:
                total_pages = len(pdf.pages)
                print(f"📄 Total de páginas para processar: {total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"\n   📖 Processando página {page_num}/{total_pages}...")
                    
                    text = page.extract_text()
                    if not text:
                        print(f"   ⚠ Página {page_num} sem texto extraível")
                        continue
                    
                    # Extrai emails
                    emails = self.extract_emails_from_text(text)
                    print(f"   📧 Emails encontrados: {len(emails)}")
                    
                    # Extrai nomes (heurística)
                    names = self.extract_names_from_text(text)
                    print(f"   👤 Nomes encontrados: {len(names)}")
                    
                    # Combina dados (simplificado - na prática precisaria de parsing de tabela)
                    for email in emails:
                        # Tenta encontrar nome correspondente (heurística simples)
                        corresponding_name = None
                        for name in names:
                            # Verifica se o nome está perto do email no texto
                            name_pos = text.find(name)
                            email_pos = text.find(email)
                            
                            if name_pos != -1 and email_pos != -1:
                                distance = abs(name_pos - email_pos)
                                if distance < 500:  # Nome e email próximos no texto
                                    corresponding_name = name
                                    break
                        
                        # Cria registro
                        record = {
                            'nome': corresponding_name or f"Leiloeiro {len(all_data) + 1}",
                            'email': email,
                            'email_corporativo': self.is_corporate_email(email),
                            'pagina': page_num
                        }
                        
                        # Adiciona site se email for corporativo
                        if record['email_corporativo']:
                            site = self.extract_site_from_email(email)
                            if site:
                                record['site'] = site
                                print(f"   🌐 Site extraído: {site}")
                        
                        all_data.append(record)
                    
                    # Progresso
                    if page_num % 5 == 0 or page_num == total_pages:
                        print(f"   📊 Progresso: {page_num}/{total_pages} páginas")
                        print(f"   📈 Registros acumulados: {len(all_data)}")
        
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n✅ Extração concluída!")
        print(f"📊 Total de registros extraídos: {len(all_data)}")
        
        self.extracted_data = all_data
        return all_data
    
    def save_to_json(self, output_path: str = "data/processed/leiloeiros_enriquecidos.json"):
        """Salva dados extraídos em arquivo JSON"""
        if not self.extracted_data:
            print("❌ Nenhum dado para salvar")
            return False
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Formata dados para saída
        formatted_data = []
        for record in self.extracted_data:
            formatted_record = {
                'nome': record['nome'],
                'email': record['email'],
                'email_corporativo': record['email_corporativo'],
                'pagina_origem': record.get('pagina', 0)
            }
            
            if 'site' in record:
                formatted_record['site'] = record['site']
            
            formatted_data.append(formatted_record)
        
        # Salva em JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Dados salvos em: {output_path}")
        print(f"📊 Estatísticas finais:")
        print(f"   - Total de leiloeiros: {len(formatted_data)}")
        
        # Conta emails corporativos
        corporate_emails = sum(1 for r in formatted_data if r['email_corporativo'])
        print(f"   - Emails corporativos: {corporate_emails}")
        
        # Conta sites extraídos
        sites_extracted = sum(1 for r in formatted_data if 'site' in r)
        print(f"   - Sites extraídos: {sites_extracted}")
        
        return True
    
    def run_full_extraction(self):
        """Executa o pipeline completo de extração"""
        print("=" * 60)
        print("🔧 EXTRATOR DE LEILOEIROS DE PDFs")
        print("=" * 60)
        
        # Passo 1: Listar PDFs
        self.list_pdfs()
        
        # Passo 2: Identificar PDF alvo
        target_pdf = self.identify_target_pdf()
        if not target_pdf:
            print("\n❌ Pipeline interrompido: PDF alvo não encontrado")
            return False
        
        # Passo 3: Extrair dados em massa
        self.extract_data_from_pdf()
        
        # Passo 4: Salvar resultados
        success = self.save_to_json()
        
        if success:
            print("\n✅ Pipeline de extração concluído com sucesso!")
            return True
        else:
            print("\n❌ Falha no pipeline de extração")
            return False

def main():
    """Função principal"""
    extractor = PDFLeiloeiroExtractor()
    success = extractor.run_full_extraction()
    
    if success:
        # Retorna caminho do arquivo gerado para uso posterior
        output_path = "data/processed/leiloeiros_enriquecidos.json"
        print(f"\n📁 Arquivo gerado: {output_path}")
        return output_path
    else:
        return None

if __name__ == "__main__":
    main()
