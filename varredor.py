import json
from datetime import datetime
import requests

def varrer_e_atualizar():
    data_alvo = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Baixando dados da API...")
    
    url_api = f"https://sports.bzzoiro.com/api/v2/events/?date_from={data_alvo}&date_to={data_alvo}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    payload_final = {}

    try:
        response = requests.get(url_api, headers=headers, timeout=15)
        print(f"📡 Status Code da API: {response.status_code}")
        
        if response.status_code == 200:
            # Salva o conteúdo bruto retornado pela API para inspecionarmos
            payload_final = response.json()
            print("✅ Dados obtidos com sucesso da API!")
        else:
            payload_final = {"erro": f"Status code {response.status_code}", "conteudo": response.text}
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        payload_final = {"erro_excecao": str(e)}

    # Salva exatamente o que a API respondeu no arquivo JSON
    nome_arquivo = f"brasileirao_odds_{data_alvo}.json"
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(payload_final, f, ensure_ascii=False, indent=4)
        
    print(f"📁 Arquivo {nome_arquivo} atualizado com o conteúdo bruto!")

if __name__ == "__main__":
    varrer_e_atualizar()
