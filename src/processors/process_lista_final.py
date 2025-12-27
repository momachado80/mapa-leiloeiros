"""
Processa a lista final de leiloeiros fornecida pelo usuário
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
import re

class ListaFinalProcessor:
    """Processa a lista final de leiloeiros com dados completos"""
    
    def __init__(self):
        self.data = []
        
    def load_data_from_text(self, text_data: str):
        """Carrega dados do texto fornecido pelo usuário"""
        print("📁 Carregando lista final de leiloeiros...")
        
        try:
            # O texto parece ser uma lista JSON
            self.data = json.loads(text_data)
            print(f"✅ Dados carregados: {len(self.data)} leiloeiros")
        except json.JSONDecodeError:
            print("❌ Erro ao decodificar JSON. Tentando processar manualmente...")
            # Tenta processar como lista de dicionários Python
            lines = text_data.strip().split('\n')
            records = []
            current_record = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('{'):
                    if current_record:
                        records.append(current_record)
                    current_record = {}
                elif ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().strip('"')
                    value = value.strip().strip(',"')
                    current_record[key] = value
            
            if current_record:
                records.append(current_record)
            
            self.data = records
            print(f"✅ Dados processados manualmente: {len(self.data)} leiloeiros")
        
        return self.data
    
    def is_corporate_email(self, email: str) -> bool:
        """Verifica se o email é corporativo"""
        if not email or pd.isna(email) or email == "null":
            return False
        
        generic_domains = {
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
            'globo.com', 'live.com', 'msn.com', 'aol.com',
            'gmail.com.br', 'hotmail.com.br', 'yahoo.com.br'
        }
        
        try:
            domain = email.split('@')[-1].lower()
            return not any(domain.endswith(generic) for generic in generic_domains)
        except:
            return False
    
    def extract_site_from_data(self, record: Dict) -> str:
        """Extrai site dos dados do registro"""
        # Primeiro, verifica se já tem site no registro
        site = record.get('site')
        if site and site != "null" and site and not pd.isna(site):
            # Adiciona http:// se não tiver
            if not site.startswith('http'):
                return f"https://{site}"
            return site
        
        # Se não tem site, tenta extrair do email
        email = record.get('email')
        if email and email != "null" and email and not pd.isna(email):
            if self.is_corporate_email(email):
                domain = email.split('@')[-1]
                domain_parts = domain.split('.')
                
                if len(domain_parts) >= 2:
                    if domain_parts[-1] == 'br' and len(domain_parts) >= 3:
                        main_domain = '.'.join(domain_parts[-3:])
                    else:
                        main_domain = '.'.join(domain_parts[-2:])
                    
                    return f"https://www.{main_domain}"
        
        return "Não Identificado"
    
    def calculate_tech_score(self, record: Dict) -> int:
        """
        Calcula TechScore (0-100):
        - Email corporativo: +40
        - Site identificado: +30
        - Domínio .com.br: +20
        - Domínio simples: +10
        - Email genérico: +5 (mínimo)
        - Sem email: 0
        """
        score = 0
        
        email = record.get('email')
        site = self.extract_site_from_data(record)
        
        if not email or email == "null" or pd.isna(email):
            return 0
        
        # Email genérico: +5 (mínimo)
        if not self.is_corporate_email(email):
            score = 5
        else:
            # Email corporativo: +40
            score += 40
            
            # Site identificado
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
        if not nome or pd.isna(nome) or nome == "null":
            return "Nome Não Identificado"
        
        nome_str = str(nome)
        
        # Remove números e caracteres especiais no final
        nome_str = re.sub(r'[\d\s\-\./]+$', '', nome_str)
        
        # Remove caracteres especiais no início
        nome_str = re.sub(r'^[_\W]+', '', nome_str)
        
        # Remove espaços extras
        nome_str = nome_str.strip()
        
        # Capitaliza se tudo for minúsculo
        if nome_str and nome_str.islower():
            words = nome_str.split()
            capitalized_words = [word.capitalize() for word in words]
            nome_str = ' '.join(capitalized_words)
        
        return nome_str if nome_str else "Nome Não Identificado"
    
    def process_all(self) -> pd.DataFrame:
        """Processa todos os leiloeiros da lista"""
        print("\n🔬 PROCESSANDO LISTA FINAL DE LEILOEIROS")
        print("-" * 50)
        
        if not self.data:
            print("❌ Nenhum dado para processar")
            return pd.DataFrame()
        
        processed_rows = []
        
        for record in self.data:
            # Limpa o nome
            nome_limpo = self.clean_nome(record.get('nome', ''))
            
            # Obtém email
            email = record.get('email', '')
            if email == "null":
                email = ""
            
            # Extrai site
            site = self.extract_site_from_data(record)
            
            # Calcula TechScore
            tech_score = self.calculate_tech_score(record)
            
            # Determina categoria
            categoria = self.determine_category(site, tech_score)
            
            # Verifica se é email corporativo
            email_corporativo = self.is_corporate_email(email) if email else False
            
            # Cria registro processado
            processed_row = {
                'nome': nome_limpo,
                'matricula': record.get('matricula', ''),
                'cidade': record.get('cidade', ''),
                'email': email if email else "",
                'email_corporativo': email_corporativo,
                'site': site,
                'telefone': record.get('telefone', ''),
                'tech_score': tech_score,
                'categoria': categoria,
                'fonte': 'lista_final_usuario'
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
        print("\n📈 DISTRIBUIÇÃO POR CATEGORIA:")
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
        print(f"   • Com site identificado: {com_site} ({com_site/total*100:.1f}%)")
        print(f"   • Emails corporativos: {int(emails_corp)} ({emails_corp/total*100:.1f}%)")
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
        print(f"   • Total oportunidades: {len(oportunidades)} ({len(oportunidades)/total*100:.1f}%)")
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
        csv_path = output_dir / "lista_final_processada.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV salvo em: {csv_path}")
        
        # Salva JSON
        json_path = output_dir / "processed" / "lista_final_processada.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        json_data = df.to_dict('records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON salvo em: {json_path}")
        
        return csv_path, json_path
    
    def run_processing(self, text_data: str):
        """Executa o pipeline completo"""
        print("=" * 70)
        print("🏆 PROCESSAMENTO DA LISTA FINAL DE LEILOEIROS")
        print("=" * 70)
        
        # 1. Carrega dados
        self.load_data_from_text(text_data)
        if not self.data:
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
        print("✅ PROCESSAMENTO CONCLUÍDO!")
        print("=" * 70)
        
        print(f"\n📁 Arquivos gerados:")
        print(f"   • {csv_path}")
        print(f"   • {json_path}")
        
        print(f"\n🎯 Dados prontos para o dashboard!")
        print(f"   Total processado: {len(processed_df)} leiloeiros")
        
        return processed_df

def main():
    """Função principal"""
    # Carrega os dados fornecidos pelo usuário
    with open('lista_final_usuario.txt', 'r', encoding='utf-8') as f:
        text_data = f.read()
    
    processor = ListaFinalProcessor()
    result_df = processor.run_processing(text_data)
    
    if result_df is not None:
        print(f"\n🚀 Execute o dashboard atualizado:")
        print(f"   streamlit run src/app.py")
    else:
        print("\n❌ Falha no processamento")

if __name__ == "__main__":
    main()
