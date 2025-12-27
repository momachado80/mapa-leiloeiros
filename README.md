# Mapa-Leiloeiros

Sistema SaaS para mapeamento e ranqueamento de leiloeiros das juntas comerciais do Brasil.

## Objetivo

Criar um sistema completo que mapeia todos os leiloeiros registrados nas juntas comerciais do Brasil e ranqueia sua relevância online através de análise de dados e métricas digitais.

## Stack Tecnológica

- **Backend/Scraping**: Python 3.11+
- **Banco de Dados**: SQLite (inicial), PostgreSQL (produção)
- **Scraping**: Crawl4AI, Playwright
- **Processamento de Dados**: Pandas, NumPy
- **APIs**: FastAPI (futuro)
- **Frontend**: React (futuro)

## Estrutura do Projeto

```
Mapa-Leiloeiros/
├── src/
│   ├── scrapers/          # Scripts de scraping para cada junta comercial
│   │   └── sp_jucesp.py   # Scraper para JUCE-SP
│   ├── models/            # Modelos de dados e ORM
│   ├── api/               # API REST (futuro)
│   └── utils/             # Utilitários comuns
├── data/
│   ├── raw/               # Dados brutos extraídos
│   └── processed/         # Dados processados e limpos
├── notebooks/             # Jupyter notebooks para análise
├── tests/                 # Testes automatizados
├── venv/                  # Ambiente virtual Python
├── requirements.txt       # Dependências do projeto
├── .gitignore            # Arquivos ignorados pelo Git
└── README.md             # Documentação do projeto
```

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/mapa-leiloeiros.git
   cd mapa-leiloeiros
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Instale os navegadores do Playwright:
   ```bash
   playwright install
   ```

## Uso

### Scraper JUCE-SP

Para executar o scraper da Junta Comercial de São Paulo:

```bash
python src/scrapers/sp_jucesp.py
```

O script irá:
- Acessar o site da JUCE-SP
- Extrair a lista de leiloeiros (nome, matrícula, site)
- Lidar com paginação automaticamente
- Salvar os dados em `data/raw/leiloeiros_sp.csv`

### Configuração

O scraper está configurado para:
- Modo headless (sem interface gráfica)
- 5 páginas máximas (ajustável)
- 10 resultados por página
- Pausas de 2 segundos entre requisições

## Próximos Passos

1. **Expansão para outras juntas comerciais**:
   - JUCE-RJ, JUCE-MG, etc.
   - Scrapers específicos para cada estado

2. **Banco de Dados**:
   - Migração para PostgreSQL
   - Schema otimizado para consultas

3. **Análise de Relevância**:
   - Métricas de presença online
   - Ranqueamento baseado em múltiplos fatores
   - Dashboard de visualização

4. **API REST**:
   - Endpoints para consulta de dados
   - Autenticação e autorização
   - Documentação Swagger/OpenAPI

5. **Frontend**:
   - Dashboard React/Next.js
   - Visualizações interativas
   - Filtros e buscas avançadas

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## Contato

Seu Nome - [@seu_twitter](https://twitter.com/seu_twitter) - email@exemplo.com

Link do Projeto: [https://github.com/seu-usuario/mapa-leiloeiros](https://github.com/seu-usuario/mapa-leiloeiros)
