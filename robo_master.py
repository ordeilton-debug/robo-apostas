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
    
    # Retorno padrão caso falhe a leitura
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
            print("Dados atualizados com sucesso no JSONBin!")
        else:
            print(f"Erro ao salvar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na requisição de salvamento: {e}")

def executar_ciclo():
    dados = carregar_dados()
    
    # Dados da nova simulação de entrada
    esportes = ["Futebol", "Basquete"]
    mercados_opcoes = [
        ("Mais de 1.5 Gols", 1.42),
        ("Escanteios (Mais de 8.5)", 1.50),
        ("Vitória (Moneyline)", 1.35)
    ]
    
    esporte = random.choice(esportes)
    mercado_nome, odd = random.choice(mercados_opcoes)
    
    # Simulando resultado (70% de chance de GREEN para testes consistentes)
    status_resultado = "GREEN" if random.random() < 0.7 else "RED"
    stake = float(dados.get("stake", 1.0))
    
    banca_atual = float(dados.get("banca", 20.0))
    if status_resultado == "GREEN":
        lucro_entrada = stake * (odd - 1)
        banca_atual += lucro_entrada
    else:
        banca_atual -= stake
        
    dados["banca"] = round(banca_atual, 2)
    
    # Criando nova operação para o histórico
    nova_operacao = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "esporte": esporte,
        "partida": "Simulação Automatizada IA",
        "mercado": mercado_nome,
        "odd": odd,
        "stake": f"R$ {stake:.2f}",
        "status": status_resultado
    }
    
    if "historico" not in dados:
        dados["historico"] = []
        
    # Adiciona no topo da lista e mantém no máximo os últimos 20 registros
    dados["historico"].insert(0, nova_operacao)
    dados["historico"] = dados["historico"][:20]
    
    # Atualiza estatísticas do mercado
    if mercado_nome in dados["mercados_stats"]:
        dados["mercados_stats"][mercado_nome]["tentativas"] += 1
        if status_resultado == "GREEN":
            dados["mercados_stats"][mercado_nome]["acertos"] += 1

    # Salva na nuvem
    salvar_dados(dados)

if __name__ == "__main__":
    print("Iniciando execução do robô...")
    executar_ciclo()