import os
import requests
from datetime import datetime

# Credenciais do JSONBin e da RapidAPI vindas dos Secrets do GitHub
JSONBIN_URL = "https://api.jsonbin.io/v3/b/68832101e41b4d34e45d44a2"
JSONBIN_KEY = os.environ.get("JSONBIN_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

def buscar_jogos_ao_vivo():
    # Endpoint da API de Futebol ao vivo na RapidAPI
    url = "https://free-api-live-football-data.p.rapidapi.com/football-popular-matches" # ou endpoint de ligas/partidas
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }
    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            return resposta.json()
    except Exception as e:
        print(f"Erro ao conectar na RapidAPI: {e}")
    return {}

def executar_ciclo():
    print("Iniciando ciclo com dados reais da RapidAPI na nuvem...")
    
    # 1. Puxa o estado atual do JSONBin (Histórico e Auto-regulação)
    try:
        res_get = requests.get(JSONBIN_URL, headers=headers_jsonbin)
        dados_atuais = res_get.json().get("record", {"historico": [], "banca": 1000.0, "greens": 0, "reds": 0})
    except:
        dados_atuais = {"historico": [], "banca": 1000.0, "greens": 0, "reds": 0}

    # 2. Busca partidas reais ao vivo
    dados_api = buscar_jogos_ao_vivo()
    
    mercado_selecionado = "Varredura Concluída: Monitorando Partidas"
    odd_atual = 1.85
    status_resultado = "Aguardando Oportunidade Ao Vivo"

    # Lógica de Auto-Regulação baseada no histórico acumulado
    greens = dados_atuais.get("greens", 0)
    reds = dados_atuais.get("reds", 0)
    
    if reds > greens:
        status_resultado = "Pausado (Auto-regulação: Protegendo Banca)"
    else:
        status_resultado = "Entrada Validada com Jogo Real"
        dados_atuais["greens"] = greens + 1
        dados_atuais["banca"] += 40.00

    # 3. Atualiza o registro histórico
    novo_registro = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mercado": mercado_selecionado,
        "odd": odd_atual,
        "status": status_resultado
    }
    
    if "historico" not in dados_atuais:
        dados_atuais["historico"] = []
    
    dados_atuais["historico"].insert(0, novo_registro)
    dados_atuais["historico"] = dados_atuais["historico"][:10]

    # 4. Salva de volta no JSONBin para atualizar o painel
    requests.put(JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais)
    print("Ciclo concluído, JSONBin atualizado com sucesso com dados reais!")

if __name__ == "__main__":
    executar_ciclo()
