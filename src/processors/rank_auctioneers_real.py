"""
Sistema de Ranqueamento de Autoridade para Leiloeiros - VERSÃO REAL
Analisa métricas de SEO e tecnologia usando dados reais extraídos do PDF.
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
import sys

class RealAuctioneerRanker:
    """Classifica leiloeiros baseado em métricas simplificadas usando dados reais"""
    
    def __init__(self):
        self.data = []
        
    def load_real_data(self, input_path: str = "data/processed/leiloeiros_enriquecidos.json") -> List[Dict]:
        """Carrega os dados reais extraídos do PDF"""
        filepath = Path(input_path)
        if not filepath.exists():
            print(f"❌ Arquivo não encontrado: {input_path}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ {len(data)} leiloeiros reais carregados")
        return data
    
    def calculate_tech_score(self, leiloeiro: Dict) -> Dict:
        """
        Calcula TechScore baseado em métricas de tecnologia:
        1. Email corporativo: +40 pontos
        2. Site extraído: +30 pontos
        3. Domínio .com.br: +20 pontos
        4. Domínio sem subdomínio: +10 pontos
        Total máximo: 100 pontos
        """
        score = 0
        breakdown = {}
        
        # Verifica se tem site
        has_site = 'site' in leiloeiro and leiloeiro['site'] and leiloeiro['site'] != 'N/A'
        
        # Se não tem site, score = 0
        if not has_site:
            return {
                'score': 0,
                'category': 'Offline (Sem Site)',
                'breakdown': {'sem_site': 0},
                'has_site': False
            }
        
        # 1. Email corporativo
        if leiloeiro.get('email_corporativo', False):
            score += 40
            breakdown['email_corporativo'] = 40
        
        # 2. Site extraído
        score += 30
        breakdown['site_extraido'] = 30
            
        # 3. Domínio .com.br
        if '.com.br' in leiloeiro['site']:
            score += 20
            breakdown['dominio_com_br'] = 20
        
        # 4. Domínio sem subdomínio (apenas www)
        if leiloeiro['site'].startswith('https://www.') and leiloeiro['site'].count('.') == 3:
            score += 10
            breakdown['dominio_simples'] = 10
        
        # Classificação baseada no TechScore
        if score > 75:
            category = "Gigante (Portal)"
        elif score >= 40:
            category = "Médio (Consolidado)"
        else:
            category = "Pequeno (Site Básico)"
        
        return {
            'score': score,
            'category': category,
            'breakdown': breakdown,
            'has_site': True
        }
    
    def analyze_all(self, data: List[Dict]) -> List[Dict]:
        """Analisa todos os leiloeiros"""
        print(f"\n📊 Analisando {len(data)} leiloeiros reais...")
        
        results = []
        for leiloeiro in data:
            ranking = self.calculate_tech_score(leiloeiro)
            
            result = {
                'nome': leiloeiro.get('nome', 'N/A'),
                'email': leiloeiro.get('email', 'N/A'),
                'email_corporativo': leiloeiro.get('email_corporativo', False),
                'site': leiloeiro.get('site', 'N/A'),
                'fonte': leiloeiro.get('fonte', 'desconhecida'),
                'tech_score': ranking['score'],
                'categoria': ranking['category'],
                'has_site': ranking.get('has_site', False),
                'breakdown': ranking['breakdown']
            }
            
            results.append(result)
        
        return results
    
    def save_to_csv(self, results: List[Dict], output_path: str = "data/relatorio_final_ranking.csv"):
        """Salva os resultados em CSV ordenado por tech_score (oportunidades primeiro)"""
        # Ordena por tech_score (ascendente - oportunidades primeiro)
        sorted_results = sorted(results, key=lambda x: x['tech_score'])
        
        # Converte para DataFrame
        df = pd.DataFrame(sorted_results)
        
        # Remove coluna breakdown (não é útil no CSV)
        if 'breakdown' in df.columns:
            df = df.drop(columns=['breakdown'])
        if 'has_site' in df.columns:
            df = df.drop(columns=['has_site'])
        
        # Garante que o diretório existe
        filepath = Path(output_path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Salva em CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 CSV salvo em: {output_path}")
        print(f"📊 Total de leiloeiros: {len(df)}")
        
        # Estatísticas
        categories = df['categoria'].value_counts()
        print("\n📈 Distribuição por categoria:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} leiloeiros")
        
        # Top pequenos (site básico)
        print("\n🔍 TOP 10 PEQUENOS (Site Básico):")
        pequenos = df[df['categoria'] == 'Pequeno (Site Básico)'].head(10)
        for idx, row in pequenos.iterrows():
            print(f"   • {row['nome']} - TechScore: {row['tech_score']}")
        
        # Top gigantes
        print("\n🏆 TOP 10 GIGANTES (Portal):")
        gigantes = df[df['categoria'] == 'Gigante (Portal)'].head(10)
        if len(gigantes) > 0:
            for idx, row in gigantes.iterrows():
                print(f"   • {row['nome']} - TechScore: {row['tech_score']}")
        else:
            print("   Nenhum gigante identificado")
        
        return df
    
    def save_to_json(self, results: List[Dict], output_path: str = "data/processed/ranking_final.json"):
        """Salva os resultados completos em JSON"""
        # Ordena por tech_score (ascendente - oportunidades primeiro)
        sorted_results = sorted(results, key=lambda x: x['tech_score'])
        
        # Garante que o diretório existe
        filepath = Path(output_path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Salva em JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sorted_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 JSON salvo em: {output_path}")
        
        return sorted_results

def main():
    """Função principal"""
    print("=" * 70)
    print("🏆 SISTEMA DE RANQUEAMENTO REAL - LEILOEIROS DE SP")
    print("=" * 70)
    
    try:
        # Inicializa o ranker
        ranker = RealAuctioneerRanker()
        
        # Carrega dados reais
        print("\n📁 Carregando dados extraídos do PDF...")
        data = ranker.load_real_data()
        
        if not data:
            print("❌ Nenhum dado para analisar.")
            return
        
        print(f"📊 Dados carregados: {len(data)} leiloeiros")
        
        # Analisa todos os leiloeiros
        print("\n" + "-" * 70)
        print("🔬 CALCULANDO SCORES DE AUTORIDADE")
        print("-" * 70)
        
        results = ranker.analyze_all(data)
        
        # Salva resultados
        print("\n" + "-" * 70)
        print("💾 GERANDO RELATÓRIOS FINAIS")
        print("-" * 70)
        
        # Salva CSV
        df = ranker.save_to_csv(results)
        
        # Salva JSON
        json_data = ranker.save_to_json(results)
        
        # Resumo final
        print("\n" + "=" * 70)
        print("📋 RESUMO FINAL DO PROJETO")
        print("=" * 70)
        
        total_leiloeiros = len(results)
        
        # Contagem por categoria
        gigantes = len([r for r in results if r['categoria'] == 'Gigante (Portal)'])
        medios = len([r for r in results if r['categoria'] == 'Médio (Consolidado)'])
        pequenos = len([r for r in results if r['categoria'] == 'Pequeno (Site Básico)'])
        offline = len([r for r in results if r['categoria'] == 'Offline (Sem Site)'])
        
        oportunidades_online = medios + pequenos
        
        print(f"📊 TOTAL MAPEADO: {total_leiloeiros}")
        print(f"🏆 GIGANTES (Portal): {gigantes}")
        print(f"⚖️  MÉDIOS (Consolidado): {medios}")
        print(f"🔍 PEQUENOS (Site Básico): {pequenos}")
        print(f"📴 OFFLINE (Sem Site): {offline}")
        print(f"💡 OPORTUNIDADES ONLINE (Médios + Pequenos): {oportunidades_online}")
        
        # Porcentagem de emails corporativos
        corporativos = len([r for r in results if r['email_corporativo']])
        perc_corporativos = (corporativos / total_leiloeiros * 100) if total_leiloeiros > 0 else 0
        print(f"📧 EMAILS CORPORATIVOS: {corporativos} ({perc_corporativos:.1f}%)")
        
        # Porcentagem com site
        com_site = len([r for r in results if r['has_site']])
        perc_site = (com_site / total_leiloeiros * 100) if total_leiloeiros > 0 else 0
        print(f"🌐 COM SITE: {com_site} ({perc_site:.1f}%)")
        print(f"📴 SEM SITE: {offline} ({100 - perc_site:.1f}%)")
        
        print("\n" + "=" * 70)
        print("🚀 PRÓXIMOS PASSOS:")
        print("=" * 70)
        print("1. Dashboard Streamlit já está disponível em src/app.py")
        print("2. Execute: streamlit run src/app.py")
        print("3. O dashboard carregará automaticamente o CSV gerado")
        print("4. Use o filtro 'Filtrar por Tamanho' para analisar categorias")
        print("5. Foco em 'Pequenos (Site Básico)' e 'Offline' para oportunidades")
        print("\n✅ Ranqueamento com nova lógica concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
