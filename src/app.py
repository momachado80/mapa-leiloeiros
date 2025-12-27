import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Radar de Leilões")
ARQUIVO_CSV = 'data/relatorio_final_ranking.csv'

st.title("🎯 Radar de Leilões (600+)")

if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV)
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", len(df))
    col2.metric("Online", len(df[df['Categoria']=='Online']))
    col3.metric("Offline", len(df[df['Categoria']!='Online']))
    
    # Filtro
    tipo = st.sidebar.radio("Filtrar:", ["Todos", "Online", "Offline / Sem Site"])
    if tipo != "Todos":
        df = df[df['Categoria'] == tipo]

    # Tabela com Links
    st.data_editor(
        df,
        column_config={
            "Link": st.column_config.LinkColumn(
                "Acesso Rápido", display_text="Botão"
            )
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("⚠️ Dados não encontrados. Rode o script de processamento.")