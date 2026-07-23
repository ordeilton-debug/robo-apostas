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
data_hoje = datetime.now().strftime("%Y-%m-%d")

try:
  # 1. Pega os dados atuais do Jsonbin
  res_get = requests.get(JSONBIN_URL, headers=headers_jsonbin)
  dados_atuais = res_get.json().get(
      "record", {"historico": [], "banca": 20.82, "greens": 0, "reds": 0}
  )

  banca_atual = float(dados_atuais.get("banca", 20.82))
  greens = int(dados_atuais.get("greens", 0))
  reds = int(dados_atuais.get("reds", 0))

  if "historico" not in dados_atuais:
    dados_atuais["historico"] = []

  partida_encontrada = None
  camp_escolhido = None
  mercado_escolhido = None
  odd_escolhida = None

  # Tenta buscar do Futebol Ao Vivo / Programado
  url_futebol = (
      f"https://free-api-live-football-data.p.rapidapi.com/football-matches-live"
  )
  headers_futebol = {
      "content-type": "application/json",
      "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
      "x-rapidapi-key": RAPID_KEY,
  }

  res_fut = requests.get(url_futebol, headers=headers_futebol)
  if res_fut.status_code == 200:
    conteudo_fut = res_fut.json()
    jogos = conteudo_fut.get("response", [])
    if jogos:
      j = random.choice(jogos)
      camp_escolhido = j.get("league", {}).get("name", "Futebol Profissional")
      home = j.get("homeTeam", {}).get("name", "Equipe Mandante")
      away = j.get("awayTeam", {}).get("name", "Equipe Visitante")
      partida_encontrada = f"{home} x {away}"
      mercado_escolhido = "Mais de 1.5 Gols"
      odd_escolhida = 1.48

  # Se o futebol ao vivo estiver vazio, tenta a API de Basquete com endpoint de jogos por data
  if not partida_encontrada:
    url_basquete = f"https://api-basketball-nba.p.rapidapi.com/games?date={data_hoje}"
    headers_basquete = {
        "content-type": "application/json",
        "x-rapidapi-host": "api-basketball-nba.p.rapidapi.com",
        "x-rapidapi-key": RAPID_KEY,
    }
    res_basq = requests.get(url_basquete, headers=headers_basquete)
    if res_basq.status_code == 200:
      conteudo_basq = res_basq.json()
      jogos_basq = conteudo_basq.get("response", [])
      if jogos_basq:
        jb = random.choice(jogos_basq)
        camp_escolhido = "Basquete 🏀 (NBA / Internacionais)"
        # Extrai os nomes dos times da API de basquete real
        teams = jb.get("teams", {})
        home_b = teams.get("home", {}).get("name", "Mandante NBA")
        away_b = teams.get("away", {}).get("name", "Visitante NBA")
        partida_encontrada = f"{home_b} x {away_b}"
        mercado_escolhido = "Total Mais de 214.5 Pontos"
        odd_escolhida = 1.90

  # Se encontrou partida real em qualquer uma das APIs, registra no painel
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
        f"Sucesso real! Inserido: {partida_encontrada} | Status:"
        f" {res_put.status_code}"
    )
  else:
    print(
        "Nenhum jogo retornado no momento atual pelas APIs. O workflow"
        " encerrou sem inserir dados vazios."
    )

except Exception as e:
  print("Erro na execução:", e)
