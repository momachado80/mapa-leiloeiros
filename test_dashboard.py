#!/usr/bin/env python3
"""
Teste do dashboard - Verifica se os dados estão sendo carregados corretamente
"""

import pandas as pd
import json
from pathlib import Path

print("🧪 TESTE DO DASHBOARD - CARREGAMENTO DE DADOS")
print("=" * 60)

# Verificar arquivos existentes
print("\n📁 Verificando arquivos de dados:")
csv_path = Path("data/relatorio_final.csv")
json_path = Path("data/processed/leiloeiros_rankeados.json")

if csv_path.exists():
    print(f"✅ CSV encontrado: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"   • Registros: {len(df)}")
    print(f"   • Colunas: {list(df.columns)}")
    
    # Estatísticas
    if 'tech_score' in df.columns:
        print(f"   • TechScore médio: {df['tech_score'].mean():.1f}")
        print(f"   • TechScore min/max: {df['tech_score'].min()}/{df['tech_score'].max()}")
    
    if 'categoria' in df.columns:
        print(f"   • Distribuição por categoria:")
        for cat, count in df['categoria'].value_counts().items():
            print(f"     - {cat}: {count}")
    
    if 'email_corporativo' in df.columns:
        corporativos = df['email_corporativo'].sum()
        print(f"   • Emails corporativos: {int(corporativos)}/{len(df)} ({corporativos/len(df)*100:.1f}%)")
    
    if 'site' in df.columns:
        com_site = df[df['site'].notna() & (df['site'] != '')].shape[0]
        print(f"   • Com site: {com_site}/{len(df)} ({com_site/len(df)*100:.1f}%)")
else:
    print(f"❌ CSV não encontrado: {csv_path}")

if json_path.exists():
    print(f"\n✅ JSON encontrado: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"   • Registros: {len(data)}")
else:
    print(f"\n❌ JSON não encontrado: {json_path}")

# Verificar estrutura do dashboard
print("\n🔍 Verificando estrutura do dashboard:")
app_path = Path("src/app.py")
if app_path.exists():
    print(f"✅ Dashboard encontrado: {app_path}")
    
    # Testar importação
    try:
        import sys
        sys.path.insert(0, 'src')
        from app import load_data, create_sample_data
        
        print("✅ Funções do dashboard importadas com sucesso")
        
        # Testar carregamento de dados
        print("\n🧪 Testando carregamento de dados:")
        df_dashboard = load_data()
        print(f"   • Dados carregados: {len(df_dashboard)} registros")
        print(f"   • Colunas: {list(df_dashboard.columns)}")
        
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
else:
    print(f"❌ Dashboard não encontrado: {app_path}")

print("\n" + "=" * 60)
print("✅ TESTE CONCLUÍDO")
print("=" * 60)

# Sugestões
print("\n💡 SUGESTÕES:")
print("1. Para executar o dashboard: streamlit run src/app.py")
print("2. Para processar mais dados: python process_lista_final.py")
print("3. Para verificar dados brutos: ls -la data/raw/")
print("4. Para verificar dados processados: ls -la data/processed/")
