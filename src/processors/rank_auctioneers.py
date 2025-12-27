"""
Sistema de Ranqueamento de Autoridade para Leiloeiros
Analisa métricas de SEO e tecnologia para diferenciar 'Gigantes' de leiloeiros pequenos.

Modo: DEMONSTRAÇÃO (usa dados simulados para mostrar a lógica completa)
"""
import json
import whois
import requests
import re
import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import time
from pathlib import Path

class AuctioneerRanker:
    """Classifica leiloeiros baseado em métricas de autoridade online"""
    
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def load_leiloeiros(self, input_path: str = "data/raw/leiloeiros_sp.json") -> List[Dict]:
        """Carrega os dados dos leiloeiros do arquivo JSON"""
        filepath = Path(input_path)
        if not filepath.exists():
            print(f"❌ Arquivo não encontrado: {input_path}")
            print("📝 Usando dados de demonstração...")
            return self.get_demo_data()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ {len(data)} leiloeiros carregados")
        return data
    
    def get_demo_data(self) -> List[Dict]:
        """Retorna dados de demonstração com domínios reais para teste"""
        return [
            {
                "nome": "ZUK LEILÕES S/A",
                "matricula": "ZUK001/SP",
                "site": "https://www.google.com"  # Domínio real para teste
            },
            {
                "nome": "MEGALEILÕES BRASIL",
                "matricula": "MEGA002/SP",
                "site": "https://www.github.com"  # Domínio real para teste
            },
            {
                "nome": "SATO AUCTION HOUSE",
                "matricula": "SATO003/SP",
                "site": "https://www.wikipedia.org"  # Domínio real para teste
            },
            {
                "nome": "PEQUENO LEILOEIRO LOCAL",
                "matricula": "LOCAL004/SP",
                "site": "http://exemplo-local.com.br"  # Domínio fictício
            },
            {
                "nome": "LEILÕES RÁPIDOS ME",
                "matricula": "RAPID005/SP",
                "site": "https://www.cloudflare.com"  # Domínio com CDN
            }
        ]
    
    def extract_domain(self, url: str) -> Optional[str]:
        """Extrai o domínio de uma URL"""
        if not url or url == 'N/A':
            return None
        
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return parsed.netloc.lower()
            return None
        except:
            return None
    
    def get_domain_age(self, domain: str) -> Optional[Tuple[float, datetime]]:
        """
        Obtém a idade do domínio usando WHOIS.
        Em modo demo, simula idades diferentes.
        
        Returns:
            Tuple (idade_em_anos, data_de_registro) ou None
        """
        if not domain:
            return None
        
        if self.demo_mode:
            # Simula idades diferentes para demonstração
            demo_ages = {
                'google.com': 25.5,      # Domínio muito antigo
                'github.com': 15.2,       # Domínio antigo
                'wikipedia.org': 23.8,    # Domínio muito antigo
                'cloudflare.com': 12.7,   # Domínio antigo
                'exemplo-local.com.br': 1.2  # Domínio novo
            }
            
            for demo_domain, age in demo_ages.items():
                if demo_domain in domain:
                    creation_date = datetime.now() - timedelta(days=age*365.25)
                    return (age, creation_date)
            
            # Default: domínio médio (5 anos)
            return (5.0, datetime.now() - timedelta(days=5*365.25))
        
        # Modo real: usa WHOIS
        try:
            time.sleep(1)  # Delay para evitar rate limiting
            w = whois.whois(domain)
            
            if not w.creation_date:
                return None
            
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if isinstance(creation_date, datetime):
                age_years = (datetime.now() - creation_date).days / 365.25
                return (age_years, creation_date)
            
            return None
            
        except Exception as e:
            print(f"⚠ Erro WHOIS para {domain}: {str(e)[:100]}...")
            return None
    
    def check_https(self, url: str) -> bool:
        """Verifica se o site usa HTTPS"""
        if not url or url == 'N/A':
            return False
        
        return url.startswith('https://')
    
    def detect_cdn(self, domain: str) -> Tuple[bool, List[str]]:
        """
        Detecta se o site usa CDN (Cloudflare, AWS, Akamai, etc.)
        Em modo demo, simula detecção baseada no domínio.
        """
        if not domain:
            return False, []
        
        if self.demo_mode:
            # Simula detecção de CDN para demonstração
            cdn_domains = {
                'cloudflare.com': ['cloudflare'],
                'google.com': ['google', 'gstatic'],
                'github.com': ['fastly', 'github'],
                'wikipedia.org': ['wikimedia', 'akamai'],
            }
            
            for cdn_domain, cdns in cdn_domains.items():
                if cdn_domain in domain:
                    return True, cdns
            
            return False, []
        
        # Modo real: faz requisição HTTP
        try:
            response = self.session.get(f"http://{domain}", timeout=10, allow_redirects=True)
            headers = response.headers
            
            cdns_detected = []
            cdn_indicators = {
                'server': ['cloudflare', 'akamai', 'aws', 'fastly', 'cloudfront'],
                'via': ['cloudflare', 'akamai', 'aws'],
                'x-cache': ['cloudflare', 'akamai'],
                'x-powered-by': ['cloudflare'],
            }
            
            for header_name, cdn_list in cdn_indicators.items():
                header_value = headers.get(header_name, '').lower()
                for cdn in cdn_list:
                    if cdn in header_value:
                        cdns_detected.append(cdn)
            
            html = response.text.lower()
            for cdn in ['cloudflare', 'akamai', 'aws', 'cloudfront']:
                if cdn in html:
                    cdns_detected.append(cdn)
            
            cdns_detected = list(set(cdns_detected))
            return len(cdns_detected) > 0, cdns_detected
            
        except Exception as e:
            print(f"⚠ Erro ao detectar CDN para {domain}: {str(e)[:100]}...")
            return False, []
    
    def detect_social_media(self, domain: str) -> Tuple[int, List[str]]:
        """
        Detecta presença em redes sociais.
        Em modo demo, simula contagens diferentes.
        """
        if not domain:
            return 0, []
        
        if self.demo_mode:
            # Simula presença em redes sociais para demonstração
            social_profiles = {
                'google.com': (4, ['youtube', 'facebook', 'twitter', 'linkedin']),
                'github.com': (3, ['twitter', 'youtube', 'linkedin']),
                'wikipedia.org': (2, ['facebook', 'twitter']),
                'cloudflare.com': (3, ['twitter', 'linkedin', 'youtube']),
            }
            
            for demo_domain, (count, platforms) in social_profiles.items():
                if demo_domain in domain:
                    return count, platforms
            
            # Default: poucas redes sociais
            return (1, ['facebook'])
        
        # Modo real: analisa HTML
        try:
            response = self.session.get(f"http://{domain}", timeout=10)
            html = response.text.lower()
            
            social_platforms = {
                'instagram': ['instagram.com', 'instagr.am'],
                'facebook': ['facebook.com', 'fb.com'],
                'linkedin': ['linkedin.com', 'linked.in'],
                'youtube': ['youtube.com', 'youtu.be'],
                'twitter': ['twitter.com', 'x.com'],
            }
            
            detected_platforms = []
            for platform, domains in social_platforms.items():
                for domain_pattern in domains:
                    pattern = f'href=["\']https?://[^"\']*{domain_pattern}[^"\']*["\']'
                    if re.search(pattern, html):
                        detected_platforms.append(platform)
                        break
            
            detected_platforms = list(set(detected_platforms))
            return len(detected_platforms), detected_platforms
            
        except Exception as e:
            print(f"⚠ Erro ao detectar redes sociais para {domain}: {str(e)[:100]}...")
            return 0, []
    
    def calculate_score(self, leiloeiro: Dict, metrics: Dict) -> Dict:
        """
        Calcula o score de autoridade (0-100) baseado nas métricas.
        
        Lógica:
        - Base: 0
        - Domínio Antigo (>10 anos): +30 pontos
        - Usa Cloudflare/CDN: +20 pontos
        - Cada Rede Social detectada: +10 pontos (Max 40)
        - HTTPS: +10 pontos
        """
        score = 0
        breakdown = {}
        
        # 1. Idade do domínio
        domain_age = metrics.get('domain_age')
        if domain_age and domain_age > 10:
            score += 30
            breakdown['domain_age'] = 30
            print(f"   🎂 Domínio antigo (>10 anos): +30 pontos")
        elif domain_age and domain_age > 5:
            score += 15
            breakdown['domain_age'] = 15
            print(f"   🎂 Domínio médio (5-10 anos): +15 pontos")
        elif domain_age and domain_age > 2:
            score += 5
            breakdown['domain_age'] = 5
            print(f"   🎂 Domínio jovem (2-5 anos): +5 pontos")
        
        # 2. CDN
        uses_cdn = metrics.get('uses_cdn', False)
        if uses_cdn:
            score += 20
            breakdown['cdn'] = 20
            print(f"   ☁️  Usa CDN: +20 pontos")
        
        # 3. Redes sociais
        social_count = metrics.get('social_count', 0)
        social_score = min(social_count * 10, 40)  # Max 40 pontos
        score += social_score
        breakdown['social_media'] = social_score
        if social_score > 0:
            print(f"   📱 {social_count} redes sociais: +{social_score} pontos")
        
        # 4. HTTPS
        has_https = metrics.get('has_https', False)
        if has_https:
            score += 10
            breakdown['https'] = 10
            print(f"   🔒 HTTPS: +10 pontos")
        
        # Classificação
        if score >= 70:
            category = "GIGANTE 🏆"
        elif score >= 40:
            category = "MÉDIO ⚖️"
        else:
            category = "PEQUENO 🔍"
        
        print(f"   📊 Score total: {score}/100 | Categoria: {category}")
        
        return {
            'score': score,
            'category': category,
            'breakdown': breakdown,
            'metrics': metrics
        }
    
    def analyze_leiloeiro(self, leiloeiro: Dict) -> Dict:
        """Analisa um leiloeiro individual e retorna todas as métricas"""
        print(f"\n🔍 Analisando: {leiloeiro.get('nome', 'N/A')}")
        print(f"   🌐 Site: {leiloeiro.get('site', 'N/A')}")
        
        url = leiloeiro.get('site', '')
        domain = self.extract_domain(url)
        
        metrics = {
            'domain': domain,
            'has_https': self.check_https(url),
            'domain_age': None,
            'domain_creation_date': None,
            'uses_cdn': False,
            'cdns_detected': [],
            'social_count': 0,
            'social_platforms': [],
        }
        
        if domain:
            print(f"   🔎 Domínio: {domain}")
            
            # Idade do domínio
            domain_info = self.get_domain_age(domain)
            if domain_info:
                age_years, creation_date = domain_info
                metrics['domain_age'] = age_years
                metrics['domain_creation_date'] = creation_date.isoformat()
                print(f"   📅 Idade do domínio: {age_years:.1f} anos")
            
            # CDN
            uses_cdn, cdns = self.detect_cdn(domain)
            metrics['uses_cdn'] = uses_cdn
            metrics['cdns_detected'] = cdns
            if uses_cdn:
                print(f"   ☁️  CDNs detectadas: {', '.join(cdns)}")
            
            # Redes sociais
            social_count, platforms = self.detect_social_media(domain)
            metrics['social_count'] = social_count
            metrics['social_platforms'] = platforms
            if social_count > 0:
                print(f"   📱 Redes sociais: {', '.join(platforms)}")
        
        # Calcula score
        ranking = self.calculate_score(leiloeiro, metrics)
        
        return {
            **leiloeiro,
            'ranking': ranking
        }
    
    def analyze_all(self, leiloeiros: List[Dict]) -> List[Dict]:
        """Analisa todos os leiloeiros"""
        results = []
        
        print(f"\n📊 Analisando {len(leiloeiros)} leiloeiros...")
        
        for i, leiloeiro in enumerate(leiloeiros, 1):
            result = self.analyze_leiloeiro(leiloeiro)
            results.append(result)
            
            if not self.demo_mode and i < len(leiloeiros):
                time.sleep(1)  # Delay para evitar bloqueios
        
        return results
    
    def save_results(self, results: List[Dict], output_path: str = "data/processed/ranking_autoridade.json"):
        """Salva os resultados ordenados por score"""
        # Ordena por score (decrescente)
        sorted_results = sorted(results, key=lambda x: x['ranking']['score'], reverse=True)
        
        # Garante que o diretório existe
        filepath = Path(output_path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepara dados para JSON
        output_data = []
        for result in sorted_results:
            output_data.append({
                'nome': result['nome'],
                'matricula': result['matricula'],
                'site': result['site'],
                'score': result['ranking']['score'],
                'category': result['ranking']['category'],
                'breakdown': result['ranking']['breakdown'],
                'metrics': {
                    'domain_age': result['ranking']['metrics'].get('domain_age'),
                    'has_https': result['ranking']['metrics'].get('has_https'),
                    'uses_cdn': result['ranking']['metrics'].get('uses_cdn'),
                    'social_count': result['ranking']['metrics'].get('social_count'),
                    'social_platforms': result['ranking']['metrics'].get('social_platforms'),
                }
            })
        
        # Salva em JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Resultados salvos em: {output_path}")
        print(f"📊 Total de leiloeiros analisados: {len(output_data)}")
        
        # Estatísticas
        categories = {}
        for item in output_data:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📈 Distribuição por categoria:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} leiloeiros")
        
        return output_data

def main():
    """Função principal"""
    print("=" * 70)
    print("🏆 SISTEMA DE RANQUEAMENTO DE AUTORIDADE - LEILOEIROS")
    print("=" * 70)
    
    try:
        # Inicializa o ranker em modo demonstração
        ranker = AuctioneerRanker(demo_mode=True)
        
        # Carrega dados
        leiloeiros = ranker.load_leiloeiros()
        if not leiloeiros:
            print("❌ Nenhum leiloeiro para analisar.")
            return
        
        # Analisa todos os leiloeiros
        print("\n" + "-" * 70)
        print("🔬 INICIANDO ANÁLISE DETALHADA (MODO DEMONSTRAÇÃO)")
        print("-" * 70)
        print("📝 Usando dados simulados para mostrar a lógica completa")
        print("🔄 Para análise real, defina demo_mode=False")
        
        results = ranker.analyze_all(leiloeiros)
        
        # Salva resultados
        print("\n" + "-" * 70)
        print("💾 SALVANDO RESULTADOS")
        print("-" * 70)
        
        ranking_data = ranker.save_results(results)
        
        # Mostra top 5
        print("\n" + "=" * 70)
        print("🏅 TOP 5 LEILOEIROS POR AUTORIDADE")
        print("=" * 70)
        
        for i, item in enumerate(ranking_data[:5], 1):
            print(f"\n{i}. {item['nome']}")
            print(f"   Score: {item['score']}/100 | Categoria: {item['category']}")
            print(f"   Site: {item['site']}")
            print(f"   Métricas: Idade={item['metrics']['domain_age'] or 'N/A'} anos, "
                  f"HTTPS={'✓' if item['metrics']['has_https'] else '✗'}, "
                  f"CDN={'✓' if item['metrics']['uses_cdn'] else '✗'}, "
                  f"Redes={item['metrics']['social_count']}")
        
        print("\n" + "=" * 70)
        print("🚀 PRÓXIMOS PASSOS PARA USO REAL:")
        print("=" * 70)
        print("1. Obtenha dados reais de leiloeiros (scraping completo)")
        print("2. Defina demo_mode=False no construtor AuctioneerRanker")
        print("3. Ajuste os timeouts e delays conforme necessário")
        print("4. Monitore possíveis bloqueios por rate limiting")
        print("\n✅ Demonstração concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
