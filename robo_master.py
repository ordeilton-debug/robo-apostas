# calibrar.py (Sugestão de melhoria)
import sqlite3
import pandas as pd
from database import DB_NAME

def analisar_desempenho_historico():
    conn = sqlite3.connect(DB_NAME)
    # Supondo que você salve as apostas analisadas, odds, probabilidade estimada e se bateu (1 ou 0)
    query = """
        SELECT data, liga, mercado, odd_ofertada, probabilidade_justa, 
               (probabilidade_justa * odd_ofertada - 1) as edge_teorico, 
               resultado_real 
        FROM historico_apostas 
        WHERE resultado_real IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        print("Ainda não há dados suficientes no banco para backtesting.")
        return

    # Calculando o ROI geral e por faixa de odds
    df['lucro_prejuizo'] = df.apply(
        lambda row: (row['odd_ofertada'] - 1) if row['resultado_real'] == 1 else -1, 
        axis=1
    )
    
    roi_total = (df['lucro_prejuizo'].sum() / len(df)) * 100
    print(f"Total de apostas analisadas: {len(df)}")
    print(f"ROI Geral do Sistema: {roi_total:.2f}%")
    
    return df

if __name__ == "__main__":
    analisar_desempenho_historico()
