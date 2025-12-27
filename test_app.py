#!/usr/bin/env python3
"""
Teste rápido do aplicativo Streamlit
"""

import sys
import subprocess
import time
import signal

def test_streamlit():
    """Testa se o Streamlit inicia sem erros"""
    
    print("🚀 Testando aplicativo Streamlit...")
    
    # Comando para iniciar o Streamlit
    cmd = ["streamlit", "run", "src/app.py", "--server.headless", "true", "--server.port", "8502"]
    
    try:
        # Inicia o processo
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguarda alguns segundos
        time.sleep(5)
        
        # Verifica se ainda está rodando
        if proc.poll() is None:
            print("✅ Streamlit iniciado com sucesso!")
            print("📊 Verificando saída...")
            
            # Tenta ler alguma saída
            try:
                stdout, stderr = proc.communicate(timeout=2)
                if stdout:
                    print(f"STDOUT (primeiras linhas):")
                    for line in stdout.split('\n')[:5]:
                        if line.strip():
                            print(f"  {line}")
                if stderr:
                    print(f"STDERR (primeiras linhas):")
                    for line in stderr.split('\n')[:5]:
                        if line.strip():
                            print(f"  {line}")
            except subprocess.TimeoutExpired:
                pass
            
            # Encerra o processo
            proc.terminate()
            proc.wait(timeout=3)
            print("✅ Processo finalizado corretamente")
            return True
        else:
            # Processo terminou prematuramente
            stdout, stderr = proc.communicate()
            print("❌ Streamlit falhou ao iniciar")
            print(f"STDOUT: {stdout[:200]}")
            print(f"STDERR: {stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Streamlit: {e}")
        return False

def test_data_loading():
    """Testa se os dados são carregados corretamente"""
    
    print("\n📊 Testando carregamento de dados...")
    
    try:
        import pandas as pd
        from pathlib import Path
        
        csv_path = Path("data/relatorio_final.csv")
        
        if not csv_path.exists():
            print("❌ Arquivo CSV não encontrado")
            return False
        
        df = pd.read_csv(csv_path)
        print(f"✅ CSV carregado: {len(df)} leiloeiros")
        
        # Verifica colunas importantes
        required_cols = ['nome', 'categoria', 'link_acesso', 'texto_link', 'score']
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            print(f"❌ Colunas faltando: {missing}")
            return False
        
        print(f"✅ Todas colunas necessárias presentes")
        
        # Verifica categorias
        online = len(df[df['categoria'] == 'Online'])
        offline = len(df[df['categoria'] == 'Offline'])
        print(f"✅ Categorias: Online={online}, Offline={offline}")
        
        # Verifica links
        valid_links = df['link_acesso'].notna().sum()
        print(f"✅ Links válidos: {valid_links} de {len(df)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False

def main():
    """Função principal"""
    
    print("=" * 60)
    print("TESTE DO DASHBOARD MAPA DE LEILOEIROS SP")
    print("=" * 60)
    
    # Testa carregamento de dados
    if not test_data_loading():
        print("\n❌ Teste de dados FALHOU")
        sys.exit(1)
    
    # Testa Streamlit
    if not test_streamlit():
        print("\n❌ Teste do Streamlit FALHOU")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 60)
    print("\n🎉 O dashboard está pronto para uso!")
    print("\n📋 Para executar:")
    print("   cd /Users/momachado/Desktop/Mapa-Leiloeiros")
    print("   source venv/bin/activate")
    print("   streamlit run src/app.py")
    print("\n🌐 Acesse: http://localhost:8501")

if __name__ == "__main__":
    main()
