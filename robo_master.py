import requests
import random
from datetime import datetime

# Configurações do seu JSONBin
BIN_ID = "6a6166c2f5f4af5e29b36f8c"
MASTER_KEY = "$2a$10$nkhtoMSSze53SGdX4zIyuuG9AQDrgqelRjxIivfNseGcbXi9OLrg6"

def carregar_dados():
    url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
    headers = {
        'X-Master-Key': MASTER_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('record', {})
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
    
    return {
        "banca": 20.0,
        "stake": 1.0,
        "historico": [],
        "mercados_stats": {
            "Mais de 1.5 Gols": {"tentativas": 0, "acertos": 0, "ativo": True},
            "Escanteios (Mais de 8.5)": {"tentativas": 0, "acertos": 0, "ativo": True},
            "Vitória (Moneyline)": {"tentativas": 0, "acertos": 0, "ativo": True}
        }
    }

def salvar_dados(dados):
    url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': MASTER_KEY
    }
    try:
        response = requests.put(url, json=dados, headers=headers)
        if response.status_code == 200:
            print("Varredura concluída: Entrada realizada e dados atualizados no JSONBin!")
        else:
            print(f"Erro ao salvar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na requisição de salvamento: {e}")

def executar_varredura():
    print("Iniciando varredura de mercados...")
    dados = carregar_dados()
    
    # Simula a varredura: 80% de chance de encontrar uma oportunidade válida neste ciclo de 5 minutos
    encontrou_oportunidade = random.random() < 0.8
    
    if not encontrou_oportunidade:
        print("Varredura finalizada: Nenhuma oportunidade com o padrão ideal encontrada neste ciclo.")
        return

    esportes = ["Futebol", "Basquete"]
    mercados_opcoes = [
        ("Mais de 1.5 Gols", 1.40),
        ("Escanteios (Mais de 8.5)", 1.52),
        ("Vitória (Moneyline)", 1.35)
    ]
    
    esporte = random.choice(esportes)
    mercado_nome, odd = random.choice(mercados_opcoes)
    
    # Simula o resultado da aposta baseada na estratégia quantitativa
    status_resultado = "GREEN" if random.random() < 0.72 else "RED"
    stake = float(dados.get("stake", 1.0))
    
    banca_atual = float(dados.get("banca", 20.0))
    if status_resultado == "GREEN":
        lucro_entrada = stake * (odd - 1)
        banca_atual += lucro_entrada
    else:
        banca_atual -= stake
        
    dados["banca"] = round(banca_atual, 2)
    
    nova_operacao = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "esporte": esporte,
        "partida": "Varredura Automática IA",
        "mercado": mercado_nome,
        "odd": odd,
        "stake": f"R$ {stake:.2f}",
        "status": status_resultado
    }
    
    if "historico" not in dados:
        dados["historico"] = []
        
    dados["historico"].insert(0, nova_operacao)
    dados["historico"] = dados["historico"][:25] # Mantém os últimos 25 registros
    
    if mercado_nome in dados["mercados_stats"]:
        dados["mercados_stats"][mercado_nome]["tentativas"] += 1
        if status_resultado == "GREEN":
            dados["mercados_stats"][mercado_nome]["acertos"] += 1

    salvar_dados(dados)

if __name__ == "__main__":
    executar_varredura()
