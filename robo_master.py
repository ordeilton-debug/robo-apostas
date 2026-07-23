# robo_unico.py - Robô Profissional de Value Bets (Versão Nuvem GitHub)
import os
import sqlite3
import requests
from datetime import datetime

# ================= CONFIGURAÇÕES =================
ODDS_API_KEY = "toa_live_l6296elsleop719g"
TELEGRAM_TOKEN = "8971175524:AAEtdsBH4urEM_n7p7_I4iamWCTfkwMCNlg"
TELEGRAM_CHAT_ID = "1430032505"

BANCA = 1000.00
EDGE_MINIMO = 0.03          # 3% de edge mínimo
KELLY_FRACAO = 0.25         # 25% do Kelly Pleno
ODD_MINIMA = 1.70
ODD_MAXIMA = 5.00

BASE_URL = "https://api.the-odds-api.com/v4"
REGIONS = "br,eu"
MARKETS = "h2h"

# Ligas completas com foco em Futebol e principais mercados
ESPORTES = [
    "soccer_brazil_campeonato",
    "soccer_brazil_serie_b",
    "soccer_conmebol_copa_libertadores",
    "soccer_conmebol_copa_sudamericana",
    "soccer_uefa_champions_league",
    "soccer_england_premier_league",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
    "basketball_nba",
    "esports_counter_strike"
]

DB_NAME = "apostas.db"
# ==================================================

def inicializar_banco():
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas_enviados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_unico TEXT UNIQUE,
            data_envio TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_value (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida TEXT,
            liga TEXT,
            casa TEXT,
            selecao TEXT,
            odd REAL,
            edge REAL,
            stake REAL,
            data_registro TEXT
        )
    """)
    conexao.commit()
    conexao.close()

def verificar_alerta_enviado(hash_unico):
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("SELECT id FROM alertas_enviados WHERE hash_unico = ?", (hash_unico,))
    resultado = cursor.fetchone()
    conexao.close()
    return resultado is not None

def registrar_alerta(hash_unico):
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("INSERT OR IGNORE INTO alertas_enviados (hash_unico, data_envio) VALUES (?, ?)", 
                   (hash_unico, str(datetime.now())))
    conexao.commit()
    conexao.close()

def salvar_historico(partida, liga, casa, selecao, odd, edge, stake):
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO historico_value (partida, liga, casa, selecao, odd, edge, stake, data_registro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (partida, liga, casa, selecao, odd, edge, stake, str(datetime.now())))
    conexao.commit()
    conexao.close()

def buscar_eventos(esporte):
    url = f"{BASE_URL}/sports/{esporte}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "decimal"
    }
    try:
        resposta = requests.get(url, params=params, timeout=15)
        if resposta.status_code != 200:
            return []
        return resposta.json()
    except Exception as e:
        print(f"Erro ao buscar eventos para {esporte}: {e}")
        return []

def calcular_consenso_mercado(bookmakers):
    prob_soma = {}
    contagem = {}

    for casa in bookmakers:
        for market in casa.get("markets", []):
            if market["key"] != "h2h":
                continue
            for outcome in market["outcomes"]:
                nome = outcome["name"]
                odd = outcome["price"]
                if odd <= 1:
                    continue
                p = 1 / odd
                prob_soma[nome] = prob_soma.get(nome, 0) + p
                contagem[nome] = contagem.get(nome, 0) + 1

    probabilidades_justas = {}
    for nome in prob_soma:
        if contagem[nome] > 0:
            probabilidades_justas[nome] = prob_soma[nome] / contagem[nome]

    return probabilidades_justas

def encontrar_melhor_odd(bookmakers):
    melhores = {}

    for casa in bookmakers:
        casa_nome = casa.get("title")
        for market in casa.get("markets", []):
            if market["key"] != "h2h":
                continue
            for outcome in market["outcomes"]:
                nome = outcome["name"]
                odd = outcome["price"]
                
                if not (ODD_MINIMA <= odd <= ODD_MAXIMA):
                    continue

                if nome not in melhores or odd > melhores[nome]["odd"]:
                    melhores[nome] = {"odd": odd, "casa": casa_nome}

    return melhores

def analisar_value_bets(bookmakers, edge_minimo):
    probs = calcular_consenso_mercado(bookmakers)
    melhores_odds = encontrar_melhor_odd(bookmakers)
    values = []

    for selecao, dados in melhores_odds.items():
        if selecao not in probs:
            continue
            
        prob_justa = probs[selecao]
        odd_ofertada = dados["odd"]
        casa = dados["casa"]

        edge = (prob_justa * odd_ofertada) - 1

        if edge >= edge_minimo:
            values.append({
                "selecao": selecao,
                "odd": odd_ofertada,
                "casa": casa,
                "prob_justa": prob_justa,
                "edge": edge
            })

    return values

def calcular_kelly(odd, prob_justa):
    b = odd - 1
    q = 1 - prob_justa
    f_star = ((b * prob_justa) - q) / b
    
    if f_star <= 0:
        return 0.0
        
    stake = BANCA * f_star * KELLY_FRACAO
    return round(stake, 2)

def enviar_alerta_telegram(partida, liga, casa, selecao, odd, prob_justa, edge, stake):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    mensagem = (
        f"🚨 *VALUE BET ENCONTRADA* 🚨\n\n"
        f"⚽/🏀/🎮 *{partida}*\n"
        f"🏆 *Liga:* {liga}\n\n"
        f"📍 *Casa:* {casa}\n"
        f"🎯 *Seleção:* {selecao}\n"
        f"📈 *Odd Ofertada:* {odd}\n"
        f"💹 *Mercado Justo:* {1/prob_justa:.2f}\n"
        f"🔥 *Edge:* {edge*100:.2f}%\n"
        f"💰 *Stake (Kelly):* R$ {stake:.2f}"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

def executar():
    print("🤖 Iniciando varredura automatizada...")
    inicializar_banco()
    
    total = 0
    for esporte in ESPORTES:
        print(f"Varrendo: {esporte}")
        eventos = buscar_eventos(esporte)
        
        for evento in eventos:
            partida = f"{evento.get('home_team')} x {evento.get('away_team')}"
            liga = evento.get('sport_title', esporte)
            bookmakers = evento.get("bookmakers", [])
            
            if not bookmakers:
                continue
                
            values = analisar_value_bets(bookmakers, EDGE_MINIMO)
            
            for v in values:
                selecao = v["selecao"]
                odd = v["odd"]
                casa = v["casa"]
                edge = v["edge"]
                prob_justa = v["prob_justa"]
                
                hash_unico = f"{partida}_{selecao}_{casa}".replace(" ", "_").lower()
                
                if verificar_alerta_enviado(hash_unico):
                    continue
                
                stake = calcular_kelly(odd, prob_justa)
                if stake <= 0:
                    continue
                
                registrar_alerta(hash_unico)
                salvar_historico(partida, liga, casa, selecao, odd, edge, stake)
                enviar_alerta_telegram(partida, liga, casa, selecao, odd, prob_justa, edge, stake)
                
                print(f"[ENCONTRADO] {partida} | {selecao} @ {odd} ({casa}) -> Edge: {edge*100:.2f}%")
                total += 1

    print(f"Varredura finalizada. Alertas enviados: {total}")

if __name__ == "__main__":
    executar()
