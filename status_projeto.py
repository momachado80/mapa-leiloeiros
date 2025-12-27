#!/usr/bin/env python3
"""
Status do Projeto Mapa-Leiloeiros
Verifica todos os componentes e mostra o estado atual
"""

import json
import pandas as pd
from pathlib import Path
import sys

def print_header(title):
    print("\n" + "=" * 60)
    print(f"📊 {title}")
    print("=" * 60)

def check_data_files():
    """Verifica arquivos de dados"""
    print_header("VERIFICAÇÃO DE ARQUIVOS DE DADOS")
    
    files_to_check = [
        ("data/raw/lista_completa_sp.json", "Dados brutos extraídos"),
        ("data/relatorio_final.csv", "Relatório final processado"),
        ("data/processed/leiloeiros_rankeados.json", "JSON processado"),
    ]
    
    for file_path, description in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {description}: {file_path}")
            
            # Informações adicionais
            if file_path.endswith('.csv'):
                try:
                    df = pd.read_csv(path)
                    print(f"   • Registros: {len(df)}")
                    if 'tech_score' in df.columns:
                        print(f"   • TechScore médio: {df['tech_score'].mean():.1f}")
                except Exception as e:
                    print(f"   • Erro ao ler: {e}")
            elif file_path.endswith('.json'):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"   • Registros: {len(data)}")
                except Exception as e:
                    print(f"   • Erro ao ler: {e}")
        else:
            print(f"❌ {description}: {file_path} (NÃO ENCONTRADO)")

def check_scripts():
    """Verifica scripts principais"""
    print_header("VERIFICAÇÃO DE SCRIPTS")
    
    scripts_to_check = [
        ("process_lista_final.py", "Processamento principal"),
        ("src/app.py", "Dashboard Streamlit"),
        ("test_dashboard.py", "Teste do dashboard"),
    ]
    
    for script_path, description in scripts_to_check:
        path = Path(script_path)
        if path.exists():
            print(f"✅ {description}: {script_path}")
            print(f"   • Tamanho: {path.stat().st_size} bytes")
        else:
            print(f"❌ {description}: {script_path} (NÃO ENCONTRADO)")

def check_dependencies():
    """Verifica dependências Python"""
    print_header("VERIFICAÇÃO DE DEPENDÊNCIAS")
    
    dependencies = [
        ("pandas", "pd"),
        ("streamlit", "st"),
        ("json", "json"),
        ("pathlib", "Path"),
    ]
    
    for package, import_name in dependencies:
        try:
            if package == "json":
                import json
                print(f"✅ {package}: OK")
            elif package == "pathlib":
                from pathlib import Path
                print(f"✅ {package}: OK")
            else:
                __import__(package)
                print(f"✅ {package}: OK")
        except ImportError:
            print(f"❌ {package}: NÃO INSTALADO")

def analyze_data():
    """Analisa os dados processados"""
    print_header("ANÁLISE DOS DADOS PROCESSADOS")
    
    csv_path = Path("data/relatorio_final.csv")
    if not csv_path.exists():
        print("❌ Arquivo de dados não encontrado")
        return
    
    try:
        df = pd.read_csv(csv_path)
        print(f"📈 Total de leiloeiros: {len(df)}")
        
        # Estatísticas básicas
        if 'tech_score' in df.columns:
            print(f"\n📊 TechScore:")
            print(f"   • Média: {df['tech_score'].mean():.1f}")
            print(f"   • Mínimo: {df['tech_score'].min()}")
            print(f"   • Máximo: {df['tech_score'].max()}")
            print(f"   • Mediana: {df['tech_score'].median():.1f}")
            
            # Distribuição
            print(f"\n📈 Distribuição do TechScore:")
            bins = [0, 20, 40, 60, 80, 100]
            labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
            if len(df) > 0:
                df['score_bin'] = pd.cut(df['tech_score'], bins=bins, labels=labels)
                for label in labels:
                    count = len(df[df['score_bin'] == label])
                    if count > 0:
                        print(f"   • {label}: {count} ({count/len(df)*100:.1f}%)")
        
        if 'categoria' in df.columns:
            print(f"\n🏷️ Categorias:")
            for cat, count in df['categoria'].value_counts().items():
                print(f"   • {cat}: {count} ({count/len(df)*100:.1f}%)")
        
        if 'email_corporativo' in df.columns:
            corporativos = df['email_corporativo'].sum()
            print(f"\n📧 Emails corporativos: {int(corporativos)}/{len(df)} ({corporativos/len(df)*100:.1f}%)")
        
        if 'site' in df.columns:
            com_site = df[df['site'].notna() & (df['site'] != '')].shape[0]
            print(f"🌐 Com site: {com_site}/{len(df)} ({com_site/len(df)*100:.1f}%)")
        
        # Oportunidades (Offline + Pequenos)
        if 'categoria' in df.columns:
            offline = len(df[df['categoria'] == 'Offline (Sem Site)'])
            pequenos = len(df[df['categoria'] == 'Pequeno (Com Site)'])
            oportunidades = offline + pequenos
            print(f"\n🎯 OPORTUNIDADES DE NEGÓCIO:")
            print(f"   • Offline (Sem Site): {offline} ({offline/len(df)*100:.1f}%)")
            print(f"   • Pequenos (Com Site): {pequenos} ({pequenos/len(df)*100:.1f}%)")
            print(f"   • TOTAL OPORTUNIDADES: {oportunidades} ({oportunidades/len(df)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

def check_dashboard():
    """Verifica o dashboard"""
    print_header("VERIFICAÇÃO DO DASHBOARD")
    
    app_path = Path("src/app.py")
    if not app_path.exists():
        print("❌ Dashboard não encontrado")
        return
    
    print("✅ Dashboard encontrado: src/app.py")
    
    # Verificar se pode ser importado
    try:
        import sys
        sys.path.insert(0, 'src')
        from app import load_data
        
        print("✅ Funções do dashboard importáveis")
        
        # Testar carregamento
        df = load_data()
        print(f"✅ Dados carregados: {len(df)} registros")
        
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")

def main():
    print("=" * 60)
    print("🔍 STATUS DO PROJETO MAPA-LEILOEIROS")
    print("=" * 60)
    
    check_data_files()
    check_scripts()
    check_dependencies()
    analyze_data()
    check_dashboard()
    
    print_header("PRÓXIMOS PASSOS")
    
    print("🚀 PARA EXECUTAR O DASHBOARD:")
    print("   streamlit run src/app.py")
    print("\n🔧 PARA PROCESSAR MAIS DADOS:")
    print("   python process_lista_final.py")
    print("\n📊 PARA VERIFICAR DADOS:")
    print("   python status_projeto.py")
    
    print("\n" + "=" * 60)
    print("✅ STATUS VERIFICADO COM SUCESSO")
    print("=" * 60)

if __name__ == "__main__":
    main()
