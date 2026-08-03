import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def varrer_e_atualizar():
    data_alvo = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 GitHub Action rodando: Buscando partidas do Brasileirão...")
    
    url_alvo = "https://oddsscanner.com/br/futebol/campeonato-brasileiro"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    jogos_do_dia = []

    try:
        response = requests.get(url_alvo, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscando por elementos genéricos de partidas ou links de eventos na página
            # Sites modernos costumam agrupar os jogos em cards ou linhas de tabela
            cards = soup.find_all(['a', 'div'], class_=lambda x: x and ('match' in x.lower() or 'game' in x.lower() or 'event' in x.lower()))
            
            print(f"🔍 Elementos potenciais encontrados: {len(cards)}")
            
            # Tentativa de extrair textos relevantes caso os seletores estejam visíveis no HTML estático
            for card in cards[:30]:  # Limita para evitar duplicadas excessivas
                texto = card.get_text(strip=True)
                if " x " in texto or " vs " in texto:
                    if texto not in jogos_do_dia:
                        jogos_do_dia.append({
                            "data_captura": data_alvo,
                            "confronto_ou_bloco": texto[:100], # Primeiros caracteres do bloco do jogo
                            "fonte": url_alvo
                        })
            
            # Se não achar pelo filtro de texto, garante pelo menos o registro base
            if not jogos_do_dia:
                jogos_do_dia.append({
                    "data_captura": data_alvo,
                    "status": "Página acessada, aguardando renderização dinâmica completa via API",
                    "fonte": url_alvo
                })
                
        else:
            print(f"⚠️ Aviso: Status {response.status_code} ao acessar o site.")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

    # Salva o arquivo JSON atualizado
    nome_arquivo = f"brasileirao_odds_{data_alvo}.json"
    payload = {
        "data_referencia": data_alvo,
        "total_registros": len(jogos_do_dia),
        "partidas": jogos_do_dia,
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    print(f"✅ Arquivo {nome_arquivo} atualizado e salvo com sucesso!")

if __name__ == "__main__":
    varrer_e_atualizar()
