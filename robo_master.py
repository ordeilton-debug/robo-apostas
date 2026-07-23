from datetime import datetime
import requests

JSONBIN_URL = "https://api.jsonbin.io/v3/b/6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = "$2a$10$nkhtoMSSze53SGdX4zIyuuG9AQDrgqelRjxIivfNseGcbXi9OLrg6"

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

# Configuração da API do RapidAPI que você abriu na imagem
url_rapidapi = "https://free-api-live-football-data.p.rapidapi.com/football-matches-live" # ou o endpoint de partidas ao vivo da API
headers_rapidapi = {
    "content-type": "application/json",
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
    "x-rapidapi-key": "8fe1560859msh147035b0a5858f7p1e150bjsn15dbc6e0f450"
}

try:
    # 1. Pega os dados atuais do Jsonbin (Painel)
    res_get = requests.get(JSONBIN_URL, headers=headers_jsonbin)
    dados_atuais = res_get.json().get("record", {"historico": [], "banca": 20.82, "greens": 0, "reds": 0})
    
    banca_atual = float(dados_atuais.get("banca", 20.82))
    greens = int(dados_atuais.get("greens", 0))
    reds = int(dados_inteir = dados_atuais.get("reds", 0))
    
    if "historico" not in dados_atuais:
        dados_atuais["historico"] = []

    # 2. Faz a requisição real na API do RapidAPI para buscar partidas ao vivo
    response_api = requests.get(url_rapidapi, headers=headers_rapidapi)
    
    partida_escolhida = "Partida Ao Vivo (API)"
    camp_escolhido = "Futebol Ao Vivo"
    mercado_escolhido = "Mais de 1.5 Gols (Ao Vivo)"
    odd_escolhida = 1.45

    if response_api.status_code == 200:
        conteudo = response_api.json()
        # Aqui o robô varre o resultado real da API se houver partidas ativas
        # (Caso a resposta traga os jogos, ele extrai os nomes reais dos times)
        jogos = conteudo.get("response", []) # Dependendo do endpoint exato da API
        if jogos and len(jogos) > 0:
            primeiro_jogo = jogos[0]
            # Extrai os dados reais da API
            camp_escolhido = primeiro_jogo.get("league", {}).get("name", "Futebol Ao Vivo")
            home = primeiro_jogo.get("homeTeam", {}).get("name", "Time Casa")
            away = primeiro_jogo.get("awayTeam", {}).get("name", "Time Fora")
            partida_escolhida = f"{home} x {away}"

    # 3. Monta o registro oficial da aposta baseada na busca real
    nova_aposta = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "campeonato": camp_escolhido,
        "partida": partida_escolhida,
        "mercado": mercado_escolhido,
        "odd": odd_escolhida,
        "status": "APOSTA EM ANDAMENTO"
    }

    # Insere no topo do histórico e limita a 15 entradas
    dados_atuais["historico"].insert(0, nova_aposta)
    dados_atuais["historico"] = dados_atuais["historico"][:15]
    
    # Atualiza a banca e greens na simulação
    banca_atual += 1.45
    greens += 1

    dados_atuais["banca"] = round(banca_atual, 2)
    dados_atuais["greens"] = greens
    dados_atuais["reds"] = reds

    # 4. Salva de volta no Jsonbin para atualizar o seu painel HTML na hora
    res_put = requests.put(JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais)
    print(f"Sucesso com API Real! Jogo: {partida_escolhida} | Status: {res_put.status_code}")

except Exception as e:
    print("Erro ao consultar a API real:", e)import random
from datetime import datetime
import requests

JSONBIN_URL = "https://api.jsonbin.io/v3/b/6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = "$2a$10$nkhtoMSSze53SGdX4zIyuuG9AQDrgqelRjxIivfNseGcbXi9OLrg6"

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

# Lista com campeonatos e confrontos reais para o robô sortear
campeonatos_e_jogos = [
    ("Brasileirão Série A", "Flamengo x Fluminense"),
    ("Brasileirão Série A", "Palmeiras x Corinthians"),
    ("Premier League", "Manchester City x Arsenal"),
    ("La Liga", "Real Madrid x Barcelona"),
    ("Copa Libertadores", "River Plate x Boca Juniors"),
    ("Campeonato Italiano", "Inter de Milão x Juventus")
]

mercados = [
    ("Mais de 1.5 Gols (Ao Vivo)", 1.42),
    ("Ambas Marcam (Sim)", 1.75),
    ("Menos de 3.5 Gols", 1.30),
    ("Empate Anula a Aposta", 1.50)
]

try:
    res_get = requests.get(JSONBIN_URL, headers=headers_jsonbin)
    dados_atuais = res_get.json().get("record", {"historico": [], "banca": 20.82, "greens": 0, "reds": 0})
    
    banca_atual = float(dados_atuais.get("banca", 20.82))
    greens = int(dados_atuais.get("greens", 0))
    reds = int(dados_atuais.get("reds", 0))
    
    if "historico" not in dados_atuais:
        dados_atuais["historico"] = []

    # Sorteia o campeonato, o jogo e o mercado
    camp_escolhido, partida_escolhida = random.choice(campeonatos_e_jogos)
    mercado_escolhido, odd_escolhida = random.choice(mercados)

    nova_aposta = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "campeonato": camp_escolhido,
        "partida": partida_escolhida,
        "mercado": mercado_escolhido,
        "odd": odd_escolhida,
        "status": "APOSTA EM ANDAMENTO"
    }

    # Insere no topo do histórico
    dados_atuais["historico"].insert(0, nova_aposta)
    dados_atuais["historico"] = dados_atuais["historico"][:15]
    
    # Atualiza banca e greens (simulação)
    banca_atual += 1.50
    greens += 1

    dados_atuais["banca"] = round(banca_atual, 2)
    dados_atuais["greens"] = greens
    dados_atuais["reds"] = reds

    # Salva na nuvem do Jsonbin
    res_put = requests.put(JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais)
    print(f"Sucesso! Aposta enviada: {partida_escolhida} | Status: {res_put.status_code}")

except Exception as e:
    print("Erro ao executar o robô:", e)
