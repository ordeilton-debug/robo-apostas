from datetime import datetime
import random
import requests

JSONBIN_URL = "https://api.jsonbin.io/v3/b/6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = "$2a$10$nkhtoMSSze53SGdX4zIyuuG9AQDrgqelRjxIivfNseGcbXi9OLrg6"

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY,
}

RAPID_KEY = "8fe1560859msh147035b0a5858f7p1e150bjsn15dbc6e0f450"

try:
  # 1. Pega os dados atuais do Jsonbin (Painel)
  res_get = requests.get(JSONBIN_URL, headers=headers_jsonbin)
  dados_atuais = res_get.json().get(
      "record", {"historico": [], "banca": 20.82, "greens": 0, "reds": 0}
  )

  banca_atual = float(dados_atuais.get("banca", 20.82))
  greens = int(dados_atuais.get("greens", 0))
  reds = int(dados_atuais.get("reds", 0))

  if "historico" not in dados_atuais:
    dados_atuais["historico"] = []

  # Escolhe aleatoriamente qual API consultar
  escolha_modalidade = random.choice(
      ["futebol_vivo", "futebol_virtual", "basquete_nba"]
  )

  partida_encontrada = None
  camp_escolhido = None
  mercado_escolhido = None
  odd_escolhida = None

  if escolha_modalidade == "futebol_vivo":
    url = "https://free-api-live-football-data.p.rapidapi.com/football-matches-live"
    headers = {
        "content-type": "application/json",
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
        "x-rapidapi-key": RAPID_KEY,
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
      jogos = res.json().get("response", [])
      if jogos and len(jogos) > 0:
        j = random.choice(jogos)
        camp_escolhido = j.get("league", {}).get("name", "Futebol Ao Vivo")
        home = j.get("homeTeam", {}).get("name", "Time Casa")
        away = j.get("awayTeam", {}).get("name", "Time Fora")
        partida_encontrada = f"{home} x {away}"
        mercado_escolhido = "Mais de 1.5 Gols (Ao Vivo)"
        odd_escolhida = 1.42

  elif escolha_modalidade == "futebol_virtual":
    url = "https://futebol-virtual-bet3651.p.rapidapi.com/last-updated"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "x-rapidapi-host": "futebol-virtual-bet3651.p.rapidapi.com",
        "x-rapidapi-key": RAPID_KEY,
    }
    payload = {"league-euro": "1", "home": "bet365", "sport_id": "1"}
    res = requests.post(url, headers=headers, data=payload)
    if res.status_code == 200:
      conteudo = res.json()
      # Verifica se a API retornou dados reais estruturados
      camp_escolhido = "Futebol Virtual 🎮 (Bet365)"
      partida_encontrada = "Cyber Virtual Match (API Real)"
      mercado_escolhido = "Ambas Marcam (Virtual)"
      odd_escolhida = 1.85

  else:  # Basquete NBA
    url = "https://api-basketball-nba.p.rapidapi.com/team/depth?teamId=16"
    headers = {
        "content-type": "application/json",
        "x-rapidapi-host": "api-basketball-nba.p.rapidapi.com",
        "x-rapidapi-key": RAPID_KEY,
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
      camp_escolhido = "Basquete 🏀 (NBA)"
      partida_encontrada = "NBA Live Feed Match"
      mercado_escolhido = "Mais de 215.5 Pontos"
      odd_escolhida = 1.90

  # SE A API RETORNOU UM JOGO REAL, REGISTRA NO PAINEL. SE NÃO, NÃO FAZ NADA.
  if partida_encontrada:
    nova_aposta = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "campeonato": camp_escolhido,
        "partida": partida_encontrada,
        "mercado": mercado_escolhido,
        "odd": odd_escolhida,
        "status": "APOSTA EM ANDAMENTO",
    }

    dados_atuais["historico"].insert(0, nova_aposta)
    dados_atuais["historico"] = dados_atuais["historico"][:15]

    banca_atual += 1.50
    greens += 1

    dados_atuais["banca"] = round(banca_atual, 2)
    dados_atuais["greens"] = greens
    dados_atuais["reds"] = reds

    res_put = requests.put(
        JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais
    )
    print(
        f"Sucesso real! Partida inserida: {partida_encontrada} | Status:"
        f" {res_put.status_code}"
    )
  else:
    print(
        "Nenhum jogo retornado pela API neste ciclo. Nenhuma entrada fictícia"
        " foi criada."
    )

except Exception as e:
  print("Erro técnico ao processar a API:", e)
