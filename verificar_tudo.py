#!/usr/bin/env python3
"""
Verificação final do sistema completo
"""

import json
import pandas as pd
from pathlib import Path
import sys

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE ARQUIVOS")
    print("=" * 60)
    
    arquivos = [
        ("data/raw/lista_completa_sp.json", "Dados brutos completos"),
        ("data/relatorio_final_ranking.csv", "CSV com todos os leiloeiros"),
        ("data/processed/ranking_final_inclusivo.json", "JSON processado"),
        ("src/processors/rank_everyone.py", "Script de processamento"),
        ("src/app.py", "Dashboard Streamlit"),
    ]
    
    todos_ok = True
    for caminho, descricao in arquivos:
        path = Path(caminho)
        if path.exists():
            print(f"✅ {descricao}: {caminho}")
            
            # Informações adicionais
            if caminho.endswith('.csv'):
                try:
                    df = pd.read_csv(path)
                    print(f"   • Registros: {len(df)}")
                    if 'tech_score' in df.columns:
                        print(f"   • TechScore médio: {df['tech_score'].mean():.1f}")
                except Exception as e:
                    print(f"   • Erro ao ler: {e}")
            elif caminho.endswith('.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"   • Registros: {len(data)}")
                except Exception as e:
                    print(f"   • Erro ao ler: {e}")
        else:
            print(f"❌ {descricao}: {caminho} (NÃO ENCONTRADO)")
            todos_ok = False
    
    return todos_ok

def analisar_dados():
    """Analisa os dados processados"""
    print("\n" + "=" * 60)
    print("📊 ANÁLISE DOS DADOS PROCESSADOS")
    print("=" * 60)
    
    csv_path = Path("data/relatorio_final_ranking.csv")
    if not csv_path.exists():
        print("❌ Arquivo de dados não encontrado")
        return False
    
    try:
        df = pd.read_csv(csv_path)
        total = len(df)
        print(f"📈 Total de leiloeiros: {total}")
        
        if 'categoria' in df.columns:
            print("\n🏷️ Distribuição por categoria:")
            for cat, count in df['categoria'].value_counts().items():
                print(f"   • {cat}: {count} ({count/total*100:.1f}%)")
        
        if 'tech_score' in df.columns:
            print(f"\n🎯 TechScore:")
            print(f"   • Média: {df['tech_score'].mean():.1f}")
            print(f"   • Mínimo: {df['tech_score'].min()}")
            print(f"   • Máximo: {df['tech_score'].max()}")
            
            # Distribuição
            print(f"\n📊 Distribuição do TechScore:")
            bins = [0, 20, 40, 60, 80, 100]
            labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
            df['score_bin'] = pd.cut(df['tech_score'], bins=bins, labels=labels)
            for label in labels:
                count = len(df[df['score_bin'] == label])
                if count > 0:
                    print(f"   • {label}: {count} ({count/total*100:.1f}%)")
        
        if 'email_corporativo' in df.columns:
            corporativos = df['email_corporativo'].sum()
            print(f"\n📧 Emails corporativos: {int(corporativos)}/{total} ({corporativos/total*100:.1f}%)")
        
        if 'site' in df.columns:
            com_site = df[df['site'].notna() & (df['site'] != '')].shape[0]
            print(f"🌐 Com site: {com_site}/{total} ({com_site/total*100:.1f}%)")
        
        # Oportunidades
        if 'categoria' in df.columns:
            offline = len(df[df['categoria'] == 'Offline/Sem Site'])
            pequenos = len(df[df['categoria'] == 'Pequeno (Com Site)'])
            oportunidades = offline + pequenos
            print(f"\n🎯 OPORTUNIDADES DE NEGÓCIO:")
            print(f"   • Offline/Sem Site: {offline} ({offline/total*100:.1f}%)")
            print(f"   • Pequeno (Com Site): {pequenos} ({pequenos/total*100:.1f}%)")
            print(f"   • TOTAL OPORTUNIDADES: {oportunidades} ({oportunidades/total*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return False

def testar_dashboard():
    """Testa se o dashboard pode ser importado"""
    print("\n" + "=" * 60)
    print("🚀 TESTE DO DASHBOARD")
    print("=" * 60)
    
    app_path = Path("src/app.py")
    if not app_path.exists():
        print("❌ Dashboard não encontrado")
        return False
    
    print("✅ Dashboard encontrado: src/app.py")
    
    try:
        import sys
        sys.path.insert(0, 'src')
        from app import load_data, create_sample_data
        
        print("✅ Funções do dashboard importáveis")
        
        # Testar carregamento
        print("\n🧪 Testando carregamento de dados...")
        df = load_data()
        print(f"✅ Dados carregados: {len(df)} registros")
        print(f"✅ Colunas disponíveis: {list(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 VERIFICAÇÃO FINAL DO SISTEMA")
    print("=" * 60)
    
    # Verificar arquivos
    arquivos_ok = verificar_arquivos()
    
    # Analisar dados
    dados_ok = analisar_dados()
    
    # Testar dashboard
    dashboard_ok = testar_dashboard()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    if arquivos_ok and dados_ok and dashboard_ok:
        print("✅ SISTEMA COMPLETO E FUNCIONAL!")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Execute o dashboard: streamlit run src/app.py")
        print("2. Acesse: http://localhost:8501")
        print("3. Use os filtros para explorar os dados")
        print("4. Identifique oportunidades de negócio")
    else:
        print("⚠️ ALGUNS PROBLEMAS FORAM ENCONTRADOS")
        print("\n🔧 CORREÇÕES NECESSÁRIAS:")
        if not arquivos_ok:
            print("• Verifique se os arquivos de dados existem")
        if not dados_ok:
            print("• Execute o script de processamento: python src/processors/rank_everyone.py")
        if not dashboard_ok:
            print("• Verifique as dependências: pip install streamlit pandas")
    
    print("\n" + "=" * 60)
    print("📞 INFORMAÇÕES DE CONTATO")
    print("=" * 60)
    print("Projeto: Mapa-Leiloeiros")
    print("Status: Sistema de análise de oportunidades")
    print("Data: 22/12/2025")
    print("Versão: 2.0.0 (Inclusiva - Todos os 600+ leiloeiros)")

if __name__ == "__main__":
    main()
