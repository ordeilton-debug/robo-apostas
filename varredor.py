import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def varrer_e_atualizar():
    data_alvo = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 GitHub Action rodando: Varrendo odds para {data_alvo}...")
    
    # Substitua abaixo pela URL real do site que você deseja varrer
    url_alvo = f"https://exemplo-site-esportes.com/jogos?data={data_alvo}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    jogos_do_dia = []

    try:
        response = requests.get(url_alvo, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards_partidas = soup.find_all("div", class_="match-item-row")
            
            for item in cards_partidas:
                horario = item.find("span", class_="match-time").text.strip() if item.find("span", class_="match-time") else "00:00"
                mandante = item.find("span", class_="home-team").text.strip()
                visitante = item.find("span", class_="away-team").text.strip()
                
                odd_casa = item.find("span", class_="odd-home").text.strip() if item.find("span", class_="odd-home") else "-"
                odd_empate = item.find("span", class_="odd-draw").text.strip() if item.find("span", class_="odd-draw") else "-"
                odd_fora = item.find("span", class_="odd-away").text.strip() if item.find("span", class_="odd-away") else "-"
                
                gols_over = item.find("span", class_="odds-over-goals").text.strip() if item.find("span", class_="odds-over-goals") else "-"
                escanteios_over = item.find("span", class_="odds-over-corners").text.strip() if item.find("span", class_="odds-over-corners") else "-"

                partida_obj = {
                    "data_partida": data_alvo,
                    "horario": horario,
                    "confronto": f"{mandante} vs {visitante}",
                    "mercados": {
                        "match_odds_1x2": {"casa": odd_casa, "empate": odd_empate, "fora": odd_fora},
                        "gols_mais_2_5": gols_over,
                        "escanteios_mais_9_5": escanteios_over
                    }
                }
                jogos_do_dia.append(partida_obj)
        else:
            print(f"⚠️ Aviso: Status {response.status_code} ao acessar o site. Gerando JSON base...")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}. Gerando JSON base...")

    # Garante que o arquivo JSON sempre será criado/atualizado para evitar o erro do Git
    nome_arquivo = f"jogos_{data_alvo}.json"
    payload = {
        "data_referencia": data_alvo,
        "total_jogos": len(jogos_do_dia),
        "partidas": jogos_do_dia,
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    print(f"✅ Arquivo {nome_arquivo} salvo com sucesso!")

if __name__ == "__main__":
    varrer_e_atualizar()
