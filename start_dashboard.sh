#!/bin/bash
# Script para iniciar o dashboard Streamlit

echo "🚀 Iniciando Mapa de Leiloeiros SP..."
echo "======================================"

# Verifica se o arquivo de dados existe
if [ ! -f "data/relatorio_final.csv" ]; then
    echo "❌ Arquivo de dados não encontrado!"
    echo "Executando processamento..."
    python src/processors/fix_all.py
fi

# Verifica se o Streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit não encontrado!"
    echo "Instalando Streamlit..."
    pip install streamlit
fi

echo "✅ Tudo pronto!"
echo ""
echo "📊 Iniciando servidor Streamlit..."
echo "🔗 O dashboard será aberto em: http://localhost:8501"
echo ""
echo "📝 Para parar o servidor: Pressione CTRL+C no terminal"
echo ""

# Inicia o Streamlit
streamlit run src/app.py
