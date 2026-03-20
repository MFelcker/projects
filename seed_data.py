#!/usr/bin/env python3
"""
Script para popular o banco de dados com os dados históricos da empresa.
Execute uma única vez: python seed_data.py
"""
import database as db


def seed():
    db.init_db()

    conn = db.get_connection()
    c = conn.cursor()

    # Verifica se já existem dados
    count = c.execute("SELECT COUNT(*) FROM maquinas").fetchone()[0]
    if count > 0:
        print("Dados já existem no banco. Abortando para evitar duplicação.")
        conn.close()
        return

    # =========================================================================
    # MÁQUINAS
    # =========================================================================
    # Extratora 01: comprada Jul/2025, 12 parcelas de ~R$148.58
    c.execute(
        """INSERT INTO maquinas (nome, data_compra, valor_total, parcelas_total,
           valor_parcela, parcelas_pagas) VALUES (?, ?, ?, ?, ?, ?)""",
        ("Extratora 01", "2025-07-01", 1782.96, 12, 148.58, 9),
    )
    # Extratora 02: comprada Jan/2026, 10 parcelas de R$142.00
    c.execute(
        """INSERT INTO maquinas (nome, data_compra, valor_total, parcelas_total,
           valor_parcela, parcelas_pagas) VALUES (?, ?, ?, ?, ?, ?)""",
        ("Extratora 02", "2026-01-01", 1420.00, 10, 142.00, 3),
    )
    # IDs: Extratora 01 = 1, Extratora 02 = 2

    # Peças padrão para cada máquina
    pecas_padrao = [
        ("Filtro HEPA", 90, 35.0),
        ("Filtro de espuma", 60, 20.0),
        ("Mangueira de sucção", 365, 50.0),
        ("Escova rotativa", 180, 45.0),
        ("Correia", 365, 25.0),
        ("Vedação do reservatório", 365, 30.0),
    ]
    for maq_id in [1, 2]:
        dt = "2025-07-01" if maq_id == 1 else "2026-01-01"
        for nome, vida, custo in pecas_padrao:
            c.execute(
                """INSERT INTO pecas (maquina_id, nome, vida_util_dias,
                   custo_reposicao, data_instalacao, status)
                   VALUES (?, ?, ?, ?, ?, 'ok')""",
                (maq_id, nome, vida, custo, dt),
            )

    # =========================================================================
    # ALUGUÉIS (receitas)
    # Formato: (data, maquina_id, dias, valor_diaria, produto_extra_qtd,
    #           valor_produto_extra, observacoes)
    # =========================================================================
    alugueis = [
        # --- JULHO 2025 ---
        ("2025-07-08", 1, 1, 80, 1, 10, ""),
        ("2025-07-10", 1, 1, 80, 1, 10, ""),
        ("2025-07-11", 1, 1, 80, 0, 0, ""),
        ("2025-07-12", 1, 1, 80, 0, 0, ""),
        ("2025-07-16", 1, 1, 80, 1, 10, ""),
        # --- AGOSTO 2025 ---
        ("2025-08-01", 1, 1, 72, 0, 0, "Valor com desconto"),
        ("2025-08-02", 1, 1, 80, 0, 0, ""),
        ("2025-08-04", 1, 1, 0, 1, 10, "Venda avulsa de produto"),
        ("2025-08-09", 1, 1, 80, 0, 0, ""),
        ("2025-08-16", 1, 1, 80, 0, 0, ""),
        ("2025-08-19", 1, 1, 80, 0, 0, ""),
        ("2025-08-21", 1, 1, 0, 1, 10, "Venda avulsa de produto"),
        ("2025-08-28", 1, 2, 120, 0, 0, ""),
        ("2025-08-31", 1, 1, 0, 1, 15, "Venda avulsa de produto"),
        # --- SETEMBRO 2025 ---
        ("2025-09-12", 1, 1, 80, 2, 30, ""),
        # --- OUTUBRO 2025 ---
        ("2025-10-05", 1, 1, 80, 0, 0, ""),
        ("2025-10-06", 1, 1, 80, 0, 0, ""),
        ("2025-10-19", 1, 1, 80, 0, 0, ""),
        ("2025-10-20", 1, 1, 80, 0, 0, ""),
        ("2025-10-24", 1, 1, 80, 0, 0, ""),
        ("2025-10-25", 1, 1, 80, 1, 15, ""),
        ("2025-10-28", 1, 1, 80, 0, 0, ""),
        ("2025-10-31", 1, 2, 120, 0, 0, ""),
        # --- NOVEMBRO 2025 ---
        ("2025-11-03", 1, 1, 80, 1, 15, ""),
        ("2025-11-08", 1, 1, 80, 0, 0, ""),
        ("2025-11-09", 1, 1, 80, 1, 15, ""),
        ("2025-11-19", 1, 1, 80, 1, 15, ""),
        ("2025-11-23", 1, 1, 140, 1, 15, "Valor especial"),
        ("2025-11-25", 1, 1, 80, 0, 0, ""),
        ("2025-11-26", 1, 1, 80, 0, 0, ""),
        ("2025-11-27", 1, 1, 0, 1, 15, "Venda avulsa de produto"),
        ("2025-11-29", 1, 1, 80, 0, 0, ""),
        ("2025-11-30", 1, 1, 80, 1, 15, ""),
        # --- DEZEMBRO 2025 ---
        ("2025-12-02", 1, 1, 60, 0, 0, ""),
        ("2025-12-06", 1, 1, 80, 1, 15, ""),
        ("2025-12-17", 1, 1, 100, 0, 0, ""),
        ("2025-12-19", 1, 1, 80, 1, 15, ""),
        ("2025-12-19", 1, 1, 80, 0, 0, "2º aluguel do dia"),
        ("2025-12-20", 1, 1, 80, 0, 0, ""),
        ("2025-12-22", 1, 1, 60, 2, 30, ""),
        ("2025-12-22", 1, 1, 60, 1, 15, "2º aluguel do dia"),
        ("2025-12-27", 1, 1, 80, 0, 0, ""),
        ("2025-12-28", 1, 1, 60, 0, 0, ""),
        ("2025-12-28", 1, 1, 60, 0, 0, "2º aluguel do dia"),
        ("2025-12-30", 1, 1, 60, 1, 15, ""),
        ("2025-12-31", 1, 1, 60, 0, 0, ""),
        # --- JANEIRO 2026 ---
        ("2026-01-04", 1, 1, 80, 0, 0, ""),
        ("2026-01-05", 1, 1, 60, 0, 0, ""),
        ("2026-01-07", 1, 1, 150, 1, 15, ""),
        ("2026-01-07", 2, 1, 60, 1, 15, ""),
        ("2026-01-09", 1, 1, 80, 1, 15, ""),
        ("2026-01-11", 1, 1, 80, 0, 0, ""),
        ("2026-01-12", 1, 1, 60, 0, 0, ""),
        ("2026-01-19", 1, 1, 70, 0, 0, ""),
        ("2026-01-25", 1, 1, 80, 1, 15, ""),
        ("2026-01-27", 1, 1, 70, 1, 15, ""),
        ("2026-01-31", 1, 1, 70, 0, 0, ""),
        ("2026-01-31", 2, 1, 80, 0, 0, ""),
        # --- FEVEREIRO 2026 ---
        ("2026-02-06", 1, 1, 70, 0, 0, ""),
        ("2026-02-09", 1, 1, 200, 0, 0, "Serviço especial"),
        ("2026-02-09", 2, 1, 80, 0, 0, ""),
        ("2026-02-09", 1, 1, 70, 0, 0, ""),
        ("2026-02-15", 1, 1, 80, 0, 0, ""),
        ("2026-02-18", 1, 1, 70, 0, 0, ""),
        ("2026-02-20", 1, 2, 120, 0, 0, ""),
        ("2026-02-20", 2, 1, 80, 0, 0, ""),
        ("2026-02-22", 1, 1, 80, 0, 0, ""),
        ("2026-02-28", 1, 1, 157.59, 0, 0, ""),
        # --- MARÇO 2026 ---
        ("2026-03-03", 1, 1, 70, 0, 0, ""),
    ]

    cliente_num = 0
    for data, maq_id, dias, valor, extra_qtd, extra_val, obs in alugueis:
        cliente_num += 1
        valor_total = valor + extra_val
        c.execute(
            """INSERT INTO alugueis (maquina_id, cliente_nome, cliente_telefone,
               data_inicio, dias, valor, produto_extra_qtd, valor_produto_extra,
               valor_total, status, observacoes)
               VALUES (?, ?, '', ?, ?, ?, ?, ?, ?, 'finalizado', ?)""",
            (maq_id, f"Cliente {cliente_num}", data, dias, valor,
             extra_qtd, extra_val, valor_total, obs),
        )

    # =========================================================================
    # DESPESAS
    # Formato: (data, categoria, descricao, valor, maquina_id ou None)
    # =========================================================================
    despesas = [
        # --- JULHO 2025 ---
        ("2025-07-01", "parcela_maquina", "Extratora 01 (1/12)", 148.58, 1),
        # --- AGOSTO 2025 ---
        ("2025-08-01", "parcela_maquina", "Extratora 01 (2/12)", 148.58, 1),
        ("2025-08-01", "produto", "Compra de sabão", 157.52, None),
        ("2025-08-01", "marketing", "Compra de Flyers", 330.81, None),
        ("2025-08-12", "produto", "Compra de sabão", 385.38, None),
        ("2025-08-15", "suprimentos", "Compra de borrifador", 35.00, None),
        # --- SETEMBRO 2025 ---
        ("2025-09-01", "parcela_maquina", "Extratora 01 (3/12)", 148.58, 1),
        # --- OUTUBRO 2025 ---
        ("2025-10-01", "parcela_maquina", "Extratora 01 (4/12)", 148.58, 1),
        ("2025-10-24", "suprimentos", "Compra de borrifador", 30.00, None),
        ("2025-10-28", "manutencao", "Compra de filtro", 79.99, 1),
        # --- NOVEMBRO 2025 ---
        ("2025-11-01", "parcela_maquina", "Extratora 01 (5/12)", 148.58, 1),
        ("2025-11-01", "marketing", "Tráfego", 299.46, None),
        # --- DEZEMBRO 2025 ---
        ("2025-12-01", "parcela_maquina", "Extratora 01 (6/12)", 148.58, 1),
        ("2025-12-01", "marketing", "Tráfego", 56.64, None),
        ("2025-12-07", "suprimentos", "Compra de borrifador", 39.99, None),
        # --- JANEIRO 2026 ---
        ("2026-01-01", "parcela_maquina", "Extratora 01 (7/12)", 148.53, 1),
        ("2026-01-01", "parcela_maquina", "Extratora 02 (1/10)", 142.00, 2),
        ("2026-01-01", "suprimentos", "Borrifadores", 129.31, None),
        ("2026-01-01", "produto", "Produto de limpeza", 78.99, None),
        ("2026-01-01", "suprimentos", "Borrifadores", 55.89, None),
        ("2026-01-01", "produto", "Sabão", 277.43, None),
        ("2026-01-01", "marketing", "Tráfego", 58.00, None),
        ("2026-01-01", "marketing", "Tráfego", 8.25, None),
        ("2026-01-01", "marketing", "Tráfego", 58.00, None),
        ("2026-01-31", "produto", "Compra de sabão", 85.00, None),
        # --- FEVEREIRO 2026 ---
        ("2026-02-01", "parcela_maquina", "Extratora 01 (8/12)", 148.53, 1),
        ("2026-02-01", "parcela_maquina", "Extratora 02 (2/10)", 142.00, 2),
        ("2026-02-01", "marketing", "Tráfego", 10.80, None),
        ("2026-02-01", "marketing", "Tráfego", 66.02, None),
        ("2026-02-01", "marketing", "Tráfego", 54.88, None),
        # --- MARÇO 2026 ---
        ("2026-03-01", "parcela_maquina", "Extratora 01 (9/12)", 148.58, 1),
        ("2026-03-01", "parcela_maquina", "Extratora 02 (3/10)", 142.00, 2),
        ("2026-03-01", "marketing", "Tráfego", 66.06, None),
        ("2026-03-01", "marketing", "Tráfego", 20.26, None),
        ("2026-03-01", "marketing", "Tráfego", 66.02, None),
        ("2026-03-01", "marketing", "Tráfego", 66.05, None),
        ("2026-03-01", "suprimentos", "Adesivos", 42.70, None),
        ("2026-03-01", "produto", "Sabão e Filtro", 818.92, None),
    ]

    for data, cat, desc, valor, maq_id in despesas:
        c.execute(
            """INSERT INTO despesas (data, categoria, descricao, valor, maquina_id)
               VALUES (?, ?, ?, ?, ?)""",
            (data, cat, desc, valor, maq_id),
        )

    conn.commit()
    conn.close()

    # Contagem final
    total_alugueis = len(alugueis)
    total_despesas = len(despesas)
    receita_total = sum(v + ev for _, _, _, v, _, ev, _ in alugueis)
    despesa_total = sum(v for _, _, _, v, _ in despesas)

    print(f"Dados importados com sucesso!")
    print(f"  Máquinas: 2 (Extratora 01 e 02)")
    print(f"  Aluguéis: {total_alugueis} registros (R$ {receita_total:,.2f})")
    print(f"  Despesas: {total_despesas} registros (R$ {despesa_total:,.2f})")
    print(f"  Peças: 12 (6 por máquina)")
    print(f"\nAgora rode: streamlit run app.py")


if __name__ == "__main__":
    seed()
