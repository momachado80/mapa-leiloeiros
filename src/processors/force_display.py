#!/usr/bin/env python3
"""
Processamento forçado para exibição de TODOS os leiloeiros no Dashboard
Lógica simplificada: Offline/Sem Site vs Online
"""

import json
import pandas as pd
from pathlib import Path
import sys

def processar_leiloeiro(leiloeiro):
    """Processa um leiloeiro individual com lógica simplificada"""
    # Copia os dados originais
    resultado = leiloeiro.copy()
    
    # Extrai site
    site = leiloeiro.get('site')
    
    # Domínios genéricos a serem considerados como "não sites"
    dominios_genericos = ['gmail', 'hotmail', 'outlook', 'yahoo', 'uol', 'bol', 'terra', 'ig']
    
    # Verifica se tem site válido
    tem_site_valido = False
    
    if site and site != 'null' and site is not None and str(site).strip() != '':
        site_str = str(site).lower()
        
        # Verifica se não é domínio genérico
        if not any(dominio in site_str for dominio in dominios_genericos):
            tem_site_valido = True
    
    # Aplica lógica de categorização
    if tem_site_valido:
        resultado['Categoria'] = 'Online'
        resultado['Score'] = 60  # Score base para exibição
        # Garante que o site tenha https:// se não tiver
        if not site.startswith(('http://', 'https://')):
            resultado['site'] = f'https://{site}'
    else:
        resultado['Categoria'] = 'Offline / Sem Site'
        resultado['Score'] = 0
        resultado['site'] = None  # Site vazio para não quebrar o link
    
    # Garante que as colunas necessárias existam
    if 'email' not in resultado:
        resultado['email'] = None
    if 'telefone' not in resultado:
        resultado['telefone'] = None
    if 'matricula' not in resultado:
        resultado['matricula'] = None
    if 'cidade' not in resultado:
        resultado['cidade'] = None
    
    return resultado

def main():
    print("=" * 60)
    print("🔧 PROCESSAMENTO FORÇADO - TODOS OS LEILOEIROS")
    print("=" * 60)
    
    # Carregar dados
    input_path = Path("data/full_list.json")
    if not input_path.exists():
        print(f"❌ Arquivo de entrada não encontrado: {input_path}")
        print("💡 Verifique se o arquivo data/full_list.json existe")
        sys.exit(1)
    
    print(f"📁 Carregando dados de: {input_path}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            leiloeiros = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {e}")
        sys.exit(1)
    
    print(f"✅ Dados carregados: {len(leiloeiros)} leiloeiros")
    
    # Processar cada leiloeiro
    print("\n⚙️ Processando cada leiloeiro...")
    leiloeiros_processados = []
    
    for i, leiloeiro in enumerate(leiloeiros):
        if i % 100 == 0:
            print(f"   Processados: {i}/{len(leiloeiros)}")
        
        leiloeiro_processado = processar_leiloeiro(leiloeiro)
        leiloeiros_processados.append(leiloeiro_processado)
    
    print(f"✅ Processamento concluído: {len(leiloeiros_processados)} leiloeiros")
    
    # Gerar relatório
    total = len(leiloeiros_processados)
    online = sum(1 for l in leiloeiros_processados if l['Categoria'] == 'Online')
    offline = total - online
    
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL (FORÇADO)")
    print("=" * 60)
    print(f"Total de leiloeiros: {total}")
    print(f"Online (com site válido): {online} ({online/total*100:.1f}%)")
    print(f"Offline / Sem Site: {offline} ({offline/total*100:.1f}%)")
    
    # Salvar resultados
    output_csv = Path("data/relatorio_final_ranking.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    # Converter para DataFrame
    df = pd.DataFrame(leiloeiros_processados)
    
    # Reordenar colunas para melhor visualização
    column_order = ['nome', 'matricula', 'cidade', 'site', 'email', 'telefone', 'Score', 'Categoria']
    
    # Manter apenas colunas existentes
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    # Salvar CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n💾 CSV salvo: {output_csv}")
    
    # Salvar também como relatorio_final.csv (para compatibilidade com dashboard)
    compat_csv = Path("data/relatorio_final.csv")
    df.to_csv(compat_csv, index=False, encoding='utf-8')
    print(f"💾 CSV de compatibilidade: {compat_csv}")
    
    print("\n" + "=" * 60)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("=" * 60)
    
    # Feedback final conforme solicitado
    print(f"\nSUCESSO: Total de Leiloeiros Processados: {total}")
    
    # Mostrar exemplos
    print("\n📋 EXEMPLOS DE CLASSIFICAÇÃO (primeiros 5):")
    for i, leiloeiro in enumerate(leiloeiros_processados[:5]):
        print(f"\n{i+1}. {leiloeiro['nome']}")
        print(f"   Site: {leiloeiro.get('site', 'Nenhum')}")
        print(f"   Score: {leiloeiro['Score']}")
        print(f"   Categoria: {leiloeiro['Categoria']}")

if __name__ == "__main__":
    main()
