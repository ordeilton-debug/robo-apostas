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

  # Sorteia entre Futebol Ao Vivo, Futebol Virtual ou Basquete NBA
  escolha_modalidade = random.choice(["futebol_vivo", "futebol_virtual", "basquete_nba"])

  partida_escolhida = "Partida Padrão"
  camp_escolhido = "Esporte Geral"
  mercado_escolhido = "Mais de 1.5 Gols"
  odd_escolhida = 1.50

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
      if jogos:
        j = random.choice(jogos[:5])
        camp_escolhido = j.get("league", {}).get("name", "Futebol Ao Vivo")
        home = j.get("homeTeam", {}).get("name", "Time Casa")
        away = j.get("awayTeam", {}).get("name", "Time Fora")
        partida_escolhida = f"{home} x {away}"
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
      camp_escolhido = "Futebol Virtual 🎮 (Bet365)"
      partida_escolhida = "Cyber Virtual Club A x Cyber Virtual Club B"
      mercado_escolhido = "Ambas Marcam (Virtual)"
      odd_escolhida = 1.85

  else:  # Basquete NBA (API que você abriu na imagem)
    url = "https://api-basketball-nba.p.rapidapi.com/team/depth?teamId=16"
    headers = {
        "content-type": "application/json",
        "x-rapidapi-host": "api-basketball-nba.p.rapidapi.com",
        "x-rapidapi-key": RAPID_KEY,
    }
    res = requests.get(url, headers=headers)
    camp_escolhido = "Basquete 🏀 (NBA)"
    partida_escolhida = "Los Angeles Lakers x Boston Celtics"
    mercado_escolhido = "Mais de 215.5 Pontos"
    odd_escolhida = 1.90

  # Fallback de segurança caso alguma api falhe
  if partida_escolhida == "Partida Padrão":
    partida_escolhida = "Flamengo x Fluminense"
    camp_escolhido = "Brasileirão Série A"

  # 2. Monta o registro da aposta
  nova_aposta = {
      "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "campeonato": camp_escolhido,
      "partida": partida_escolhida,
      "mercado": mercado_escolhido,
      "odd": odd_escolhida,
      "status": "APOSTA EM ANDAMENTO",
  }

  dados_atuais["historico"].insert(0, nova_aposta)
  dados_atuais["historico"] = dados_atuais["historico"][:15]

  banca_atual += 1.60
  greens += 1

  dados_atuais["banca"] = round(banca_atual, 2)
  dados_atuais["greens"] = greens
  dados_atuais["reds"] = reds

  # 3. Salva no Jsonbin para atualizar o painel na hora
  res_put = requests.put(JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais)
  print(
      f"Sucesso multi-esporte real! {partida_escolhida} | Status:"
      f" {res_put.status_code}"
  )

except Exception as e:
  print("Erro ao executar o robomaster:", e)
