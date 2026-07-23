import os
import requests
from datetime import datetime, timedelta

JSONBIN_URL = "https://api.jsonbin.io/v3/b/6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = os.environ.get("JSONBIN_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

def executar_ciclo():
    print("Iniciando ciclo do robô (Gerando lote de 3 apostas)...")
    
    # 1. Puxa o estado atual do JSONBin
    try:
        res_get = requests.get(JSONBIN_URL, headers=headers_jsonbin)
        dados_atuais = res_get.json().get("record", {"historico": [], "banca": 1000.0, "greens": 0, "reds": 0})
    except:
        dados_atuais = {"historico": [], "banca": 1000.0, "greens": 0, "reds": 0}

    banca_atual = float(dados_atuais.get("banca", 25.82))
    greens = int(dados_atuais.get("greens", 0))
    reds = int(dados_atuais.get("reds", 0))
    
    if "historico" not in dados_atuais:
        dados_atuais["historico"] = []

    # Lista de mercados para variar nas 3 apostas
    mercados_possiveis = [
        ("Mais de 1.5 Gols (Ao Vivo)", 1.42, "GREEN"),
        ("Ambas Marcam (Sim)", 1.75, "GREEN"),
        ("Menos de 3.5 Gols", 1.30, "GREEN"),
        ("Vitória Simples Favorito", 1.55, "GREEN")
    ]

    # 2. Gera exatamente 3 apostas neste ciclo
    novas_entradas = []
    for i in range(3):
        # Desloca o horário em alguns segundos para a listagem ficar bonita no painel
        horario_aposta = datetime.now() - timedelta(seconds=(3 - i) * 10)
        
        mercado, odd, status = mercados_possiveis[i % len(mercados_possiveis)]
        
        novas_entradas.insert(0, {
            "data": horario_aposta.strftime("%Y-%m-%d %H:%M:%S"),
            "mercado": mercado,
            "odd": odd,
            "status": status
        })
        
        greens += 1
        banca_atual += 4.50

    # Adiciona as 3 novas entradas no topo do histórico existente
    dados_atuais["historico"] = novas_entradas + dados_atuais["historico"]
    
    # Mantém apenas as últimas 15 entradas para não pesar o painel
    dados_atuais["historico"] = dados_atuais["historico"][:15]

    dados_atuais["banca"] = round(banca_atual, 2)
    dados_atuais["greens"] = greens
    dados_atuais["reds"] = reds

    # 3. Salva de volta no JSONBin
    res_put = requests.put(JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais)
    print("Lote de 3 apostas enviado com sucesso! Status:", res_put.status_code)

if __name__ == "__main__":
    executar_ciclo()
