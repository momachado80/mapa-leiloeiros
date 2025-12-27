#!/usr/bin/env python3
"""
Rankeamento Inclusivo de Todos os Leiloeiros SP
Processa a lista completa sem excluir ninguém
"""

import json
import pandas as pd
from pathlib import Path
import sys

def calcular_tech_score(leiloeiro):
    """Calcula TechScore baseado em site, email e outros fatores"""
    score = 0
    
    # Site (0-50 pontos)
    site = leiloeiro.get('site')
    if site and site != 'null' and site != 'Não Identificado' and site is not None:
        # Site válido: 30 pontos
        score += 30
        
        # Site profissional (não é domínio de email)
        email_domains = ['outlook', 'gmail', 'hotmail', 'yahoo', 'uol', 'bol', 'terra', 'ig', 'me.com']
        site_lower = str(site).lower()
        if not any(domain in site_lower for domain in email_domains):
            # Site corporativo: +20 pontos
            score += 20
    
    # Email corporativo (0-30 pontos)
    email = leiloeiro.get('email')
    if email and email != 'null' and email is not None:
        # Email válido: 10 pontos
        score += 10
        
        # Email corporativo (não é gmail/hotmail/etc)
        email_lower = str(email).lower()
        if not ('@gmail.' in email_lower or '@hotmail.' in email_lower or 
                '@yahoo.' in email_lower or '@outlook.' in email_lower or
                '@uol.' in email_lower or '@bol.' in email_lower):
            # Email corporativo: +20 pontos
            score += 20
    
    # Telefone (0-10 pontos)
    telefone = leiloeiro.get('telefone')
    if telefone and telefone != 'null' and telefone is not None:
        score += 10
    
    # Matrícula (0-10 pontos)
    matricula = leiloeiro.get('matricula')
    if matricula and matricula != 'null' and matricula is not None:
        score += 10
    
    return min(score, 100)  # Máximo 100

def limpar_sites_falsos(leiloeiros):
    """Limpa sites falsos (domínios de email)"""
    email_domains = ['outlook', 'gmail', 'hotmail', 'yahoo', 'uol', 'bol', 'terra', 'ig', 'me.com']
    
    for leiloeiro in leiloeiros:
        site = leiloeiro.get('site')
        
        if not site or site == 'null' or site == 'Não Identificado' or site is None:
            leiloeiro['site'] = None
            continue
            
        site_str = str(site).lower()
        if any(domain in site_str for domain in email_domains):
            leiloeiro['site'] = None
        else:
            # Adicionar https:// se não tiver
            if site and not site.startswith(('http://', 'https://')):
                leiloeiro['site'] = f'https://{site}'
    
    return leiloeiros

def classificar_inclusivo(leiloeiros):
    """Classifica leiloeiros sem excluir ninguém (4 categorias)"""
    for leiloeiro in leiloeiros:
        site = leiloeiro.get('site')
        tech_score = leiloeiro.get('tech_score', 0)
        
        # Se não tem site válido -> Offline/Sem Site
        if not site:
            leiloeiro['categoria'] = 'Offline/Sem Site'
            leiloeiro['tech_score'] = 0  # Garante score 0 para offline
            continue
            
        # Tem site válido, classificar por TechScore
        if tech_score > 80:
            leiloeiro['categoria'] = 'Gigante (Portal)'
        elif tech_score >= 40:
            leiloeiro['categoria'] = 'Médio (Consolidado)'
        else:
            leiloeiro['categoria'] = 'Pequeno (Com Site)'
    
    return leiloeiros

def main():
    print("=" * 60)
    print("🔧 RANKEAMENTO INCLUSIVO - TODOS OS LEILOEIROS SP")
    print("=" * 60)
    
    # Carregar dados
    input_path = Path("data/raw/lista_completa_sp.json")
    if not input_path.exists():
        print(f"❌ Arquivo de entrada não encontrado: {input_path}")
        print("💡 Verifique se o arquivo data/raw/lista_completa_sp.json existe")
        sys.exit(1)
    
    print(f"📁 Carregando dados de: {input_path}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            leiloeiros = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {e}")
        sys.exit(1)
    
    print(f"✅ Dados carregados: {len(leiloeiros)} leiloeiros")
    
    # Limpar sites falsos
    print("\n🧹 Limpando sites falsos (domínios de email)...")
    leiloeiros = limpar_sites_falsos(leiloeiros)
    
    # Calcular TechScore
    print("📊 Calculando TechScore...")
    for leiloeiro in leiloeiros:
        leiloeiro['tech_score'] = calcular_tech_score(leiloeiro)
        leiloeiro['email_corporativo'] = not any(domain in str(leiloeiro.get('email', '')).lower() 
                                                for domain in ['gmail', 'hotmail', 'yahoo', 'outlook', 'uol', 'bol'])
    
    # Classificar (inclusivo - ninguém excluído)
    print("🏷️ Classificando leiloeiros (4 categorias inclusivas)...")
    leiloeiros = classificar_inclusivo(leiloeiros)
    
    # Gerar relatório
    total = len(leiloeiros)
    com_site = sum(1 for l in leiloeiros if l.get('site'))
    offline = total - com_site
    
    categorias = {}
    for leiloeiro in leiloeiros:
        cat = leiloeiro['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL (INCLUSIVO)")
    print("=" * 60)
    print(f"Total de leiloeiros: {total}")
    print(f"Com site válido: {com_site} ({com_site/total*100:.1f}%)")
    print(f"Offline/Sem site: {offline} ({offline/total*100:.1f}%)")
    print("\n📈 Distribuição por categoria:")
    for cat, count in categorias.items():
        print(f"  • {cat}: {count} ({count/total*100:.1f}%)")
    
    # Calcular TechScore médio (apenas para quem tem site)
    tech_scores = [l['tech_score'] for l in leiloeiros if l.get('site')]
    if tech_scores:
        avg_score = sum(tech_scores) / len(tech_scores)
        print(f"\n🎯 TechScore médio (com site): {avg_score:.1f}")
    
    # Salvar resultados
    output_csv = Path("data/relatorio_final_ranking.csv")
    output_json = Path("data/processed/ranking_final_inclusivo.json")
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    
    # Salvar CSV
    df = pd.DataFrame(leiloeiros)
    
    # Reordenar colunas para melhor visualização
    column_order = ['nome', 'matricula', 'cidade', 'site', 'email', 'telefone', 
                    'tech_score', 'email_corporativo', 'categoria']
    
    # Manter apenas colunas existentes
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n💾 CSV salvo: {output_csv}")
    
    # Salvar JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(leiloeiros, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON salvo: {output_json}")
    
    # Salvar também como relatorio_final.csv (para compatibilidade com dashboard)
    compat_csv = Path("data/relatorio_final.csv")
    df.to_csv(compat_csv, index=False, encoding='utf-8')
    print(f"💾 CSV de compatibilidade: {compat_csv}")
    
    print("\n" + "=" * 60)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("=" * 60)
    
    # Mostrar exemplos
    print("\n📋 EXEMPLOS DE CLASSIFICAÇÃO (primeiros 5):")
    for i, leiloeiro in enumerate(leiloeiros[:5]):
        print(f"\n{i+1}. {leiloeiro['nome']}")
        print(f"   Site: {leiloeiro.get('site', 'Nenhum')}")
        print(f"   TechScore: {leiloeiro['tech_score']}")
        print(f"   Categoria: {leiloeiro['categoria']}")
    
    print(f"\n🎯 OPORTUNIDADES DE NEGÓCIO:")
    print(f"   • Offline/Sem Site: {categorias.get('Offline/Sem Site', 0)} leiloeiros")
    print(f"   • Pequeno (Com Site): {categorias.get('Pequeno (Com Site)', 0)} leiloeiros")
    oportunidades = categorias.get('Offline/Sem Site', 0) + categorias.get('Pequeno (Com Site)', 0)
    print(f"   • TOTAL OPORTUNIDADES: {oportunidades} ({oportunidades/total*100:.1f}%)")

if __name__ == "__main__":
    main()
