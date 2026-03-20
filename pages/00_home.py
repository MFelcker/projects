import streamlit as st
from datetime import datetime
import database as db

st.title("Visão Geral")

now = datetime.now()
st.caption(f"{now.strftime('%A, %d/%m/%Y').capitalize()}")

# ---------------------------------------------------------------------------
# KPIs do mês atual
# ---------------------------------------------------------------------------
resumo = db.get_resumo_mensal()
mes_label = now.strftime("%B/%Y").capitalize()

st.subheader(f"Resultados — {mes_label}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Faturamento", f"R$ {resumo['receita']:,.2f}")
c2.metric("Despesas", f"R$ {resumo['despesas']:,.2f}")

delta_lucro = f"{resumo['margem']:.0f}% margem" if resumo["receita"] > 0 else None
c3.metric("Lucro", f"R$ {resumo['lucro']:,.2f}", delta=delta_lucro)
c4.metric("Aluguéis", resumo["num_alugueis"],
          delta=f"R$ {resumo['ticket_medio']:,.0f} ticket médio" if resumo["num_alugueis"] > 0 else None)

# ---------------------------------------------------------------------------
# Alertas
# ---------------------------------------------------------------------------
alertas = []

# Estoque
estoque = db.get_estoque_atual()
if estoque <= 0:
    alertas.append(("error", f":material/inventory_2: **Estoque zerado!** Impossível realizar aluguéis."))
elif estoque <= 3:
    alertas.append(("error", f":material/inventory_2: **Estoque crítico:** apenas {estoque} unidade(s)."))
elif estoque <= 5:
    alertas.append(("warning", f":material/inventory_2: **Estoque baixo:** {estoque} unidade(s). Considere reabastecer."))

# Aluguéis ativos
ativos = db.get_alugueis_ativos()
if ativos:
    alertas.append(("info", f":material/assignment: **{len(ativos)} aluguel(éis) ativo(s)** no momento."))

# Parcelas pendentes
maquinas = db.listar_maquinas()
for maq in maquinas:
    restantes = maq["parcelas_total"] - maq["parcelas_pagas"]
    if restantes > 0:
        valor_rest = restantes * maq["valor_parcela"]
        alertas.append(("warning", f":material/payments: **{maq['nome']}:** {restantes} parcelas restantes (R$ {valor_rest:,.2f})."))

if alertas:
    st.divider()
    st.subheader("Alertas")
    for tipo, msg in alertas:
        getattr(st, tipo)(msg)

# ---------------------------------------------------------------------------
# Aluguéis Ativos
# ---------------------------------------------------------------------------
if ativos:
    st.divider()
    st.subheader("Aluguéis em Andamento")
    for a in ativos:
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        c1.markdown(f"**{a['cliente_nome']}**")
        c2.markdown(f"{a['maquina_nome']}")
        c3.markdown(f"{a['data_inicio']} | {a['dias']} dia(s)")
        c4.markdown(f"**R$ {a['valor_total']:,.2f}**")

# ---------------------------------------------------------------------------
# ROI por Máquina (resumo)
# ---------------------------------------------------------------------------
roi_data = db.get_roi_por_maquina()
if roi_data:
    st.divider()
    st.subheader("Retorno por Máquina")

    cols = st.columns(len(roi_data))
    for i, maq in enumerate(roi_data):
        receita = maq["receita_gerada"]
        custo = maq["custo_maquina"]
        roi_pct = ((receita - custo) / custo * 100) if custo > 0 else 0

        with cols[i]:
            st.markdown(f"**{maq['nome']}**")
            st.metric("Receita Gerada", f"R$ {receita:,.2f}")
            st.metric("Custo da Máquina", f"R$ {custo:,.2f}")
            st.metric(
                "ROI",
                f"{roi_pct:,.0f}%",
                delta=f"{'Lucro' if roi_pct > 0 else 'Prejuízo'}",
                delta_color="normal" if roi_pct >= 0 else "inverse",
            )
            st.caption(f"{maq['total_alugueis']} aluguéis realizados")

# ---------------------------------------------------------------------------
# Top Clientes
# ---------------------------------------------------------------------------
top_clientes = db.get_top_clientes(5)
if top_clientes:
    st.divider()
    st.subheader("Top Clientes")

    for i, c in enumerate(top_clientes, 1):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        col1.markdown(f"**{i}. {c['cliente_nome']}**")
        col2.markdown(f"{c['total_alugueis']} aluguéis")
        col3.markdown(f"R$ {c['receita_total']:,.2f} total")
        col4.markdown(f"Último: {c['ultimo_aluguel']}")
