import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "extratora.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS maquinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_compra DATE,
            valor_total REAL DEFAULT 0,
            parcelas_total INTEGER DEFAULT 0,
            valor_parcela REAL DEFAULT 0,
            parcelas_pagas INTEGER DEFAULT 0,
            ativa BOOLEAN DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS alugueis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maquina_id INTEGER NOT NULL,
            cliente_nome TEXT NOT NULL,
            cliente_telefone TEXT,
            data_inicio DATE NOT NULL,
            dias INTEGER NOT NULL DEFAULT 1,
            valor REAL NOT NULL,
            produto_extra_qtd INTEGER DEFAULT 0,
            valor_produto_extra REAL DEFAULT 0,
            valor_total REAL NOT NULL,
            status TEXT DEFAULT 'ativo',
            observacoes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
        );

        CREATE TABLE IF NOT EXISTS estoque_movimentacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            aluguel_id INTEGER,
            custo_total REAL,
            observacoes TEXT,
            FOREIGN KEY (aluguel_id) REFERENCES alugueis(id)
        );

        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL,
            maquina_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
        );

        CREATE TABLE IF NOT EXISTS pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maquina_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            vida_util_dias INTEGER NOT NULL,
            custo_reposicao REAL NOT NULL,
            data_instalacao DATE NOT NULL,
            status TEXT DEFAULT 'ok',
            FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
        );

        CREATE TABLE IF NOT EXISTS trocas_pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peca_id INTEGER NOT NULL,
            data_troca DATE NOT NULL,
            custo REAL NOT NULL,
            observacoes TEXT,
            FOREIGN KEY (peca_id) REFERENCES pecas(id)
        );

        CREATE TABLE IF NOT EXISTS redes_sociais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            plataforma TEXT NOT NULL DEFAULT 'instagram',
            seguidores INTEGER DEFAULT 0,
            postagens INTEGER DEFAULT 0,
            curtidas INTEGER DEFAULT 0,
            comentarios INTEGER DEFAULT 0,
            alcance INTEGER DEFAULT 0,
            novos_seguidores INTEGER DEFAULT 0,
            observacoes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


# ==========================================================================
# Máquinas
# ==========================================================================

def listar_maquinas():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM maquinas ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def adicionar_maquina(nome, data_compra=None, valor_total=0, parcelas_total=0,
                      valor_parcela=0, parcelas_pagas=0):
    conn = get_connection()
    conn.execute(
        """INSERT INTO maquinas (nome, data_compra, valor_total, parcelas_total,
           valor_parcela, parcelas_pagas) VALUES (?, ?, ?, ?, ?, ?)""",
        (nome, data_compra, valor_total, parcelas_total, valor_parcela, parcelas_pagas),
    )
    conn.commit()
    conn.close()


def atualizar_maquina(maquina_id, nome, data_compra, valor_total, parcelas_total,
                      valor_parcela, parcelas_pagas):
    conn = get_connection()
    conn.execute(
        """UPDATE maquinas SET nome=?, data_compra=?, valor_total=?, parcelas_total=?,
           valor_parcela=?, parcelas_pagas=? WHERE id=?""",
        (nome, data_compra, valor_total, parcelas_total, valor_parcela, parcelas_pagas, maquina_id),
    )
    conn.commit()
    conn.close()


def atualizar_aluguel(aluguel_id, cliente_nome, cliente_telefone, data_inicio,
                      dias, valor, produto_extra_qtd, observacoes):
    valor_produto_extra = produto_extra_qtd * 15.0
    valor_total = valor + valor_produto_extra
    conn = get_connection()
    conn.execute(
        """UPDATE alugueis SET cliente_nome=?, cliente_telefone=?, data_inicio=?,
           dias=?, valor=?, produto_extra_qtd=?, valor_produto_extra=?,
           valor_total=?, observacoes=? WHERE id=?""",
        (cliente_nome, cliente_telefone, data_inicio, dias, valor,
         produto_extra_qtd, valor_produto_extra, valor_total, observacoes, aluguel_id),
    )
    conn.commit()
    conn.close()


def atualizar_despesa(despesa_id, data, categoria, descricao, valor):
    conn = get_connection()
    conn.execute(
        "UPDATE despesas SET data=?, categoria=?, descricao=?, valor=? WHERE id=?",
        (data, categoria, descricao, valor, despesa_id),
    )
    conn.commit()
    conn.close()


def excluir_despesa(despesa_id):
    conn = get_connection()
    conn.execute("DELETE FROM despesas WHERE id=?", (despesa_id,))
    conn.commit()
    conn.close()


def excluir_aluguel(aluguel_id):
    conn = get_connection()
    conn.execute("DELETE FROM estoque_movimentacao WHERE aluguel_id=?", (aluguel_id,))
    conn.execute("DELETE FROM alugueis WHERE id=?", (aluguel_id,))
    conn.commit()
    conn.close()


# ==========================================================================
# Aluguéis
# ==========================================================================

def registrar_aluguel(maquina_id, cliente_nome, cliente_telefone, data_inicio,
                      dias, produto_extra_qtd, observacoes="", valor_custom=None):
    valor = valor_custom if valor_custom is not None else (80.0 if dias == 1 else 120.0)
    valor_produto_extra = produto_extra_qtd * 15.0
    valor_total = valor + valor_produto_extra
    qtd_produto_saida = 1 + produto_extra_qtd

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO alugueis (maquina_id, cliente_nome, cliente_telefone,
           data_inicio, dias, valor, produto_extra_qtd, valor_produto_extra,
           valor_total, status, observacoes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ativo', ?)""",
        (maquina_id, cliente_nome, cliente_telefone, data_inicio, dias,
         valor, produto_extra_qtd, valor_produto_extra, valor_total, observacoes),
    )
    aluguel_id = cursor.lastrowid
    cursor.execute(
        """INSERT INTO estoque_movimentacao (data, tipo, quantidade, aluguel_id, observacoes)
           VALUES (?, 'saida', ?, ?, ?)""",
        (datetime.now().isoformat(), qtd_produto_saida, aluguel_id,
         f"Aluguel #{aluguel_id} - {cliente_nome}"),
    )
    conn.commit()
    conn.close()
    return aluguel_id


def listar_alugueis(status=None, data_inicio=None, data_fim=None):
    conn = get_connection()
    query = """SELECT a.*, m.nome as maquina_nome FROM alugueis a
               JOIN maquinas m ON a.maquina_id = m.id WHERE 1=1"""
    params = []
    if status:
        query += " AND a.status = ?"
        params.append(status)
    if data_inicio:
        query += " AND a.data_inicio >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND a.data_inicio <= ?"
        params.append(data_fim)
    query += " ORDER BY a.data_inicio DESC, a.id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def finalizar_aluguel(aluguel_id):
    conn = get_connection()
    conn.execute(
        "UPDATE alugueis SET status = 'finalizado' WHERE id = ? AND status = 'ativo'",
        (aluguel_id,),
    )
    conn.commit()
    conn.close()


def cancelar_aluguel(aluguel_id):
    conn = get_connection()
    aluguel = conn.execute(
        "SELECT * FROM alugueis WHERE id = ? AND status = 'ativo'", (aluguel_id,),
    ).fetchone()
    if aluguel:
        qtd_devolver = 1 + aluguel["produto_extra_qtd"]
        conn.execute("UPDATE alugueis SET status = 'cancelado' WHERE id = ?", (aluguel_id,))
        conn.execute(
            """INSERT INTO estoque_movimentacao (data, tipo, quantidade, aluguel_id, observacoes)
               VALUES (?, 'entrada', ?, ?, ?)""",
            (datetime.now().isoformat(), qtd_devolver, aluguel_id,
             f"Cancelamento do aluguel #{aluguel_id}"),
        )
        conn.commit()
    conn.close()


# ==========================================================================
# Estoque
# ==========================================================================

def get_estoque_atual():
    conn = get_connection()
    row = conn.execute("""
        SELECT COALESCE(
            SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE -quantidade END), 0
        ) as total FROM estoque_movimentacao
    """).fetchone()
    conn.close()
    return row["total"]


def registrar_compra_produto(quantidade_litros=5.0):
    unidades = round(quantidade_litros * 2)
    custo = (quantidade_litros / 5) * 90.0

    conn = get_connection()
    conn.execute(
        """INSERT INTO estoque_movimentacao (data, tipo, quantidade, custo_total, observacoes)
           VALUES (?, 'entrada', ?, ?, ?)""",
        (datetime.now().isoformat(), unidades, custo,
         f"Compra de {quantidade_litros:.1f}L de produto"),
    )
    conn.execute(
        """INSERT INTO despesas (data, categoria, descricao, valor)
           VALUES (?, 'produto', ?, ?)""",
        (datetime.now().strftime("%Y-%m-%d"),
         f"Compra de {quantidade_litros:.1f}L de produto de limpeza", custo),
    )
    conn.commit()
    conn.close()


def listar_movimentacoes_estoque(limite=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM estoque_movimentacao ORDER BY data DESC LIMIT ?", (limite,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==========================================================================
# Despesas
# ==========================================================================

def registrar_despesa(data, categoria, descricao, valor, maquina_id=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO despesas (data, categoria, descricao, valor, maquina_id)
           VALUES (?, ?, ?, ?, ?)""",
        (data, categoria, descricao, valor, maquina_id),
    )
    conn.commit()
    conn.close()


def listar_despesas(data_inicio=None, data_fim=None, categoria=None):
    conn = get_connection()
    query = """SELECT d.*, m.nome as maquina_nome
               FROM despesas d LEFT JOIN maquinas m ON d.maquina_id = m.id
               WHERE 1=1"""
    params = []
    if data_inicio:
        query += " AND d.data >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND d.data <= ?"
        params.append(data_fim)
    if categoria:
        query += " AND d.categoria = ?"
        params.append(categoria)
    query += " ORDER BY d.data DESC, d.id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==========================================================================
# Peças / Manutenção
# ==========================================================================

def listar_pecas(maquina_id=None):
    conn = get_connection()
    query = """SELECT p.*, m.nome as maquina_nome
               FROM pecas p JOIN maquinas m ON p.maquina_id = m.id"""
    params = []
    if maquina_id:
        query += " WHERE p.maquina_id = ?"
        params.append(maquina_id)
    query += " ORDER BY p.maquina_id, p.nome"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def adicionar_peca(maquina_id, nome, vida_util_dias, custo_reposicao, data_instalacao):
    conn = get_connection()
    conn.execute(
        """INSERT INTO pecas (maquina_id, nome, vida_util_dias, custo_reposicao,
           data_instalacao, status) VALUES (?, ?, ?, ?, ?, 'ok')""",
        (maquina_id, nome, vida_util_dias, custo_reposicao, data_instalacao),
    )
    conn.commit()
    conn.close()


def registrar_troca_peca(peca_id, data_troca, custo, observacoes=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO trocas_pecas (peca_id, data_troca, custo, observacoes) VALUES (?, ?, ?, ?)",
        (peca_id, data_troca, custo, observacoes),
    )
    conn.execute(
        "UPDATE pecas SET data_instalacao = ?, status = 'ok' WHERE id = ?",
        (data_troca, peca_id),
    )
    peca = conn.execute("SELECT * FROM pecas WHERE id = ?", (peca_id,)).fetchone()
    if peca:
        conn.execute(
            """INSERT INTO despesas (data, categoria, descricao, valor, maquina_id)
               VALUES (?, 'manutencao', ?, ?, ?)""",
            (data_troca, f"Troca de {peca['nome']}", custo, peca["maquina_id"]),
        )
    conn.commit()
    conn.close()


def listar_trocas(peca_id=None):
    conn = get_connection()
    query = """SELECT t.*, p.nome as peca_nome, m.nome as maquina_nome
               FROM trocas_pecas t
               JOIN pecas p ON t.peca_id = p.id
               JOIN maquinas m ON p.maquina_id = m.id"""
    params = []
    if peca_id:
        query += " WHERE t.peca_id = ?"
        params.append(peca_id)
    query += " ORDER BY t.data_troca DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_status_peca(peca):
    data_inst = datetime.strptime(peca["data_instalacao"], "%Y-%m-%d")
    dias_usados = (datetime.now() - data_inst).days
    vida_util = peca["vida_util_dias"]
    percentual = (dias_usados / vida_util * 100) if vida_util > 0 else 100

    if percentual >= 100:
        status = "vencida"
    elif percentual >= 75:
        status = "atencao"
    else:
        status = "ok"

    return {
        "dias_usados": dias_usados,
        "dias_restantes": max(0, vida_util - dias_usados),
        "percentual": min(100, percentual),
        "status": status,
        "data_proxima_troca": (data_inst + timedelta(days=vida_util)).strftime("%Y-%m-%d"),
    }


# ==========================================================================
# Dashboard / Relatórios
# ==========================================================================

def get_resumo_mensal(ano=None, mes=None):
    """Retorna KPIs de um mês. Sem parâmetros = mês atual."""
    conn = get_connection()

    if ano and mes:
        filtro = f"{ano:04d}-{mes:02d}"
    else:
        filtro = datetime.now().strftime("%Y-%m")

    receita = conn.execute(
        """SELECT COALESCE(SUM(valor_total), 0) as total FROM alugueis
           WHERE strftime('%Y-%m', data_inicio) = ? AND status != 'cancelado'""",
        (filtro,),
    ).fetchone()["total"]

    despesas_total = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) as total FROM despesas WHERE strftime('%Y-%m', data) = ?",
        (filtro,),
    ).fetchone()["total"]

    num_alugueis = conn.execute(
        """SELECT COUNT(*) as total FROM alugueis
           WHERE strftime('%Y-%m', data_inicio) = ? AND status != 'cancelado'""",
        (filtro,),
    ).fetchone()["total"]

    conn.close()

    lucro = receita - despesas_total
    return {
        "receita": receita,
        "despesas": despesas_total,
        "lucro": lucro,
        "num_alugueis": num_alugueis,
        "ticket_medio": receita / num_alugueis if num_alugueis > 0 else 0,
        "margem": (lucro / receita * 100) if receita > 0 else 0,
    }


def get_historico_mensal(meses=12):
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', data_inicio) as mes,
               SUM(valor_total) as receita,
               COUNT(*) as num_alugueis
        FROM alugueis WHERE status != 'cancelado'
        GROUP BY mes ORDER BY mes DESC LIMIT ?
    """, (meses,)).fetchall()

    despesas_rows = conn.execute("""
        SELECT strftime('%Y-%m', data) as mes, SUM(valor) as total
        FROM despesas GROUP BY mes ORDER BY mes DESC LIMIT ?
    """, (meses,)).fetchall()
    conn.close()

    despesas_map = {r["mes"]: r["total"] for r in despesas_rows}
    resultado = []
    for r in reversed(list(rows)):
        mes = r["mes"]
        receita = r["receita"]
        despesa = despesas_map.get(mes, 0)
        resultado.append({
            "mes": mes,
            "receita": receita,
            "despesas": despesa,
            "lucro": receita - despesa,
            "num_alugueis": r["num_alugueis"],
        })
    return resultado


def get_despesas_por_categoria(data_inicio=None, data_fim=None):
    conn = get_connection()
    query = "SELECT categoria, SUM(valor) as total FROM despesas WHERE 1=1"
    params = []
    if data_inicio:
        query += " AND data >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim)
    query += " GROUP BY categoria ORDER BY total DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ==========================================================================
# Redes Sociais
# ==========================================================================

def registrar_rede_social(data, plataforma, seguidores, postagens, curtidas,
                          comentarios, alcance, novos_seguidores, observacoes=""):
    conn = get_connection()
    conn.execute(
        """INSERT INTO redes_sociais (data, plataforma, seguidores, postagens,
           curtidas, comentarios, alcance, novos_seguidores, observacoes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data, plataforma, seguidores, postagens, curtidas, comentarios,
         alcance, novos_seguidores, observacoes),
    )
    conn.commit()
    conn.close()


def listar_redes_sociais(plataforma=None, data_inicio=None, data_fim=None):
    conn = get_connection()
    query = "SELECT * FROM redes_sociais WHERE 1=1"
    params = []
    if plataforma:
        query += " AND plataforma = ?"
        params.append(plataforma)
    if data_inicio:
        query += " AND data >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim)
    query += " ORDER BY data DESC, id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_rede_social(registro_id, data, seguidores, postagens, curtidas,
                          comentarios, alcance, novos_seguidores, observacoes):
    conn = get_connection()
    conn.execute(
        """UPDATE redes_sociais SET data=?, seguidores=?, postagens=?, curtidas=?,
           comentarios=?, alcance=?, novos_seguidores=?, observacoes=? WHERE id=?""",
        (data, seguidores, postagens, curtidas, comentarios, alcance,
         novos_seguidores, observacoes, registro_id),
    )
    conn.commit()
    conn.close()


def excluir_rede_social(registro_id):
    conn = get_connection()
    conn.execute("DELETE FROM redes_sociais WHERE id=?", (registro_id,))
    conn.commit()
    conn.close()


# ==========================================================================
# Consultas para Visão Geral / Home
# ==========================================================================

def get_alugueis_ativos():
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.*, m.nome as maquina_nome FROM alugueis a
           JOIN maquinas m ON a.maquina_id = m.id
           WHERE a.status = 'ativo' ORDER BY a.data_inicio DESC""",
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_roi_por_maquina():
    conn = get_connection()
    rows = conn.execute("""
        SELECT m.id, m.nome, m.valor_total as custo_maquina,
               m.parcelas_pagas * m.valor_parcela as total_pago,
               COALESCE(SUM(CASE WHEN a.status != 'cancelado' THEN a.valor_total ELSE 0 END), 0) as receita_gerada,
               COUNT(CASE WHEN a.status != 'cancelado' THEN 1 END) as total_alugueis,
               COALESCE(desp.total_despesas, 0) as despesas_associadas
        FROM maquinas m
        LEFT JOIN alugueis a ON a.maquina_id = m.id
        LEFT JOIN (
            SELECT maquina_id, SUM(valor) as total_despesas
            FROM despesas WHERE maquina_id IS NOT NULL
            GROUP BY maquina_id
        ) desp ON desp.maquina_id = m.id
        GROUP BY m.id
        ORDER BY receita_gerada DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_clientes(limite=10):
    conn = get_connection()
    rows = conn.execute("""
        SELECT cliente_nome,
               cliente_telefone,
               COUNT(*) as total_alugueis,
               SUM(CASE WHEN status != 'cancelado' THEN valor_total ELSE 0 END) as receita_total,
               MAX(data_inicio) as ultimo_aluguel,
               ROUND(AVG(CASE WHEN status != 'cancelado' THEN valor_total END), 2) as ticket_medio
        FROM alugueis
        GROUP BY LOWER(TRIM(cliente_nome))
        ORDER BY total_alugueis DESC, receita_total DESC
        LIMIT ?
    """, (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_receita_por_maquina_mensal():
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', a.data_inicio) as mes,
               m.nome as maquina,
               SUM(a.valor_total) as receita
        FROM alugueis a JOIN maquinas m ON a.maquina_id = m.id
        WHERE a.status != 'cancelado'
        GROUP BY mes, m.nome
        ORDER BY mes
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dias_semana_populares():
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            CASE CAST(strftime('%w', data_inicio) AS INTEGER)
                WHEN 0 THEN 'Domingo'
                WHEN 1 THEN 'Segunda'
                WHEN 2 THEN 'Terça'
                WHEN 3 THEN 'Quarta'
                WHEN 4 THEN 'Quinta'
                WHEN 5 THEN 'Sexta'
                WHEN 6 THEN 'Sábado'
            END as dia_semana,
            CAST(strftime('%w', data_inicio) AS INTEGER) as dia_num,
            COUNT(*) as total
        FROM alugueis WHERE status != 'cancelado'
        GROUP BY dia_num
        ORDER BY dia_num
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
