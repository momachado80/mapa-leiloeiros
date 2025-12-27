#!/usr/bin/env python3
"""
Script de Limpeza e Classificação de Leiloeiros

Tarefa:
1. Higienização de Sites: Sites com domínios de email (outlook, gmail, etc.) -> null
2. Reclassificação baseada em TechScore e site válido
3. Salvar resultados em CSV e JSON
"""

import json
import pandas as pd
import re
from pathlib import Path

def load_data(input_file):
    """Carrega dados do arquivo JSON"""
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_sites(leiloeiros):
    """Higieniza sites: remove sites com domínios de email"""
    email_domains = ['outlook', 'gmail', 'hotmail', 'yahoo', 'uol', 'bol', 'terra', 'ig']
    
    for leiloeiro in leiloeiros:
        site = leiloeiro.get('site', '')
        
        # Se site for None, vazio ou "Não Identificado", manter como null
        if not site or site == 'Não Identificado':
            leiloeiro['site'] = None
            continue
            
        # Verificar se contém domínio de email
        site_lower = site.lower()
        if any(domain in site_lower for domain in email_domains):
            leiloeiro['site'] = None
        else:
            # Manter o site como está
            leiloeiro['site'] = site
    
    return leiloeiros

def reclassify(leiloeiros):
    """Reclassifica leiloeiros baseado em site válido e TechScore"""
    for leiloeiro in leiloeiros:
        site = leiloeiro.get('site')
        tech_score = leiloeiro.get('tech_score', 0)
        
        # Se não tem site válido -> Offline
        if not site:
            leiloeiro['categoria'] = 'Offline (Sem Site)'
            continue
            
        # Tem site válido, classificar por TechScore
        if tech_score > 80:
            leiloeiro['categoria'] = 'Gigante (Portal)'
        elif tech_score >= 40:
            leiloeiro['categoria'] = 'Médio (Consolidado)'
        else:
            leiloeiro['categoria'] = 'Pequeno (Com Site)'
    
    return leiloeiros

def generate_report(leiloeiros):
    """Gera relatório estatístico"""
    total = len(leiloeiros)
    
    # Contagem por categoria
    categorias = {}
    for leiloeiro in leiloeiros:
        cat = leiloeiro['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    # Contagem com site
    com_site = sum(1 for l in leiloeiros if l.get('site'))
    offline = total - com_site
    
    print("=" * 60)
    print("📊 RELATÓRIO DE CLASSIFICAÇÃO")
    print("=" * 60)
    print(f"Total de leiloeiros: {total}")
    print(f"Com site válido: {com_site} ({com_site/total*100:.1f}%)")
    print(f"Offline/Sem site: {offline} ({offline/total*100:.1f}%)")
    print("\n📈 Distribuição por categoria:")
    for cat, count in categorias.items():
        print(f"  • {cat}: {count} ({count/total*100:.1f}%)")
    print("=" * 60)
    
    return {
        'total': total,
        'com_site': com_site,
        'offline': offline,
        'categorias': categorias
    }

def save_results(leiloeiros, csv_path, json_path):
    """Salva resultados em CSV e JSON"""
    # Salvar JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(leiloeiros, f, ensure_ascii=False, indent=2)
    
    # Salvar CSV
    df = pd.DataFrame(leiloeiros)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"✅ JSON salvo em: {json_path}")
    print(f"✅ CSV salvo em: {csv_path}")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 SCRIPT DE LIMPEZA E CLASSIFICAÇÃO DE LEILOEIROS")
    print("=" * 60)
    
    # Definir caminhos
    input_file = Path("data/processed/lista_final_processada.json")
    csv_output = Path("data/relatorio_final.csv")
    json_output = Path("data/processed/leiloeiros_rankeados.json")
    
    # Garantir que diretórios existem
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    
    # Carregar dados
    print("📁 Carregando dados...")
    leiloeiros = load_data(input_file)
    print(f"✅ Dados carregados: {len(leiloeiros)} leiloeiros")
    
    # Higienizar sites
    print("\n🧹 Higienizando sites...")
    leiloeiros = clean_sites(leiloeiros)
    
    # Reclassificar
    print("📊 Reclassificando leiloeiros...")
    leiloeiros = reclassify(leiloeiros)
    
    # Gerar relatório
    print("\n📈 Gerando relatório...")
    report = generate_report(leiloeiros)
    
    # Salvar resultados
    print("\n💾 Salvando resultados...")
    save_results(leiloeiros, csv_output, json_output)
    
    print("\n" + "=" * 60)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("=" * 60)
    print(f"\n🎯 Dados prontos para o dashboard:")
    print(f"   • Total: {report['total']}")
    print(f"   • Com Site: {report['com_site']}")
    print(f"   • Offline: {report['offline']}")
    print(f"\n🚀 Execute o dashboard atualizado:")
    print("   streamlit run src/app.py")

if __name__ == "__main__":
    main()
