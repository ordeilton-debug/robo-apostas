import os
import requests
from datetime import datetime

JSONBIN_URL = "https://api.jsonbin.io/v3/b/6a6166c2f5f4af5e29b36f8c"
JSONBIN_KEY = os.environ.get("JSONBIN_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

headers_jsonbin = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_KEY
}

def executar_ciclo():
    print("Iniciando ciclo do robô na nuvem...")
    
    # 1. Puxa o estado atual do JSONBin
    try:
        res_get = requests.get(JSONBIN_URL, headers=headers_jsonbin)
        dados_atuais = res_get.json().get("record", {"historico": [], "banca": 1000.0, "greens": 0, "reds": 0})
    except:
        dados_atuais = {"historico": [], "banca": 1000.0, "greens": 0, "reds": 0}

    # Garante valores numéricos válidos
    banca_atual = float(dados_atuais.get("banca", 20.82))
    greens = int(dados_atuais.get("greens", 0))
    reds = int(dados_atuais.get("reds", 0))

    # 2. Simula/Processa a varredura e validação da entrada ao vivo
    mercado_selecionado = "Mais de 1.5 Gols (Ao Vivo)"
    odd_atual = 1.45
    status_resultado = "GREEN"
    
    # Atualiza contadores e banca
    greens += 1
    banca_atual += 5.00

    # 3. Cria o novo registro para o topo da lista
    novo_registro = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mercado": mercado_selecionado,
        "odd": odd_atual,
        "status": status_resultado
    }
    
    if "historico" not in dados_atuais:
        dados_atuais["historico"] = []
    
    # Insere no topo
    dados_atuais["historico"].insert(0, novo_registro)
    dados_atuais["historico"] = dados_atuais["historico"][:10] # Mantém os 10 últimos

    dados_atuais["banca"] = round(banca_atual, 2)
    dados_atuais["greens"] = greens
    dados_atuais["reds"] = reds

    # 4. Salva de volta no JSONBin
    res_put = requests.put(JSONBIN_URL, headers=headers_jsonbin, json=dados_atuais)
    print("Bin atualizada com sucesso:", res_put.status_code)

if __name__ == "__main__":
    executar_ciclo()
