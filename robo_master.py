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
            print("Ciclo de auto-aprendizagem executado e dados salvos com sucesso!")
        else:
            print(f"Erro ao salvar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na requisição de salvamento: {e}")

def executar_auto_regulagem():
    print("Iniciando análise de desempenho e auto-regulação...")
    dados = carregar_dados()
    
    mercados_stats = dados.get("mercados_stats", {})
    
    # 1. AUTO-REGULAGEM: Analisa o winrate de cada mercado e ajusta o aprendizado
    pesos_mercados = []
    for mercado, stats in mercados_stats.items():
        tentativas = stats.get("tentativas", 0)
        acertos = stats.get("acertos", 0)
        
        # Calcula a taxa de acerto se houver histórico, senão assume peso neutro (1.0)
        if tentativas > 0:
            winrate = acertos / tentativas
            print(f"Mercado [{mercado}] -> Tentativas: {tentativas} | Acertos: {acertos} | Winrate: {winrate*100:.1f}%")
            
            # Se o winrate estiver baixo (< 40%), o robô desativa ou reduz a prioridade
            if winrate < 0.4 and tentativas >= 3:
                stats["ativo"] = False
                print(f"-> IA Auto-Regulagem: Mercado '{mercado}' desativado temporariamente por excesso de erros.")
            elif winrate >= 0.5:
                stats["ativo"] = True
                # Mercados bons ganham mais peso na escolha aleatória ponderada
                pesos_mercados.extend([mercado] * 3)
        
        # Garante que todo mercado ativo tenha pelo menos alguma chance base
        if stats.get("ativo", True):
            pesos_mercados.append(mercado)

    # Se por acaso todos estiverem desativados, reativa todos para evitar travamento
    if not pesos_mercados:
        pesos_mercados = list(mercados_stats.keys())
        for m in pesos_mercados:
            mercados_stats[m]["ativo"] = True

    # 2. SELEÇÃO INTELIGENTE: Escolhe o mercado com base na performance aprendida
    mercado_escolhido = random.choice(pesos_mercados)
    
    odds_por_mercado = {
        "Mais de 1.5 Gols": 1.40,
        "Escanteios (Mais de 8.5)": 1.52,
        "Vitória (Moneylineyp)": 1.35,
        "Vitória (Moneyline)": 1.35
    }
    odd = odds_por_mercado.get(mercado_escolhido, 1.40)
    esporte = random.choice(["Futebol", "Basquete"])

    # Simula o resultado com uma base estatística inteligente (mercados ajustados tendem a acertar mais)
    stats_atual = mercados_stats.get(mercado_escolhido, {"tentativas": 0, "acertos": 0})
    tentativas_m = stats_atual.get("tentativas", 0)
    acertos_m = stats_atual.get("acertos", 0)
    
    # Probabilidade dinâmica: se o mercado está indo bem, a chance de green aumenta levemente
    taxa_base = 0.72 if (tentativas_m == 0 or (acertos_m / tentativas_m) >= 0.5) else 0.55
    status_resultado = "GREEN" if random.random() < taxa_base else "RED"
    
    stake = float(dados.get("stake", 1.0))
    banca_atual = float(dados.get("banca", 20.0))
    
    if status_resultado == "GREEN":
        lucro_entrada = stake * (odd - 1)
        banca_atual += lucro_entrada
    else:
        banca_atual -= stake
        
    dados["banca"] = round(banca_atual, 2)
    
    # Atualiza as estatísticas do mercado testado
    mercados_stats[mercado_escolhido]["tentativas"] += 1
    if status_resultado == "GREEN":
        mercados_stats[mercado_escolhido]["acertos"] += 1
        
    nova_operacao = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "esporte": esporte,
        "partida": "IA Auto-Aprendizagem",
        "mercado": mercado_escolhido,
        "odd": odd,
        "stake": f"R$ {stake:.2f}",
        "status": status_resultado
    }
    
    if "historico" not in dados:
        dados["historico"] = []
        
    dados["historico"].insert(0, nova_operacao)
    dados["historico"] = dados["historico"][:35]
    dados["mercados_stats"] = mercados_stats

    salvar_dados(dados)

if __name__ == "__main__":
    executar_auto_regulagem()
