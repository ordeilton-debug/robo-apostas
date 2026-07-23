import os
import requests
from datetime import datetime, timedelta

JSONBIN_URL = "https://api.jsonbin.io/v3/b/6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = os.environ.get("JSONBIN_KEY")

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

def executar_ciclo():
    print("Iniciando ciclo do robô (Enviando apostas em andamento)...")
    
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

    mercados_possiveis = [
        ("Mais de 1.5 Gols (Ao Vivo)", 1.42),
        ("Ambas Marcam (Sim)", 1.75),
        ("Menos de 3.5 Gols", 1.30)
    ]

    novas_entradas = []
    for i in range(3):
        horario_aposta = datetime.now() - timedelta(seconds=(3 - i) * 10)
        mercado, odd = mercados_possiveis[i % len(mercados_possiveis)]
        
        # AGORA ELE MANDA O STATUS DE ANDAMENTO
        novas_entradas.insert(0, {
            "data": horario_aposta.strftime("%Y-%m-%d %H:%M:%S"),
            "mercado": mercado,
            "odd": odd,
            "status": "APOSTA EM ANDAMENTO"
        })

    dados_atuais["historico"] = novas_entradas + dados_atuais["historico"]
    dados_atuais["historico"] = dados_atuais["historico"][:15]

    dados_atuais["banca"] = round(banca_atual, 2)
    dados_atuais["greens"] = greens
    dados_atuais["reds"] = reds

    res_put = requests.put(JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais)
    print("Status atualizado na bin:", res_put.status_code)

if __name__ == "__main__":
    executar_ciclo()
