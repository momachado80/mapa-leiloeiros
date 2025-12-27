#!/usr/bin/env python3
"""
Verificação rápida do CSV gerado
"""

import pandas as pd
from pathlib import Path

print("🔍 VERIFICAÇÃO DO CSV GERADO")
print("=" * 60)

csv_path = Path("data/relatorio_final_ranking.csv")
if not csv_path.exists():
    print("❌ Arquivo não encontrado: data/relatorio_final_ranking.csv")
    exit(1)

try:
    df = pd.read_csv(csv_path)
    print(f"✅ CSV carregado: {len(df)} registros")
    print(f"📊 Colunas: {list(df.columns)}")
    
    print("\n📈 Estatísticas:")
    print(f"Total de leiloeiros: {len(df)}")
    
    if 'Categoria' in df.columns:
        print("\nDistribuição por Categoria:")
        for cat, count in df['Categoria'].value_counts().items():
            print(f"  {cat}: {count} ({count/len(df)*100:.1f}%)")
    
    if 'Score' in df.columns:
        print(f"\nScore:")
        print(f"  Média: {df['Score'].mean():.1f}")
        print(f"  Mínimo: {df['Score'].min()}")
        print(f"  Máximo: {df['Score'].max()}")
    
    print("\n📋 Primeiras 3 linhas:")
    print(df.head(3).to_string())
    
except Exception as e:
    print(f"❌ Erro: {e}")
