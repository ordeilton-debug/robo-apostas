from datetime import datetime
import requests

JSONBIN_URL = "https://api.jsonbin.io/v3/b/6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = "$2a$10$nkhtoMSSze53SGdX4zIyuuG9AQDrgqelRjxIivfNseGcbXi9OLrg6"

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY,
}

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

  # 2. Insere a entrada de teste forçada para validar o painel em tempo real
  nova_aposta = {
      "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "campeonato": "Futebol Internacional (Live Test)",
      "partida": "Test Match FC x Global United",
      "mercado": "Mais de 1.5 Gols",
      "odd": 1.65,
      "status": "APOSTA EM ANDAMENTO",
  }

  dados_atuais["historico"].insert(0, nova_aposta)
  dados_atuais["historico"] = dados_atuais["historico"][:15]

  banca_atual += 1.50
  greens += 1

  dados_atuais["banca"] = round(banca_atual, 2)
  dados_atuais["greens"] = greens
  dados_atuais["reds"] = reds

  # 3. Salva no Jsonbin
  res_put = requests.put(
      JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais
  )
  print(
      "Entrada de teste inserida com sucesso! Status do Jsonbin:"
      f" {res_put.status_code}"
  )

except Exception as e:
  print("Erro ao atualizar o painel:", e)
