import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def varrer_e_atualizar():
    data_alvo = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 GitHub Action rodando: Varrendo o Campeonato Brasileiro na Odds Scanner...")
    
    # URL do Brasileirão na Odds Scanner
    url_alvo = "https://oddsscanner.com/br/futebol/campeonato-brasileiro"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    jogos_do_dia = []

    try:
        response = requests.get(url_alvo, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            print("✅ Página do Brasileirão acessada com sucesso!")
            
            # Registro base do rastreio da competição
            competicao_obj = {
                "data_captura": data_alvo,
                "campeonato": "Campeonato Brasileiro",
                "fonte": url_alvo,
                "status": "Varredura da página principal realizada com sucesso"
            }
            jogos_do_dia.append(competicao_obj)
        else:
            print(f"⚠️ Aviso: Status {response.status_code} ao acessar o site.")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

    # Salva o arquivo JSON com os dados do Brasileirão
    nome_arquivo = f"brasileirao_odds_{data_alvo}.json"
    payload = {
        "data_referencia": data_alvo,
        "total_registros": len(jogos_do_dia),
        "partidas": jogos_do_dia,
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    print(f"✅ Arquivo {nome_arquivo} salvo com sucesso!")

if __name__ == "__main__":
    varrer_e_atualizar()
