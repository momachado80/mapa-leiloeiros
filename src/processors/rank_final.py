"""
Classificador Inclusivo Final - Processa dados brutos com nova lógica
Não descarta leiloeiros, categoriza todos com 4 categorias explícitas.
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
import re

class InclusiveRanker:
    """Classifica todos os leiloeiros sem descartar ninguém"""
    
    def __init__(self, input_path: str = "data/processed/leiloeiros_enriquecidos_final_v2.json"):
        self.input_path = Path(input_path)
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """Carrega dados enriquecidos"""
        print(f"📁 Carregando dados de: {self.input_path}")
        
        if not self.input_path.exists():
            print(f"❌ Arquivo não encontrado: {self.input_path}")
            
            # Tenta carregar dados OCR como fallback
            fallback_path = Path("data/processed/leiloeiros_ocr.json")
            if fallback_path.exists():
                print(f"⚠️  Usando dados OCR como fallback")
                self.input_path = fallback_path
            else:
                return pd.DataFrame()
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.df = pd.DataFrame(data)
        print(f"✅ Dados carregados: {len(self.df)} leiloeiros ({self.input_path.name})")
        return self.df
    
    def is_corporate_email(self, email: str) -> bool:
        """Verifica se o email é corporativo"""
        if not email or pd.isna(email):
            return False
        
        generic_domains = {
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
            'globo.com', 'live.com', 'msn.com', 'aol.com',
            'gmail.com.br', 'hotmail.com.br', 'yahoo.com.br'
        }
        
        domain = email.split('@')[-1].lower()
        return not any(domain.endswith(generic) for generic in generic_domains)
    
    def extract_site_from_email(self, email: str, existing_site: str = None) -> str:
        """
        Extrai site do email corporativo.
        Para emails genéricos, retorna "Não Identificado".
        Se já existe site no dado enriquecido, usa ele.
        """
        # Se já tem site no dado enriquecido, usa ele
        if existing_site and not pd.isna(existing_site) and existing_site:
            return existing_site
        
        if not email or pd.isna(email) or email == "":
            return "Não Identificado"
        
        if not self.is_corporate_email(email):
            return "Não Identificado"
        
        domain = email.split('@')[-1]
        domain_parts = domain.split('.')
        
        if len(domain_parts) >= 2:
            if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
                main_domain = '.'.join(domain_parts[-3:])
            else:
                main_domain = '.'.join(domain_parts[-2:])
            
            return f"https://www.{main_domain}"
        
        return "Não Identificado"
    
    def calculate_tech_score(self, email: str, site: str) -> int:
        """
        Calcula TechScore (0-100):
        - Email corporativo: +40
        - Site extraído: +30
        - Domínio .com.br: +20
        - Domínio simples: +10
        - Email genérico: +5 (mínimo)
        - Sem email: 0
        """
        score = 0
        
        if not email or pd.isna(email):
            return 0
        
        # Email genérico: +5 (mínimo)
        if not self.is_corporate_email(email):
            score = 5
        else:
            # Email corporativo: +40
            score += 40
            
            # Site extraído
            if site and site != "Não Identificado" and site != "":
                score += 30
                
                # Domínio .com.br
                if '.com.br' in site:
                    score += 20
                else:
                    score += 10
        
        return min(score, 100)
    
    def determine_category(self, site: str, tech_score: int) -> str:
        """
        Determina categoria baseada na nova lógica:
        1. Gigante (Portal): Site identificado + TechScore > 80
        2. Médio (Consolidado): Site identificado + TechScore 40-80
        3. Pequeno (Com Site): Site identificado + TechScore < 40
        4. Offline/Sem Site: Site "Não Identificado"
        """
        if site == "Não Identificado" or not site or site == "":
            return "Offline/Sem Site"
        
        if tech_score > 80:
            return "Gigante (Portal)"
        elif tech_score >= 40:
            return "Médio (Consolidado)"
        else:
            return "Pequeno (Com Site)"
    
    def clean_nome(self, nome: str) -> str:
        """Limpa o nome do leiloeiro"""
        if not nome or pd.isna(nome):
            return "Nome Não Identificado"
        
        # Remove "Licensed to..." e outros prefixos
        if isinstance(nome, str) and nome.startswith("Licensed to"):
            return "Leiloeiro Extraído"
        
        # Remove números e caracteres especiais no final
        nome = re.sub(r'[\d\s\-\./]+$', '', str(nome))
        
        # Remove caracteres especiais no início
        nome = re.sub(r'^[_\W]+', '', nome)
        
        # Remove espaços extras
        nome = nome.strip()
        
        # Capitaliza se tudo for minúsculo
        if nome and nome.islower():
            words = nome.split()
            capitalized_words = [word.capitalize() for word in words]
            nome = ' '.join(capitalized_words)
        
        return nome if nome else "Nome Não Identificado"
    
    def process_all(self) -> pd.DataFrame:
        """Processa todos os leiloeiros"""
        print("\n🔬 PROCESSANDO TODOS OS LEILOEIROS")
        print("-" * 50)
        
        if self.df is None or self.df.empty:
            print("❌ Nenhum dado para processar")
            return pd.DataFrame()
        
        processed_rows = []
        
        for idx, row in self.df.iterrows():
            # Limpa o nome
            nome_limpo = self.clean_nome(row.get('nome', ''))
            
            # Obtém email (do dado enriquecido)
            email = row.get('email', '')
            
            # Obtém site existente (do dado enriquecido)
            existing_site = row.get('site', None)
            
            # Extrai site (usa existente ou extrai do email)
            site = self.extract_site_from_email(email, existing_site)
            
            # Calcula TechScore
            tech_score = self.calculate_tech_score(email, site)
            
            # Determina categoria
            categoria = self.determine_category(site, tech_score)
            
            # Verifica se é email corporativo
            email_corporativo = self.is_corporate_email(email) if email else False
            
            # Cria registro processado
            processed_row = {
                'nome': nome_limpo,
                'email': email if email else "",
                'email_corporativo': email_corporativo,
                'site': site,
                'tech_score': tech_score,
                'categoria': categoria,
                'fonte': row.get('fonte_clean', row.get('fonte', 'pdf_enriquecido')),
                'pagina': row.get('pagina', 0),
                'enriquecido': row.get('enriquecido', False)
            }
            
            processed_rows.append(processed_row)
        
        # Cria DataFrame processado
        processed_df = pd.DataFrame(processed_rows)
        
        # Remove duplicados baseado no email (mantém o primeiro)
        if 'email' in processed_df.columns:
            processed_df = processed_df.drop_duplicates(subset=['email'], keep='first')
        
        print(f"✅ Processados: {len(processed_df)} leiloeiros únicos")
        return processed_df
    
    def generate_detailed_report(self, df: pd.DataFrame):
        """Gera relatório detalhado"""
        print("\n📊 RELATÓRIO DETALHADO")
        print("-" * 50)
        
        if df.empty:
            print("❌ Nenhum dado para relatório")
            return
        
        total = len(df)
        
        # Estatísticas por categoria
        print("\n📈 DISTRIBUIÇÃO POR CATEGORIA (NOVA LÓGICA):")
        categoria_counts = df['categoria'].value_counts()
        for categoria, count in categoria_counts.items():
            percentage = (count / total) * 100
            print(f"   • {categoria}: {count} leiloeiros ({percentage:.1f}%)")
        
        # Estatísticas gerais
        com_site = df[df['site'] != "Não Identificado"].shape[0]
        emails_corp = df['email_corporativo'].sum()
        avg_score = df['tech_score'].mean()
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Total de leiloeiros: {total}")
        print(f"   • Com site identificado: {com_site}")
        print(f"   • Emails corporativos: {int(emails_corp)}")
        print(f"   • TechScore médio: {avg_score:.1f}")
        
        # Top 10 por TechScore
        print(f"\n🏆 TOP 10 POR TECHSCORE:")
        top_10 = df.nlargest(10, 'tech_score')[['nome', 'tech_score', 'categoria', 'site']]
        for idx, row in top_10.iterrows():
            site_display = row['site'][:30] + "..." if len(row['site']) > 30 else row['site']
            print(f"   • {row['nome'][:25]}... - Score: {row['tech_score']} - {row['categoria']}")
            if row['site'] != "Não Identificado":
                print(f"      🌐 {site_display}")
        
        # Oportunidades (Pequenos + Offline)
        oportunidades = df[df['categoria'].isin(['Pequeno (Com Site)', 'Offline/Sem Site'])]
        print(f"\n💡 OPORTUNIDADES DE NEGÓCIO:")
        print(f"   • Total oportunidades: {len(oportunidades)}")
        print(f"   • Pequenos (Com Site): {len(df[df['categoria'] == 'Pequeno (Com Site)'])}")
        print(f"   • Offline/Sem Site: {len(df[df['categoria'] == 'Offline/Sem Site'])}")
        
        # Exemplos de cada categoria
        print(f"\n🔍 EXEMPLOS DE CADA CATEGORIA:")
        for categoria in df['categoria'].unique():
            exemplos = df[df['categoria'] == categoria].head(2)
            print(f"\n   {categoria}:")
            for idx, row in exemplos.iterrows():
                print(f"      • {row['nome'][:30]}... (Score: {row['tech_score']})")
                if row['email']:
                    print(f"        📧 {row['email']}")
    
    def save_results(self, df: pd.DataFrame):
        """Salva resultados em CSV e JSON"""
        print("\n💾 SALVANDO RESULTADOS")
        print("-" * 50)
        
        # Cria diretório se não existir
        output_dir = Path("data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Salva CSV
        csv_path = output_dir / "relatorio_final_inclusivo.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV salvo em: {csv_path}")
        
        # Salva JSON
        json_path = output_dir / "processed" / "ranking_final_inclusivo.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        json_data = df.to_dict('records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON salvo em: {json_path}")
        
        return csv_path, json_path
    
    def run_full_ranking(self):
        """Executa o pipeline completo"""
        print("=" * 70)
        print("🏆 CLASSIFICADOR INCLUSIVO FINAL - TODOS OS LEILOEIROS")
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
        
        # 3. Gera relatório
        self.generate_detailed_report(processed_df)
        
        # 4. Salva resultados
        csv_path, json_path = self.save_results(processed_df)
        
        print("\n" + "=" * 70)
        print("✅ CLASSIFICAÇÃO INCLUSIVA CONCLUÍDA!")
        print("=" * 70)
        
        print(f"\n📁 Arquivos gerados:")
        print(f"   • {csv_path}")
        print(f"   • {json_path}")
        
        print(f"\n🎯 Dados prontos para o dashboard!")
        print(f"   Total processado: {len(processed_df)} leiloeiros")
        
        return processed_df

def main():
    """Função principal"""
    ranker = InclusiveRanker()
    result_df = ranker.run_full_ranking()
    
    if result_df is not None:
        print(f"\n🚀 Execute o dashboard atualizado:")
        print(f"   streamlit run src/app.py")
    else:
        print("\n❌ Falha na classificação")

if __name__ == "__main__":
    main()
