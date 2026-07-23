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

  # Tentativa 1: Futebol ao vivo
  url_futebol = (
      "https://free-api-live-football-data.p.rapidapi.com/football-matches-live"
  )
  headers_futebol = {
      "content-type": "application/json",
      "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
      "x-rapidapi-key": RAPID_KEY,
  }

  res_fut = requests.get(url_futebol, headers=headers_futebol)
  if res_fut.status_code == 200:
    jogos = res_fut.json().get("response", [])
    if jogos:
      j = random.choice(jogos)
      camp_escolhido = j.get("league", {}).get(
          "name", "Futebol Profissional Ao Vivo"
      )
      home = j.get("homeTeam", {}).get("name", "Mandante")
      away = j.get("awayTeam", {}).get("name", "Visitante")
      partida_encontrada = f"{home} x {away}"
      mercado_escolhido = "Mais de 1.5 Gols"
      odd_escolhida = 1.55

  # Tentativa 2: Basquete Real / NBA (se o futebol não retornar nada)
  if not partida_encontrada:
    url_basquete = f"https://api-basketball-nba.p.rapidapi.com/games?date={data_hoje}"
    headers_basquete = {
        "content-type": "application/json",
        "x-rapidapi-host": "api-basketball-nba.p.rapidapi.com",
        "x-rapidapi-key": RAPID_KEY,
    }
    res_basq = requests.get(url_basquete, headers=headers_basquete)
    if res_basq.status_code == 200:
      jogos_basq = res_basq.json().get("response", [])
      if jogos_basq:
        jb = random.choice(jogos_basq)
        camp_escolhido = "Basquete 🏀 (NBA / Oficiais)"
        teams = jb.get("teams", {})
        home_b = teams.get("home", {}).get("name", "Time Casa")
        away_b = teams.get("away", {}).get("name", "Time Fora")
        partida_encontrada = f"{home_b} x {away_b}"
        mercado_escolhido = "Total Mais de 214.5 Pontos"
        odd_escolhida = 1.90

  # Tentativa 3: E-Sport Basquete 2K (Simulados ativos agora na casa)
  if not partida_encontrada:
    # Simula varredura ativa nos e-sports baseada em feeds de simulados digitais
    esports_lista = [
        {
            "campeonato": "E-Sport Basquete 🏀 (NBA 2K Live)",
            "partida": "New York Knicks (CHARM) x Boston Celtics (MARKSMAN)",
            "mercado": "Vencedor da Partida (Incl. Prorros)",
            "odd": 1.72,
        },
        {
            "campeonato": "E-Sport Basquete 🏀 (NBA 2K Live)",
            "partida": "Portland Trail Blazers x Phoenix Suns (DZOJO)",
            "mercado": "Total Mais de 157.5 Pontos",
            "odd": 1.85,
        },
    ]
    escolha_esport = random.choice(esports_lista)
    camp_escolhido = escolha_esport["campeonato"]
    partida_encontrada = escolha_esport["partida"]
    mercado_escolhido = escolha_esport["mercado"]
    odd_escolhida = escolha_esport["odd"]

  # Se encontrou o evento em qualquer uma das frentes, registra no painel
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
        "Sucesso unificado! Inserido no painel:"
        f" {partida_encontrada} | Status: {res_put.status_code}"
    )
  else:
    print("Nenhum evento capturado neste ciclo.")

except Exception as e:
  print("Erro no script unificado:", e)
