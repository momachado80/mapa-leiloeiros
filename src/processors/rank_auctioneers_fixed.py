"""
Sistema de Ranqueamento Fixo - Leiloeiros de SP
Nova lógica com 4 categorias explícitas e TechScore correto.
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import re

class AuctioneerRankerFixed:
    """Classifica leiloeiros com nova lógica de 4 categorias"""
    
    def __init__(self, input_path: str = "data/processed/leiloeiros_ocr.json"):
        self.input_path = Path(input_path)
        self.df = None
        self.ranked_data = []
        
    def load_data(self) -> pd.DataFrame:
        """Carrega dados dos leiloeiros"""
        print(f"📁 Carregando dados de: {self.input_path}")
        
        if not self.input_path.exists():
            print(f"❌ Arquivo não encontrado: {self.input_path}")
            return pd.DataFrame()
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.df = pd.DataFrame(data)
        print(f"✅ Dados carregados: {len(self.df)} leiloeiros")
        return self.df
    
    def calculate_tech_score(self, row: pd.Series) -> int:
        """
        Calcula TechScore (0-100) baseado em:
        - Email corporativo: +40 pontos
        - Site extraído: +30 pontos
        - Domínio .com.br: +20 pontos
        - Domínio simples: +10 pontos
        - Sites com erro/lento: +5 pontos (mínimo)
        """
        score = 0
        
        # 1. Email corporativo
        if row.get('email_corporativo', False):
            score += 40
        
        # 2. Site extraído
        site = row.get('site', '')
        if site and site != '' and site != 'N/A':
            score += 30
            
            # 3. Domínio .com.br
            if '.com.br' in site:
                score += 20
            else:
                score += 10  # Domínio simples
        
        # 4. Se tem email mas não tem site (genérico)
        elif row.get('email', '') and not site:
            score = 5  # Mínimo para quem tem email genérico
        
        # Garante que o score está entre 0-100
        return min(score, 100)
    
    def determine_category(self, row: pd.Series, tech_score: int) -> str:
        """
        Determina categoria baseado no TechScore e presença de site.
        4 categorias explícitas:
        1. Gigante (Portal): TechScore > 75
        2. Médio (Consolidado): TechScore 40-75
        3. Pequeno (Com Site): TechScore < 40, mas site != null/vazio
        4. Offline (Sem Site): site == null/vazio
        """
        site = row.get('site', '')
        has_site = site and site != '' and site != 'N/A'
        
        if not has_site:
            return "Offline (Sem Site)"
        
        if tech_score > 75:
            return "Gigante (Portal)"
        elif tech_score >= 40:
            return "Médio (Consolidado)"
        else:
            return "Pequeno (Site Básico)"
    
    def clean_nome(self, nome: str) -> str:
        """Limpa o nome do leiloeiro"""
        if not nome:
            return "N/A"
        
        # Remove "Licensed to..." e outros prefixos
        if nome.startswith("Licensed to"):
            # Tenta extrair nome real da linha OCR
            return "Leiloeiro Extraído"
        
        # Remove números e caracteres especiais no final
        nome = re.sub(r'[\d\s\-\./]+$', '', nome)
        
        # Remove caracteres especiais no início
        nome = re.sub(r'^[_\W]+', '', nome)
        
        # Capitaliza palavras
        words = nome.split()
        cleaned_words = []
        for word in words:
            if word and len(word) > 1:
                # Mantém a capitalização original, mas capitaliza se tudo for minúsculo
                if word.islower():
                    cleaned_words.append(word.capitalize())
                else:
                    cleaned_words.append(word)
        
        return ' '.join(cleaned_words) if cleaned_words else nome.strip()
    
    def process_all(self) -> pd.DataFrame:
        """Processa todos os leiloeiros"""
        print("\n🔬 CALCULANDO SCORES E CATEGORIAS")
        print("-" * 50)
        
        if self.df is None or self.df.empty:
            print("❌ Nenhum dado para processar")
            return pd.DataFrame()
        
        processed_rows = []
        
        for idx, row in self.df.iterrows():
            # Limpa o nome
            nome_limpo = self.clean_nome(row.get('nome', ''))
            
            # Calcula TechScore
            tech_score = self.calculate_tech_score(row)
            
            # Determina categoria
            categoria = self.determine_category(row, tech_score)
            
            # Cria registro processado
            processed_row = {
                'nome': nome_limpo,
                'email': row.get('email', ''),
                'email_corporativo': row.get('email_corporativo', False),
                'site': row.get('site', ''),
                'tech_score': tech_score,
                'categoria': categoria,
                'fonte': row.get('fonte', 'pdf_ocr')
            }
            
            processed_rows.append(processed_row)
        
        # Cria DataFrame processado
        processed_df = pd.DataFrame(processed_rows)
        
        # Remove duplicados (mantém o primeiro)
        processed_df = processed_df.drop_duplicates(subset=['email'], keep='first')
        
        print(f"✅ Processados: {len(processed_df)} leiloeiros únicos")
        return processed_df
    
    def generate_reports(self, df: pd.DataFrame):
        """Gera relatórios e estatísticas"""
        print("\n📊 GERANDO RELATÓRIOS")
        print("-" * 50)
        
        if df.empty:
            print("❌ Nenhum dado para relatório")
            return
        
        # Estatísticas por categoria
        categoria_counts = df['categoria'].value_counts()
        
        print("\n📈 DISTRIBUIÇÃO POR CATEGORIA:")
        for categoria, count in categoria_counts.items():
            print(f"   • {categoria}: {count} leiloeiros")
        
        # Estatísticas gerais
        total = len(df)
        com_site = df[df['site'] != ''].shape[0]
        emails_corp = df['email_corporativo'].sum()
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Total de leiloeiros: {total}")
        print(f"   • Com site: {com_site}")
        print(f"   • Emails corporativos: {int(emails_corp)}")
        print(f"   • Sem site: {total - com_site}")
        
        # Top 10 por TechScore
        print(f"\n🏆 TOP 10 POR TECHSCORE:")
        top_10 = df.nlargest(10, 'tech_score')[['nome', 'tech_score', 'categoria']]
        for idx, row in top_10.iterrows():
            print(f"   • {row['nome'][:30]}... - Score: {row['tech_score']} - {row['categoria']}")
        
        # Oportunidades (Pequenos + Offline)
        oportunidades = df[df['categoria'].isin(['Pequeno (Site Básico)', 'Offline (Sem Site)'])]
        print(f"\n💡 OPORTUNIDADES DE NEGÓCIO:")
        print(f"   • Total oportunidades: {len(oportunidades)}")
        print(f"   • Pequenos (Site Básico): {len(df[df['categoria'] == 'Pequeno (Site Básico)'])}")
        print(f"   • Offline (Sem Site): {len(df[df['categoria'] == 'Offline (Sem Site)'])}")
    
    def save_results(self, df: pd.DataFrame):
        """Salva resultados em CSV e JSON"""
        print("\n💾 SALVANDO RESULTADOS")
        print("-" * 50)
        
        # Cria diretório se não existir
        output_dir = Path("data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Salva CSV
        csv_path = output_dir / "relatorio_final_fixed.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV salvo em: {csv_path}")
        
        # Salva JSON
        json_path = output_dir / "processed" / "ranking_final_fixed.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Converte para lista de dicionários
        json_data = df.to_dict('records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON salvo em: {json_path}")
        
        return csv_path, json_path
    
    def run_full_ranking(self):
        """Executa o pipeline completo de ranqueamento"""
        print("=" * 70)
        print("🏆 SISTEMA DE RANQUEAMENTO FIXO - LEILOEIROS DE SP")
        print("=" * 70)
        
        # 1. Carrega dados
        self.load_data()
        if self.df is None or self.df.empty:
            print("❌ Falha ao carregar dados")
            return
        
        # 2. Processa todos os leiloeiros
        processed_df = self.process_all()
        if processed_df.empty:
            print("❌ Falha no processamento")
            return
        
        # 3. Gera relatórios
        self.generate_reports(processed_df)
        
        # 4. Salva resultados
        csv_path, json_path = self.save_results(processed_df)
        
        print("\n" + "=" * 70)
        print("✅ RANQUEAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        
        print(f"\n📁 Arquivos gerados:")
        print(f"   • {csv_path}")
        print(f"   • {json_path}")
        
        print(f"\n🚀 Próximo passo: Atualize o dashboard com:")
        print(f"   streamlit run src/app.py")
        
        return processed_df

def main():
    """Função principal"""
    ranker = AuctioneerRankerFixed()
    result_df = ranker.run_full_ranking()
    
    if result_df is not None:
        print(f"\n🎯 Sistema pronto para uso!")
    else:
        print("\n❌ Falha no ranqueamento")

if __name__ == "__main__":
    main()
