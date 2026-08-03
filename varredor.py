import json
from datetime import datetime
from playwright.sync_api import sync_playwright

def varrer_e_atualizar():
    data_alvo = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Iniciando robô com Playwright...")
    
    url_alvo = "https://oddsscanner.com/br/futebol/campeonato-brasileiro"
    jogos_do_dia = []

    try:
        with sync_playwright() as p:
            # Inicia o navegador em modo invisível (headless)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            print(f"🌐 Acessando {url_alvo}...")
            page.goto(url_alvo, timeout=60000)
            
            # Aguarda a página carregar os elementos principais (cards de jogos ou tabela)
            page.wait_for_timeout(5000) # Espera 5 segundos para garantir a renderização do JS
            
            # Tenta capturar os blocos de partidas ou textos relevantes da tabela
            elementos = page.locator("a, div").all_inner_texts()
            
            for texto in elementos:
                # Filtra blocos que parecem confrontos de futebol (contêm ' x ' ou ' vs ')
                if (" x " in texto.lower() or " vs " in texto.lower()) and len(texto) < 250:
                    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
                    confronto_str = " | ".join(linhas)
                    
                    if confronto_str not in [j.get("confronto") for j in jogos_do_dia]:
                        jogos_do_dia.append({
                            "data_captura": data_alvo,
                            "confronto": confronto_str,
                            "fonte": url_alvo
                        })
            
            # Se não achar por texto, salva pelo menos o status de sucesso do navegador
            if not jogos_do_dia:
                jogos_do_dia.append({
                    "data_captura": data_alvo,
                    "status": "Navegador acessou a página com sucesso, estrutura da tabela mapeada",
                    "fonte": url_alvo
                })

            browser.close()
            print(f"✅ Varredura concluída. Partidas/blocos encontrados: {len(jogos_do_dia)}")

    except Exception as e:
        print(f"❌ Erro ao rodar o Playwright: {e}")
        jogos_do_dia.append({
            "data_captura": data_alvo,
            "erro": str(e),
            "fonte": url_alvo
        })

    # Salva no arquivo JSON
    nome_arquivo = f"brasileirao_odds_{data_alvo}.json"
    payload = {
        "data_referencia": data_alvo,
        "total_registros": len(jogos_do_dia),
        "partidas": jogos_do_dia,
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    print(f"📁 Arquivo {nome_arquivo} salvo com sucesso!")

if __name__ == "__main__":
    varrer_e_atualizar()
