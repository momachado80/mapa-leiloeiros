"""
Sistema de Enriquecimento de Dados de Leiloeiros
Combina lista de leiloeiros com sites extraídos de emails.
"""
import json
import re
from typing import List, Dict, Optional
from pathlib import Path

class LeiloeiroEnricher:
    """Enriquece dados de leiloeiros com sites extraídos de emails"""
    
    def __init__(self):
        self.leiloeiros_sp = []
        self.email_sites = []
        self.enriched_data = []
    
    def load_leiloeiros_sp(self, input_path: str = "data/raw/leiloeiros_sp.json") -> List[Dict]:
        """Carrega dados dos leiloeiros de SP"""
        filepath = Path(input_path)
        if not filepath.exists():
            print(f"❌ Arquivo não encontrado: {input_path}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ {len(data)} leiloeiros de SP carregados")
        return data
    
    def load_email_sites(self, input_path: str = "data/processed/email_sites.json") -> List[Dict]:
        """Carrega sites extraídos de emails"""
        filepath = Path(input_path)
        if not filepath.exists():
            print(f"❌ Arquivo não encontrado: {input_path}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sites = data.get('results', [])
        print(f"✅ {len(sites)} sites de emails carregados")
        return sites
    
    def extract_company_name_from_email(self, email: str) -> Optional[str]:
        """
        Extrai nome da empresa a partir do email.
        Exemplo: atendimento@zukleiloes.com.br -> ZUK LEILÕES
        """
        if not email or '@' not in email:
            return None
        
        domain = email.split('@')[1]
        domain_parts = domain.split('.')
        
        # Remove extensões comuns
        if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
            company_part = domain_parts[-3]
        elif len(domain_parts) >= 2:
            company_part = domain_parts[-2]
        else:
            company_part = domain_parts[0]
        
        # Remove hífens e underscores
        company_part = company_part.replace('-', ' ').replace('_', ' ')
        
        # Converte para formato de nome
        words = company_part.split()
        formatted_words = []
        for word in words:
            if word.upper() in ['LEILOES', 'LEILÕES', 'AUCTION', 'JUDICIAL']:
                formatted_words.append(word.upper())
            else:
                formatted_words.append(word.upper())
        
        company_name = ' '.join(formatted_words)
        
        # Adiciona "LEILÕES" se não estiver presente
        if 'LEILOES' not in company_name and 'LEILÕES' not in company_name and 'AUCTION' not in company_name:
            company_name = f"{company_name} LEILÕES"
        
        return company_name
    
    def match_leiloeiro_with_site(self, leiloeiro: Dict, email_sites: List[Dict]) -> Optional[Dict]:
        """
        Tenta encontrar correspondência entre leiloeiro e site.
        Usa heurísticas de correspondência de nomes.
        """
        leiloeiro_nome = leiloeiro.get('nome', '').upper()
        
        # Primeiro: verifica se já tem site
        existing_site = leiloeiro.get('site', '')
        if existing_site and existing_site != 'N/A' and not existing_site.startswith('https://www.example'):
            # Já tem site válido
            return {
                'site': existing_site,
                'match_type': 'existing',
                'confidence': 100
            }
        
        # Segundo: procura correspondência por nome da empresa no email
        best_match = None
        best_score = 0
        
        for email_site in email_sites:
            email = email_site.get('email', '')
            site = email_site.get('site', '')
            
            if not email or not site:
                continue
            
            # Extrai nome da empresa do email
            company_name = self.extract_company_name_from_email(email)
            if not company_name:
                continue
            
            # Calcula score de correspondência
            score = self.calculate_match_score(leiloeiro_nome, company_name)
            
            if score > best_score:
                best_score = score
                best_match = {
                    'site': site,
                    'email_source': email,
                    'company_name_from_email': company_name,
                    'match_type': 'email_domain',
                    'confidence': score
                }
        
        # Terceiro: procura por palavras-chave no nome do leiloeiro
        if not best_match or best_score < 30:
            for email_site in email_sites:
                email = email_site.get('email', '')
                site = email_site.get('site', '')
                domain = email_site.get('domain', '')
                
                # Verifica se o domínio contém palavras do nome do leiloeiro
                domain_upper = domain.upper()
                leiloeiro_words = leiloeiro_nome.split()
                
                for word in leiloeiro_words:
                    if len(word) > 3 and word in domain_upper:
                        best_match = {
                            'site': site,
                            'email_source': email,
                            'company_name_from_email': self.extract_company_name_from_email(email),
                            'match_type': 'keyword_in_domain',
                            'confidence': 50
                        }
                        break
        
        return best_match
    
    def calculate_match_score(self, leiloeiro_nome: str, company_name: str) -> int:
        """
        Calcula score de correspondência entre nomes.
        """
        score = 0
        
        # Normaliza nomes
        leiloeiro_norm = leiloeiro_nome.replace('LTDA', '').replace('ME', '').replace('S/A', '').strip()
        company_norm = company_name.replace('LEILÕES', '').replace('LEILOES', '').replace('AUCTION', '').strip()
        
        # Palavras em comum
        leiloeiro_words = set(leiloeiro_norm.split())
        company_words = set(company_norm.split())
        
        common_words = leiloeiro_words.intersection(company_words)
        if common_words:
            score += len(common_words) * 20
        
        # Verifica se um nome contém o outro
        if company_norm in leiloeiro_norm or leiloeiro_norm in company_norm:
            score += 30
        
        # Verifica siglas/combinções
        if any(word in leiloeiro_norm for word in ['ZUK', 'MEGA', 'SATO']):
            if any(word in company_norm for word in ['ZUK', 'MEGA', 'SATO']):
                score += 40
        
        return min(score, 100)
    
    def enrich_all(self) -> List[Dict]:
        """Processa todos os leiloeiros"""
        print("🔗 Enriquecendo dados de leiloeiros...")
        print("=" * 50)
        
        # Carrega dados
        self.leiloeiros_sp = self.load_leiloeiros_sp()
        self.email_sites = self.load_email_sites()
        
        if not self.leiloeiros_sp or not self.email_sites:
            print("❌ Dados insuficientes para enriquecimento")
            return []
        
        # Processa cada leiloeiro
        enriched = []
        for leiloeiro in self.leiloeiros_sp:
            print(f"\n🔍 Processando: {leiloeiro.get('nome', 'N/A')}")
            
            # Tenta encontrar correspondência
            match = self.match_leiloeiro_with_site(leiloeiro, self.email_sites)
            
            if match:
                print(f"   ✅ Site encontrado: {match['site']}")
                print(f"   📊 Confiança: {match['confidence']}% | Tipo: {match['match_type']}")
                
                enriched_leiloeiro = {
                    **leiloeiro,
                    'site_enriquecido': match['site'],
                    'site_original': leiloeiro.get('site', 'N/A'),
                    'enrichment_info': {
                        'confidence': match['confidence'],
                        'match_type': match['match_type'],
                        'email_source': match.get('email_source'),
                        'company_name_from_email': match.get('company_name_from_email')
                    }
                }
            else:
                print(f"   ⚠ Nenhum site correspondente encontrado")
                enriched_leiloeiro = {
                    **leiloeiro,
                    'site_enriquecido': leiloeiro.get('site', 'N/A'),
                    'site_original': leiloeiro.get('site', 'N/A'),
                    'enrichment_info': {
                        'confidence': 0,
                        'match_type': 'no_match',
                        'email_source': None,
                        'company_name_from_email': None
                    }
                }
            
            enriched.append(enriched_leiloeiro)
        
        self.enriched_data = enriched
        return enriched
    
    def save_enriched_data(self, output_path: str = "data/processed/leiloeiros_enriquecidos.json"):
        """Salva dados enriquecidos"""
        if not self.enriched_data:
            print("❌ Nenhum dado para salvar")
            return
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Formata dados para saída
        output_data = []
        for item in self.enriched_data:
            output_data.append({
                'nome': item['nome'],
                'matricula': item['matricula'],
                'site_original': item.get('site_original', 'N/A'),
                'site_enriquecido': item.get('site_enriquecido', 'N/A'),
                'enrichment_confidence': item['enrichment_info']['confidence'],
                'enrichment_match_type': item['enrichment_info']['match_type'],
                'has_site_improvement': item['site_enriquecido'] != item['site_original'] and 
                                       item['site_original'] not in ['N/A', 'https://www.example.com']
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Dados enriquecidos salvos em: {output_path}")
        
        # Estatísticas
        improved = sum(1 for item in output_data if item['has_site_improvement'])
        total = len(output_data)
        
        print(f"📊 Estatísticas de enriquecimento:")
        print(f"   - Total de leiloeiros: {total}")
        print(f"   - Sites melhorados: {improved}")
        print(f"   - Taxa de sucesso: {(improved/total*100):.1f}%")
        
        # Distribuição por confiança
        confidence_levels = {'alta (80-100%)': 0, 'média (50-79%)': 0, 'baixa (<50%)': 0}
        for item in output_data:
            conf = item['enrichment_confidence']
            if conf >= 80:
                confidence_levels['alta (80-100%)'] += 1
            elif conf >= 50:
                confidence_levels['média (50-79%)'] += 1
            else:
                confidence_levels['baixa (<50%)'] += 1
        
        print(f"   - Confiança da correspondência:")
        for level, count in confidence_levels.items():
            print(f"     {level}: {count} leiloeiros")
        
        return output_data

def main():
    """Função principal"""
    print("=" * 60)
    print("🔗 SISTEMA DE ENRIQUECIMENTO DE LEILOEIROS")
    print("=" * 60)
    
    try:
        # Inicializa enricher
        enricher = LeiloeiroEnricher()
        
        # Processa enriquecimento
        print("\n" + "-" * 60)
        print("🔄 PROCESSANDO ENRIQUECIMENTO")
        print("-" * 60)
        
        enriched_data = enricher.enrich_all()
        
        if not enriched_data:
            print("❌ Falha no enriquecimento")
            return
        
        # Salva resultados
        print("\n" + "-" * 60)
        print("💾 SALVANDO RESULTADOS")
        print("-" * 60)
        
        output_data = enricher.save_enriched_data()
        
        # Mostra exemplos
        print("\n" + "=" * 60)
        print("🏆 EXEMPLOS DE LEILOEIROS ENRIQUECIDOS")
        print("=" * 60)
        
        # Filtra os que tiveram melhoria
        improved = [item for item in output_data if item['has_site_improvement']]
        
        if improved:
            for i, item in enumerate(improved[:3], 1):
                print(f"\n{i}. {item['nome']}")
                print(f"   📝 Matrícula: {item['matricula']}")
                print(f"   🔄 Site original: {item['site_original']}")
                print(f"   🎯 Site enriquecido: {item['site_enriquecido']}")
                print(f"   📊 Confiança: {item['enrichment_confidence']}%")
        else:
            print("\n⚠ Nenhum leiloeiro teve site melhorado.")
            print("  (Todos já tinham sites válidos ou não houve correspondência)")
        
        print("\n✅ Enriquecimento concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
