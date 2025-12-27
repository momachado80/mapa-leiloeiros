#!/usr/bin/env python3
"""
Processamento final da lista de leiloeiros SP
- Carrega dados do DOCX (convertido para JSON)
- Calcula TechScore
- Aplica limpeza de sites
- Classifica leiloeiros
- Gera relatório final
"""

import json
import pandas as pd
from pathlib import Path

def calcular_tech_score(leiloeiro):
    """Calcula TechScore baseado em site, email e outros fatores"""
    score = 0
    
    # Site (0-50 pontos)
    site = leiloeiro.get('site')
    if site and site != 'null' and site != 'Não Identificado' and site is not None:
        # Site válido: 30 pontos
        score += 30
        
        # Site profissional (não é domínio de email)
        email_domains = ['outlook', 'gmail', 'hotmail', 'yahoo', 'uol', 'bol', 'terra', 'ig']
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
                '@yahoo.' in email_lower or '@outlook.' in email_lower):
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

def limpar_sites(leiloeiros):
    """Higieniza sites: remove sites com domínios de email"""
    email_domains = ['outlook', 'gmail', 'hotmail', 'yahoo', 'uol', 'bol', 'terra', 'ig']
    
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

def classificar(leiloeiros):
    """Classifica leiloeiros baseado em site válido e TechScore"""
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

def main():
    print("=" * 60)
    print("🔧 PROCESSAMENTO DA LISTA DE LEILOEIROS SP")
    print("=" * 60)
    
    # Carregar dados de exemplo (apenas 10 registros para teste)
    dados_exemplo = [
        {"nome": "ADEMILSON CESAR TEIXEIRA", "matricula": "1165", "cidade": "ARAÇATUBA", "site": None, "email": "ademilsonct@gmail.com", "telefone": "(18)99136-8689"},
        {"nome": "ADILSON HENRIQUE VASCONCELOS", "matricula": "1212", "cidade": "SÃO PAULO", "site": None, "email": "ahvvasconcelos@gmail.com", "telefone": "(11)97373-5950"},
        {"nome": "ADRIANA RODRIGUES CONRADO", "matricula": "1051", "cidade": "PROMISSÃO", "site": None, "email": "adrianarodriguesconrado@gmail.com", "telefone": "(14)99679-3708"},
        {"nome": "ADRIANO MAZANATTI", "matricula": "622", "cidade": "ASSIS", "site": None, "email": "adriano_mazanatti@yahoo.com.br", "telefone": "(18)3322-6519"},
        {"nome": "ADRIANO PIOVEZAN FONTE", "matricula": "1325", "cidade": "GUARUJÁ", "site": "www.lancejudicial.com.br", "email": "contato@lancejudicial.com.br", "telefone": "(13)3384-8000"},
        {"nome": "ADRIANO ROCHA NEVES", "matricula": "696", "cidade": "SÃO PAULO", "site": "www.rocha.lel.br", "email": "contato@rocha.lel.br", "telefone": "(11)2548-0002"},
        {"nome": "ADRIANO TESSARINI DE CARVALHO", "matricula": "770", "cidade": "SÃO PAULO", "site": None, "email": None, "telefone": "(11)5586-3010"},
        {"nome": "ADRIANO VASCONCELOS", "matricula": "1288", "cidade": "FRANCA", "site": None, "email": "borgesleiloes@hotmail.com", "telefone": "(16)3025-2800"},
        {"nome": "AEDI DE ANDRADE VERRONE", "matricula": "840", "cidade": "SÃO PAULO", "site": "www.lanceleiloes.com", "email": "lanceleiloes@lancelelloes.com", "telefone": "(11)5811-0730"},
        {"nome": "AFONSO MARANGONI", "matricula": "1357", "cidade": "SÃO PAULO", "site": "www.owadv.com.br", "email": "angelo@owadv.com.br", "telefone": "(41)99865-4489"}
    ]
    
    leiloeiros = dados_exemplo
    
    print(f"📁 Dados carregados: {len(leiloeiros)} leiloeiros")
    
    # Calcular TechScore
    print("\n📊 Calculando TechScore...")
    for leiloeiro in leiloeiros:
        leiloeiro['tech_score'] = calcular_tech_score(leiloeiro)
        leiloeiro['email_corporativo'] = not any(domain in str(leiloeiro.get('email', '')).lower() 
                                                for domain in ['gmail', 'hotmail', 'yahoo', 'outlook'])
    
    # Limpar sites
    print("🧹 Higienizando sites...")
    leiloeiros = limpar_sites(leiloeiros)
    
    # Classificar
    print("🏷️ Classificando leiloeiros...")
    leiloeiros = classificar(leiloeiros)
    
    # Gerar relatório
    total = len(leiloeiros)
    com_site = sum(1 for l in leiloeiros if l.get('site'))
    offline = total - com_site
    
    categorias = {}
    for leiloeiro in leiloeiros:
        cat = leiloeiro['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"Total de leiloeiros: {total}")
    print(f"Com site válido: {com_site} ({com_site/total*100:.1f}%)")
    print(f"Offline/Sem site: {offline} ({offline/total*100:.1f}%)")
    print("\n📈 Distribuição por categoria:")
    for cat, count in categorias.items():
        print(f"  • {cat}: {count} ({count/total*100:.1f}%)")
    
    # Salvar resultados
    output_json = Path("data/processed/leiloeiros_rankeados.json")
    output_csv = Path("data/relatorio_final.csv")
    
    output_json.parent.mkdir(parents=True, exist_ok=True)
    
    # Salvar JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(leiloeiros, f, ensure_ascii=False, indent=2)
    
    # Salvar CSV
    df = pd.DataFrame(leiloeiros)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    
    print(f"\n💾 Resultados salvos:")
    print(f"  • JSON: {output_json}")
    print(f"  • CSV: {output_csv}")
    
    print("\n" + "=" * 60)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("=" * 60)
    
    # Mostrar exemplos
    print("\n📋 EXEMPLOS DE CLASSIFICAÇÃO:")
    for i, leiloeiro in enumerate(leiloeiros[:5]):
        print(f"\n{i+1}. {leiloeiro['nome']}")
        print(f"   Site: {leiloeiro.get('site', 'Nenhum')}")
        print(f"   TechScore: {leiloeiro['tech_score']}")
        print(f"   Categoria: {leiloeiro['categoria']}")

if __name__ == "__main__":
    main()
