# robo_master.py - Sistema Completo Integrado de Value Betting
import requests
import sqlite3
import pandas as pd
from datetime import datetime

# ================= CONFIGURAÇÕES =================
API_KEY_ODDS = "sua_chave_api_odds_aqui"

# Configurações do Telegram (Chat ID já ajustado com o seu)
TELEGRAM_TOKEN = "COLE_O_TOKEN_DO_BOT_FATHER_AQUI"
TELEGRAM_CHAT_ID = "205555409"

BANCA_INICIAL = 1000.00
FRACAO_KELLY = 0.25      # 25% do Kelly Pleno para segurança
LIMIAR_VALOR = 0.03      # 3% de edge mínimo exigido
DB_NAME = "apostas.db"
# ==================================================

def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_apostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            liga TEXT,
            partida TEXT,
            mercado TEXT,
            odd_ofertada REAL,
            probabilidade_justa REAL,
            edge REAL,
            stake_sugerida REAL,
            resultado_real INTEGER
        )
    """)
    conn.commit()
    conn.close()

def calcular_criterio_kelly(banca, odd, prob):
    b = odd - 1
    q = 1 - prob
    f_star = (b * prob - q) / b
    if f_star <= 0:
        return 0.0
    return round(banca * f_star * FRACAO_KELLY, 2)

def enviar_telegram(mensagem):
    if TELEGRAM_TOKEN == "COLE_O_TOKEN_DO_BOT_FATHER_AQUI":
        print(f"[MODO TESTE - TELEGRAM NÃO CONFIGURADO]\n{mensagem}\n")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

def analisar_e_escanear():
    print("🔍 Escaneando mercado em busca de apostas de valor...")
    
    # Exemplo simulado de aposta analisada (substitua futuramente pela chamada real da API)
    aposta_exemplo = {
        "liga": "Futebol - Rodada",
        "partida": "Time da Casa vs Visitante",
        "mercado": "H2H (1X2)",
        "odd_ofertada": 2.10,
        "probabilidade_justa": 0.52 
    }
    
    edge = (aposta_exemplo["probabilidade_justa"] * aposta_exemplo["odd_ofertada"]) - 1
    
    if edge >= LIMIAR_VALOR:
        stake = calcular_criterio_kelly(BANCA_INICIAL, aposta_exemplo["odd_ofertada"], aposta_exemplo["probabilidade_justa"])
        
        mensagem = (
            f"🚨 *ALERTA DE VALUE BET* 🚨\n\n"
            f"🏆 **Liga:** {aposta_exemplo['liga']}\n"
            f"⚽ **Partida:** {aposta_exemplo['partida']}\n"
            f"📊 **Mercado:** {aposta_exemplo['mercado']}\n"
            f"📈 **Odd:** {aposta_exemplo['odd_ofertada']}\n"
            f"💡 **Edge (Vantagem):** {edge*100:.2f}%\n"
            f"💰 **Stake Sugerida (Kelly):** R$ {stake}"
        )
        
        enviar_telegram(mensagem)
        
        # Salvando no banco de dados SQLite para o Backtesting futuro
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historico_apostas (data, liga, partida, mercado, odd_ofertada, probabilidade_justa, edge, stake_sugerida, resultado_real)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """, (str(datetime.now()), aposta_exemplo['liga'], aposta_exemplo['partida'], aposta_exemplo['mercado'], 
              aposta_exemplo['odd_ofertada'], aposta_exemplo['probabilidade_justa'], edge, stake))
        conn.commit()
        conn.close()

def rodar_backtesting():
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql("SELECT * FROM historico_apostas WHERE resultado_real IS NOT NULL", conn)
    except:
        df = pd.DataFrame()
    conn.close()

    if df.empty:
        print("⚠️ Sem resultados finalizados no banco para calcular o Backtesting.")
        return

    df['lucro'] = df.apply(lambda r: (r['odd_ofertada'] - 1) * r['stake_sugerida'] if r['resultado_real'] == 1 else -r['stake_sugerida'], axis=1)
    roi = (df['lucro'].sum() / df['stake_sugerida'].sum()) * 100
    
    print("="*35)
    print(f"📊 BACKTESTING: {len(df)} apostas validadas.")
    print(f"💵 Lucro Total: R$ {df['lucro'].sum():.2f}")
    print(f"📈 ROI do Sistema: {roi:.2f}%")
    print("="*35)

if __name__ == "__main__":
    inicializar_banco()
    analisar_e_escanear()
    rodar_backtesting()
