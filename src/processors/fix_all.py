#!/usr/bin/env python3
"""
Processador de Dados - Fix All
Lê data/full_list.json e gera um CSV robusto com categorização de sites.
"""

import json
import csv
import re
from pathlib import Path
from urllib.parse import quote

def process_site(site, nome):
    """
    Processa o site de um leiloeiro e determina categoria, link e score.
    
    Args:
        site (str): Site do leiloeiro (pode ser None ou string)
        nome (str): Nome do leiloeiro
    
    Returns:
        tuple: (categoria, link_acesso, texto_link, score)
    """
    # Lista de domínios de email que indicam site inválido
    email_domains = ['gmail', 'hotmail', 'outlook', 'yahoo', 'uol', 'terra', 'bol']
    
    # Verifica se site é nulo, vazio ou contém domínio de email
    if not site or pd.isna(site) or str(site).strip() == '':
        return 'Offline', None, None, 0
    
    site_str = str(site).lower().strip()
    
    # Verifica se contém domínio de email
    for domain in email_domains:
        if domain in site_str:
            # Cria URL de busca no Google
            search_query = f"leilao {nome}"
            google_url = f"https://www.google.com/search?q={quote(search_query)}"
            return 'Offline', google_url, '🔍 Buscar no Google', 0
    
    # Verifica se é um site válido (começa com http ou www)
    if site_str.startswith('http://') or site_str.startswith('https://'):
        link = site_str
    elif site_str.startswith('www.'):
        link = f"http://{site_str}"
    else:
        link = f"http://{site_str}"
    
    # Verifica se é um domínio válido (contém ponto)
    if '.' not in site_str:
        search_query = f"leilao {nome}"
        google_url = f"https://www.google.com/search?q={quote(search_query)}"
        return 'Offline', google_url, '🔍 Buscar no Google', 0
    
    return 'Online', link, '🌐 Acessar Site', 60

def main():
    """Função principal do processador."""
    # Caminhos dos arquivos
    input_path = Path("data/full_list.json")
    output_path = Path("data/relatorio_final.csv")
    
    print(f"📂 Lendo dados de: {input_path}")
    
    # Verifica se o arquivo de entrada existe
    if not input_path.exists():
        print(f"❌ Arquivo não encontrado: {input_path}")
        return
    
    # Carrega os dados JSON - trata múltiplos arrays no mesmo arquivo
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Divide o conteúdo em linhas para análise
        lines = content.strip().split('\n')
        
        # Encontra todos os arrays JSON no arquivo
        data = []
        current_array = []
        in_array = False
        brace_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('['):
                in_array = True
                brace_count = 1
                current_array = [line]
            elif in_array:
                current_array.append(line)
                brace_count += line.count('[') - line.count(']')
                
                if brace_count == 0:
                    # Fechou o array
                    array_str = '\n'.join(current_array)
                    try:
                        array_data = json.loads(array_str)
                        if isinstance(array_data, list):
                            data.extend(array_data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Aviso: Erro ao decodificar um array: {e}")
                    in_array = False
                    current_array = []
        
        # Se ainda estiver em um array no final (formato inválido), tenta processar
        if in_array and current_array:
            array_str = '\n'.join(current_array)
            try:
                array_data = json.loads(array_str)
                if isinstance(array_data, list):
                    data.extend(array_data)
            except:
                pass
                
        if not data:
            print(f"❌ Não foi possível extrair dados JSON válidos")
            return
            
    except Exception as e:
        print(f"❌ Erro ao processar JSON: {e}")
        return
    
    print(f"📊 Total de leiloeiros no JSON: {len(data)}")
    
    # Processa cada leiloeiro
    processed_data = []
    
    for leiloeiro in data:
        nome = leiloeiro.get('nome', '')
        site = leiloeiro.get('site')
        email = leiloeiro.get('email', '')
        telefone = leiloeiro.get('telefone', '')
        matricula = leiloeiro.get('matricula', '')
        cidade = leiloeiro.get('cidade', '')
        
        # Processa o site
        categoria, link_acesso, texto_link, score = process_site(site, nome)
        
        # Cria registro processado
        registro = {
            'nome': nome,
            'matricula': matricula,
            'cidade': cidade,
            'site_original': site if site else '',
            'email': email,
            'telefone': telefone,
            'categoria': categoria,
            'link_acesso': link_acesso if link_acesso else '',
            'texto_link': texto_link if texto_link else '',
            'score': score
        }
        
        processed_data.append(registro)
    
    # Salva em CSV
    try:
        # Cria diretório se não existir
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define as colunas do CSV
        fieldnames = [
            'nome', 'matricula', 'cidade', 'site_original', 'email', 
            'telefone', 'categoria', 'link_acesso', 'texto_link', 'score'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_data)
        
        print(f"✅ CSV salvo em: {output_path}")
        print(f"📈 Processados: {len(processed_data)} leiloeiros")
        
        # Estatísticas
        online_count = sum(1 for r in processed_data if r['categoria'] == 'Online')
        offline_count = sum(1 for r in processed_data if r['categoria'] == 'Offline')
        
        print(f"📊 Estatísticas:")
        print(f"   • Online: {online_count} leiloeiros ({online_count/len(processed_data)*100:.1f}%)")
        print(f"   • Offline: {offline_count} leiloeiros ({offline_count/len(processed_data)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Erro ao salvar CSV: {e}")
        return

if __name__ == "__main__":
    # Importa pandas apenas para pd.isna se necessário
    try:
        import pandas as pd
    except ImportError:
        # Define uma função simples se pandas não estiver disponível
        class PD:
            @staticmethod
            def isna(value):
                return value is None or (isinstance(value, str) and value.strip() == '')
        pd = PD()
    
    main()
