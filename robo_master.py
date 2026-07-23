import json
import random
from datetime import datetime
import urllib.request
import urllib.error

# Suas credenciais do JSONBin.io
BIN_ID = "6a6166c2f5f4af5e29b36f8c"
API_KEY = "$2a$10$nkhtoMSSze53SGdX4zIyuuG9AQDrgqelRjxIivfNseGcbXi9OLrg6"

class RoboJSONBin:
    def __init__(self):
        self.carregar_da_nuvem()

    def carregar_da_nuvem(self):
        """Baixa os dados atuais direto do JSONBin.io"""
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
        headers = {
            "X-Master-Key": API_KEY
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                resposta_completa = json.loads(response.read().decode())
                # O JSONBin guarda os dados reais dentro da chave 'record'
                dados = resposta_completa.get("record", {})
                
                self.banca = dados.get("banca", 20.00)
                self.stake = dados.get("stake", 1.00)
                self.historico = dados.get("historico", [])
                self.mercados_stats = dados.get("mercados_stats", {
                    "Mais de 1.5 Gols": {"tentativas": 0, "acertos": 0, "ativo": True},
                    "Escanteios (Mais de 8.5)": {"tentativas": 0, "acertos": 0, "ativo": True},
                    "Vitória (Moneyline)": {"tentativas": 0, "acertos": 0, "ativo": True}
                })
                print("☁️ [NUVEM] Dados carregados com sucesso do JSONBin!")
        except Exception as e:
            print(f"⚠️ Erro ao carregar da nuvem: {e}. Usando padrão local.")
            self.banca = 20.00
            self.stake = 1.00
            self.historico = []
            self.mercados_stats = {
                "Mais de 1.5 Gols": {"tentativas": 0, "acertos": 0, "ativo": True},
                "Escanteios (Mais de 8.5)": {"tentativas": 0, "acertos": 0, "ativo": True},
                "Vitória (Moneyline)": {"tentativas": 0, "acertos": 0, "ativo": True}
            }

    def salvar_na_nuvem(self):
        """Envia e atualiza os dados salvos direto para o JSONBin.io"""
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": API_KEY
        }
        dados = {
            "banca": self.banca,
            "stake": self.stake,
            "historico": self.historico,
            "mercados_stats": self.mercados_stats
        }
        try:
            payload = json.dumps(dados).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
            with urllib.request.urlopen(req) as response:
                print("☁️ [NUVEM] Estatísticas atualizadas e salvas no JSONBin com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao salvar na nuvem: {e}")

    def varrer_mercados_ao_vivo(self):
        partidas_disponiveis = [
            ("Futebol", "Flamengo x Fluminense", "Mais de 1.5 Gols"),
            ("Futebol", "Real Madrid x Sevilla", "Mais de 1.5 Gols"),
            ("Basquete", "Golden State x Bulls", "Vitória (Moneyline)"),
            ("Futebol", "Arsenal x Chelsea", "Escanteios (Mais de 8.5)")
        ]
        esporte, partida, mercado = random.choice(partidas_disponiveis)
        odd_capturada = round(random.uniform(1.30, 1.55), 2)
        return esporte, partida, mercado, odd_capturada

    def executar_ciclo_completo(self):
        esporte, partida, mercado, odd = self.varrer_mercados_ao_vivo()

        if not self.mercados_stats.get(mercado, {}).get("ativo", True):
            print(f"🚫 [BLOQUEADO] O mercado '{mercado}' está pausado.")
            return

        print(f"✅ [OPORTUNIDADE] {partida} | {mercado} | Odd: {odd}")

        acertou = random.random() < 0.75
        self.mercados_stats[mercado]["tentativas"] += 1

        if acertou:
            self.mercados_stats[mercado]["acertos"] += 1
            self.banca += self.stake * odd
            status = "GREEN"
        else:
            self.banca -= self.stake
            status = "RED"

        self.historico.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "esporte": esporte,
            "partida": partida,
            "mercado": mercado,
            "odd": odd,
            "stake": self.stake,
            "status": status
        })

        # Salva automaticamente na nuvem a cada ciclo
        self.salvar_na_nuvem()

    def atualizar_painel_html(self):
        total_op = len(self.historico)
        greens = sum(1 for op in self.historico if op["status"] == "GREEN")
        win_rate = (greens / total_op * 100) if total_op > 0 else 0
        lucro = self.banca - 20.00
        percentual_lucro = (lucro / 20.00) * 100 if 20.00 > 0 else 0

        linhas_tabela = ""
        for op in reversed(self.historico):
            badge_class = "badge-green" if op["status"] == "GREEN" else "badge-red"
            linhas_tabela += f"""
                <tr>
                    <td>{op['data']}</td>
                    <td>{op['esporte']}</td>
                    <td>{op['partida']}</td>
                    <td>{op['mercado']}</td>
                    <td>{op['odd']}</td>
                    <td>R$ {op['stake']:.2f}</td>
                    <td><span class="{badge_class}">{op['status']}</span></td>
                </tr>
            """

        html_conteudo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Painel - Robô Quantitativo Nuvem</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 30px; }}
        h1 {{ color: #3b82f6; margin-bottom: 25px; }}
        .cards-container {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .card {{ background-color: #1e293b; padding: 20px; border-radius: 12px; flex: 1; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-left: 4px solid #3b82f6; }}
        .card h3 {{ color: #94a3b8; font-size: 14px; margin-bottom: 8px; }}
        .card p {{ font-size: 26px; font-weight: bold; margin: 0; }}
        table {{ width: 100%; border-collapse: collapse; background-color: #1e293b; border-radius: 12px; overflow: hidden; }}
        th, td {{ padding: 15px; border-bottom: 1px solid #334155; text-align: left; }}
        th {{ background-color: #1e293b; color: #94a3b8; font-size: 14px; text-transform: uppercase; }}
        .badge-green {{ background-color: rgba(34, 197, 94, 0.2); color: #22c55e; padding: 6px 12px; border-radius: 6px; font-weight: bold; }}
        .badge-red {{ background-color: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 6px 12px; border-radius: 6px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🤖 Painel de Controle - Robô Varredor (Integrado com JSONBin)</h1>
    <div class="cards-container">
        <div class="card">
            <h3>BANCA VIRTUAL ATUAL</h3>
            <p>R$ {self.banca:.2f}</p>
        </div>
        <div class="card" style="border-left-color: #22c55e;">
            <h3>LUCRO LÍQUIDO</h3>
            <p style="color: #22c55e;">+R$ {lucro:.2f} ({percentual_lucro:+.1f}%)</p>
        </div>
        <div class="card" style="border-left-color: #eab308;">
            <h3>TAXA DE ACERTO (WINRATE)</h3>
            <p>{win_rate:.1f}%</p>
        </div>
        <div class="card" style="border-left-color: #a855f7;">
            <h3>TOTAL DE ENTRADAS</h3>
            <p>{total_op} Op.</p>
        </div>
    </div>
    
    <h2 style="color: #f8fafc; font-size: 20px; margin-bottom: 15px;">Histórico de Operações na Nuvem</h2>
    <table>
        <tr>
            <th>Data/Hora</th>
            <th>Esporte</th>
            <th>Partida</th>
            <th>Mercado</th>
            <th>Odd</th>
            <th>Stake</th>
            <th>Status</th>
        </tr>
        {linhas_tabela}
    </table>
</body>
</html>
"""
        with open("dashboard_robo.html", "w", encoding="utf-8") as f:
            f.write(html_conteudo)

if __name__ == "__main__":
    robo = RoboJSONBin()
    # Executa 3 novas entradas e já sincroniza com o JSONBin
    for _ in range(3):
        robo.executar_ciclo_completo()
    
    robo.atualizar_painel_html()
    print("Processo concluído! Dados salvos na nuvem e painel HTML atualizado.")