import json
from datetime import datetime
import requests

def varrer_e_atualizar():
    data_alvo = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Buscando dados direto da API oficial do site...")
    
    # URL da API de eventos por data (exemplo para hoje)
    url_api = f"https://sports.bzzoiro.com/api/v2/events/?date_from={data_alvo}&date_to={data_alvo}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    jogos_do_dia = []

    try:
        response = requests.get(url_api, headers=headers, timeout=15)
        if response.status_code == 200:
            dados = response.json()
            
            # Aqui você varre a lista de eventos que a API devolve
            # (Ajuste a chave 'results' ou 'data' conforme a estrutura exata do JSON que a API retornar)
            eventos = dados.get("results", dados) if isinstance(dados, dict) else dados
            
            for evento in eventos:
                jogos_do_dia.append({
                    "data_captura": data_alvo,
                    "confronto": evento, # ou os campos específicos como time da casa e visitante
                    "fonte": url_api
                })
            print(f"✅ Sucesso! Total de registros obtidos: {len(jogos_do_dia)}")
        else:
            print(f"⚠️ Erro na API: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

    # Salva o JSON final
    nome_arquivo = f"brasileirao_odds_{data_alvo}.json"
    payload = {
        "data_referencia": data_alvo,
        "total_registros": len(jogos_do_dia),
        "partidas": jogos_do_dia,
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    print(f"📁 Arquivo {nome_arquivo} atualizado com sucesso!")

if __name__ == "__main__":
    varrer_e_atualizar()
