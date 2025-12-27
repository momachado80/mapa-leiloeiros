import json
import pandas as pd
import os
import re

# Caminhos
INPUT_FILE = 'data/full_list.json'
OUTPUT_FILE = 'data/relatorio_final_ranking.csv'

def extrair_na_marra():
    print(f"🔍 Lendo {INPUT_FILE} de forma agressiva...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ ERRO: Arquivo {INPUT_FILE} não existe!")
        return

    # 1. Ler como texto bruto
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # 2. Limpeza prévia (Tira aspas curvas e quebras de linha estranhas)
    clean_text = raw_text.replace('“', '"').replace('”', '"').replace('\n', ' ')

    # 3. A MÁGICA: Usar Regex para achar apenas os objetos {...}
    # Isso ignora , cabeçalhos, rodapés, erros de vírgula, etc.
    padrao = r'\{.*?\}'
    objetos_encontrados = re.findall(padrao, clean_text)

    print(f"🧩 Encontrados {len(objetos_encontrados)} possíveis leiloeiros no meio do texto.")

    lista_final = []
    genericos = ['gmail', 'hotmail', 'outlook', 'yahoo', 'uol', 'bol', 'terra', 'ig', 'me.com']

    for item_str in objetos_encontrados:
        try:
            # Tenta converter cada pedacinho individualmente
            item = json.loads(item_str)
            
            nome = item.get('nome', 'Desconhecido')
            site = str(item.get('site', '')).lower()
            
            # Lógica de Classificação
            eh_generico = any(dom in site for dom in genericos)
            site_invalido = site in ['null', 'none', '', 'nan']
            
            if site_invalido or eh_generico:
                categoria = 'Offline / Sem Site'
                link = f"https://www.google.com/search?q=leilao+{nome.replace(' ', '+')}"
                texto_botao = "🔍 Buscar no Google"
                score = 5 # Score baixo
            else:
                categoria = 'Online'
                link = site if site.startswith('http') else f"http://{site}"
                texto_botao = "🌐 Acessar Site"
                score = 80 # Score alto

            lista_final.append({
                "Nome": nome,
                "Categoria": categoria,
                "Link": link,
                "Botão": texto_botao,
                "TechScore": score, # Importante para o gráfico não quebrar
                "Cidade": item.get('cidade', '-')
            })
            
        except json.JSONDecodeError:
            # Se um pedaço estiver muito quebrado, apenas ignora ele e continua
            continue

    # Salvar
    if lista_final:
        df = pd.DataFrame(lista_final)
        df.to_csv(OUTPUT_FILE, index=False)
        print("-" * 40)
        print(f"✅ SUCESSO TOTAL!")
        print(f"📊 Recuperados: {len(df)} leiloeiros.")
        print(f"🌐 Online: {len(df[df['Categoria']=='Online'])}")
        print(f"📴 Offline: {len(df[df['Categoria']!='Online'])}")
        print("-" * 40)
    else:
        print("❌ Nenhum leiloeiro válido encontrado. Verifique se copiou a lista certa.")

if __name__ == "__main__":
    extrair_na_marra()