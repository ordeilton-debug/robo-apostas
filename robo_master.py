# robo_master.py - Sistema Completo Autônomo (Arquivo Único)
import requests
import json
from datetime import datetime

# ================= CONFIGURAÇÕES =================
ODDS_API_KEY = "toa_live_l6296elsleop719g"
TELEGRAM_TOKEN = "8971175524:AAEtdsBH4urEM_n7p7_I4iamWCTfkwMCNlg"
TELEGRAM_CHAT_ID = "205555409"

# Configurações do JSONBin.io
JSONBIN_ID = "6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = "$2a$10$nkhtoMSSze53SGdX4zIyuuG9AQDrgqelRjxIivfNseGcbXi9OLrg6"

REGION = "br,eu"
MARKET = "h2h"
BANCA_INICIAL = 1000.00
FRACAO_KELLY = 0.25      # 25% do Kelly Pleno
LIMIAR_VALOR = 0.03      # 3% de edge mínimo
BASE_URL = "https://api.the-odds-api.com/v4"
# ==================================================

def buscar_odds(esporte: str):
    url = f"{BASE_URL}/sports/{esporte}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal",
    }
    try:
        resposta = requests.get(url, params=params, timeout=15)
        if resposta.status_code != 200:
            print(f"Erro ao buscar odds de {esporte}: {resposta.status_code} - {resposta.text}")
            return []
        return resposta.json()
    except Exception as e:
        print(f"Erro de conexão ao buscar odds: {e}")
        return []

def calcular_criterio_kelly(banca, odd, prob):
    b = odd - 1
    q = 1 - prob
    f_star = (b * prob - q) / b
    if f_star <= 0:
        return 0.0
    return round(banca * f_star * FRACAO_KELLY, 2)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

def salvar_no_jsonbin(nova_aposta):
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_KEY
    }
    
    try:
        resposta_get = requests.get(url, headers=headers)
        dados_atuais = []
        if resposta_get.status_code == 200:
            conteudo = resposta_get.json()
            dados_atuais = conteudo.get("record", [])
            if not isinstance(dados_atuais, list):
                dados_atuais = []
        
        dados_atuais.append(nova_aposta)
        
        resposta_put = requests.put(url, headers=headers, json=dados_atuais)
        if resposta_put.status_code != 200:
            print(f"Erro ao atualizar JSONBin: {resposta_put.status_code} - {resposta_put.text}")
    except Exception as e:
        print(f"Erro de conexão com JSONBin: {e}")

def analisar_e_escanear():
    print("🔍 Buscando odds reais na API...")
    
    esportes = ['soccer_brazil_campeonato']
    
    for esporte in esportes:
        eventos = buscar_odds(esporte)
        if not eventos:
            continue
            
        for evento in eventos:
            partida = f"{evento.get('home_team')} vs {evento.get('away_team')}"
            liga = evento.get('sport_title', esporte)
            
            for bookmaker in evento.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        outcomes = market.get('outcomes', [])
                        if len(outcomes) < 3:
                            continue
                            
                        odds = [o['price'] for o in outcomes]
                        nomes = [o['name'] for o in outcomes]
                        
                        inv_odds = [1/odd for odd in odds]
                        overround = sum(inv_odds)
                        prob_justas = [inv / overround for inv in inv_odds]
                        
                        for i, odd_ofertada in enumerate(odds):
                            prob_justa = prob_justas[i]
                            edge = (prob_justa * odd_ofertada) - 1
                            
                            if edge >= LIMIAR_VALOR:
                                stake = calcular_criterio_kelly(BANCA_INICIAL, odd_ofertada, prob_justa)
                                
                                mensagem = (
                                    f"🚨 *ALERTA DE VALUE BET* 🚨\n\n"
                                    f"🏆 **Liga:** {liga}\n"
                                    f"⚽ **Partida:** {partida}\n"
                                    f"🏛️ **Casa:** {bookmaker['title']}\n"
                                    f"📊 **Seleção:** {nomes[i]}\n"
                                    f"📈 **Odd:** {odd_ofertada}\n"
                                    f"💡 **Edge:** {edge*100:.2f}%\n"
                                    f"💰 **Stake (Kelly):** R$ {stake}"
                                )
                                
                                enviar_telegram(mensagem)
                                
                                registro_aposta = {
                                    "data": str(datetime.now()),
                                    "liga": liga,
                                    "partida": partida,
                                    "casa": bookmaker['title'],
                                    "selecao": nomes[i],
                                    "odd_ofertada": odd_ofertada,
                                    "probabilidade_justa": prob_justa,
                                    "edge": edge,
                                    "stake_sugerida": stake,
                                    "resultado_real": None
                                }
                                
                                salvar_no_jsonbin(registro_aposta)

if __name__ == "__main__":
    analisar_e_escanear()
