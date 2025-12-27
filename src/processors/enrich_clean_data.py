"""
Enriquece dados limpos com emails e sites dos dados OCR existentes
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
import re

class DataEnricher:
    """Enriquece dados limpos com informações de emails e sites"""
    
    def __init__(self):
        self.clean_data_path = Path("data/processed/lista_final_600.json")
        self.ocr_data_path = Path("data/processed/leiloeiros_ocr.json")
        self.enriched_data_path = Path("data/processed/leiloeiros_enriquecidos_final_v2.json")
        
    def load_clean_data(self) -> List[Dict]:
        """Carrega dados limpos extraídos"""
        print(f"📁 Carregando dados limpos: {self.clean_data_path.name}")
        
        if not self.clean_data_path.exists():
            print(f"❌ Arquivo não encontrado: {self.clean_data_path}")
            return []
        
        with open(self.clean_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Dados limpos carregados: {len(data)} leiloeiros")
        return data
    
    def load_ocr_data(self) -> Dict[str, Dict]:
        """Carrega dados OCR com emails e cria dicionário para busca"""
        print(f"📁 Carregando dados OCR: {self.ocr_data_path.name}")
        
        if not self.ocr_data_path.exists():
            print(f"❌ Arquivo não encontrado: {self.ocr_data_path}")
            return {}
        
        with open(self.ocr_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cria dicionário para busca rápida por nome
        ocr_dict = {}
        for item in data:
            nome = item.get('nome', '')
            if nome:
                # Normaliza nome para busca
                nome_normalizado = self.normalize_name(nome)
                if nome_normalizado:
                    ocr_dict[nome_normalizado] = item
        
        print(f"✅ Dados OCR carregados: {len(data)} registros, {len(ocr_dict)} nomes únicos")
        return ocr_dict
    
    def normalize_name(self, name: str) -> str:
        """Normaliza nome para comparação"""
        if not name:
            return ""
        
        # Remove caracteres especiais e espaços extras
        name = re.sub(r'[^\w\s]', '', str(name))
        name = re.sub(r'\s+', ' ', name)
        name = name.strip().upper()
        
        return name
    
    def find_best_match(self, clean_name: str, ocr_dict: Dict[str, Dict]) -> Dict:
        """Encontra melhor correspondência para o nome nos dados OCR"""
        clean_normalized = self.normalize_name(clean_name)
        
        if not clean_normalized:
            return {}
        
        # Tenta encontrar correspondência exata
        if clean_normalized in ocr_dict:
            return ocr_dict[clean_normalized]
        
        # Tenta encontrar correspondência parcial
        for ocr_name, ocr_data in ocr_dict.items():
            if (clean_normalized in ocr_name or 
                ocr_name in clean_normalized or
                self.similarity_score(clean_normalized, ocr_name) > 0.7):
                return ocr_data
        
        return {}
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """Calcula similaridade entre duas strings"""
        if not str1 or not str2:
            return 0.0
        
        # Converte para conjuntos de palavras
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calcula interseção
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def extract_site_from_email(self, email: str) -> str:
        """Extrai site do email corporativo"""
        if not email or pd.isna(email) or email == "":
            return None
        
        generic_domains = {
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
            'globo.com', 'live.com', 'msn.com', 'aol.com',
            'gmail.com.br', 'hotmail.com.br', 'yahoo.com.br'
        }
        
        try:
            domain = email.split('@')[-1].lower()
            
            # Verifica se é email genérico
            if any(domain.endswith(generic) for generic in generic_domains):
                return None
            
            # Extrai site do domínio
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
                    main_domain = '.'.join(domain_parts[-3:])
                else:
                    main_domain = '.'.join(domain_parts[-2:])
                
                return f"https://www.{main_domain}"
        except:
            pass
        
        return None
    
    def enrich_data(self, clean_data: List[Dict], ocr_dict: Dict[str, Dict]) -> List[Dict]:
        """Enriquece dados limpos com informações dos dados OCR"""
        print("\n🔍 Enriquecendo dados com emails e sites...")
        
        enriched_data = []
        matches_found = 0
        
        for item in clean_data:
            clean_name = item.get('nome', '')
            
            # Busca correspondência nos dados OCR
            ocr_match = self.find_best_match(clean_name, ocr_dict)
            
            if ocr_match:
                matches_found += 1
                email = ocr_match.get('email', '')
                site = self.extract_site_from_email(email)
                
                enriched_item = {
                    'nome': clean_name,
                    'email': email if email else "",
                    'email_corporativo': bool(email and not self.extract_site_from_email(email) is None),
                    'site': site if site else None,
                    'pagina': item.get('pagina', 0),
                    'fonte_clean': item.get('fonte', ''),
                    'fonte_ocr': ocr_match.get('fonte', ''),
                    'enriquecido': True
                }
            else:
                # Mantém dados originais se não encontrar correspondência
                enriched_item = {
                    'nome': clean_name,
                    'email': "",
                    'email_corporativo': False,
                    'site': None,
                    'pagina': item.get('pagina', 0),
                    'fonte_clean': item.get('fonte', ''),
                    'fonte_ocr': '',
                    'enriquecido': False
                }
            
            enriched_data.append(enriched_item)
        
        print(f"✅ Correspondências encontradas: {matches_found} de {len(clean_data)} ({matches_found/len(clean_data)*100:.1f}%)")
        return enriched_data
    
    def save_enriched_data(self, data: List[Dict]):
        """Salva dados enriquecidos em JSON"""
        print(f"\n💾 Salvando dados enriquecidos...")
        
        self.enriched_data_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.enriched_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dados enriquecidos salvos em: {self.enriched_data_path}")
        
        # Estatísticas
        df = pd.DataFrame(data)
        
        total = len(df)
        com_email = df[df['email'] != ''].shape[0]
        com_site = df[df['site'].notna()].shape[0]
        enriquecidos = df['enriquecido'].sum()
        
        print(f"\n📊 Estatísticas dos dados enriquecidos:")
        print(f"   - Total de leiloeiros: {total}")
        print(f"   - Com email: {com_email} ({com_email/total*100:.1f}%)")
        print(f"   - Com site: {com_site} ({com_site/total*100:.1f}%)")
        print(f"   - Enriquecidos: {int(enriquecidos)} ({enriquecidos/total*100:.1f}%)")
        
        # Primeiros 10 registros para verificação
        print(f"\n🔍 Primeiros 10 registros enriquecidos:")
        for i, record in enumerate(data[:10], 1):
            print(f"   {i}. {record['nome'][:30]}...")
            if record['email']:
                print(f"      📧 {record['email']}")
            if record['site']:
                print(f"      🌐 {record['site']}")
        
        return self.enriched_data_path
    
    def run_enrichment(self):
        """Executa pipeline completo de enriquecimento"""
        print("=" * 70)
        print("🔧 ENRIQUECIMENTO DE DADOS LIMPOS")
        print("=" * 70)
        
        # 1. Carrega dados limpos
        clean_data = self.load_clean_data()
        if not clean_data:
            print("❌ Falha ao carregar dados limpos")
            return
        
        # 2. Carrega dados OCR
        ocr_dict = self.load_ocr_data()
        
        # 3. Enriquece dados
        enriched_data = self.enrich_data(clean_data, ocr_dict)
        
        # 4. Salva dados enriquecidos
        output_path = self.save_enriched_data(enriched_data)
        
        print("\n" + "=" * 70)
        print("✅ ENRIQUECIMENTO CONCLUÍDO!")
        print("=" * 70)
        
        print(f"\n📁 Arquivo gerado: {output_path}")
        print(f"🚀 Próximo passo: Execute o ranqueamento final")
        print(f"   python src/processors/rank_final.py")
        
        return output_path

def main():
    """Função principal"""
    enricher = DataEnricher()
    output_path = enricher.run_enrichment()
    
    if output_path:
        print(f"\n🎯 Dados prontos para ranqueamento!")
    else:
        print("\n❌ Falha no enriquecimento")

if __name__ == "__main__":
    main()
