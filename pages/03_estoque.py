import streamlit as st
import database as db

st.title("Estoque de Produto")

estoque = db.get_estoque_atual()

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Estoque Atual", f"{estoque} unid. (500ml)")
col2.metric("Em Litros", f"{estoque * 0.5:.1f} L")
CUSTO_UNITARIO = 9.0  # R$90 / 10 unidades
col3.metric("Valor em Estoque", f"R$ {estoque * CUSTO_UNITARIO:,.2f}")

# ---------------------------------------------------------------------------
# Alerta de nível
# ---------------------------------------------------------------------------
if estoque <= 0:
    st.error("ESTOQUE ZERADO — impossível realizar aluguéis.")
elif estoque <= 3:
    st.error(f"Estoque crítico: apenas {estoque} unidade(s)!")
elif estoque <= 5:
    st.warning(f"Estoque baixo: {estoque} unidade(s). Considere reabastecer.")
else:
    st.success(f"Estoque OK: {estoque} unidade(s)")

progresso = min(max(estoque, 0) / 20, 1.0)
st.progress(progresso, text=f"{estoque}/20 unidades")

st.divider()

# ---------------------------------------------------------------------------
# Registrar Compra
# ---------------------------------------------------------------------------
st.subheader("Registrar Compra de Produto")

with st.form("form_compra"):
    st.info("**Referência:** 5 litros = 10 unidades de 500ml = R$ 90,00")

    qtd_litros = st.number_input(
        "Quantidade (litros)", min_value=0.5, max_value=100.0, value=5.0, step=0.5,
    )
    unidades = int(qtd_litros * 2)
    custo = (qtd_litros / 5) * 90.0

    st.markdown(f"**{unidades} unidades** de 500ml | Custo estimado: **R$ {custo:,.2f}**")

    if st.form_submit_button("Registrar Compra", type="primary", use_container_width=True):
        db.registrar_compra_produto(qtd_litros)
        st.success(
            f"Compra registrada! +{unidades} unidades. "
            f"Despesa de R$ {custo:,.2f} lançada automaticamente."
        )
        st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Movimentações
# ---------------------------------------------------------------------------
st.subheader("Movimentações Recentes")

movs = db.listar_movimentacoes_estoque(limite=30)
if movs:
    for m in movs:
        icon = ":material/download:" if m["tipo"] == "entrada" else ":material/upload:"
        sinal = "+" if m["tipo"] == "entrada" else "-"
        custo_str = f" | R$ {m['custo_total']:,.2f}" if m["custo_total"] else ""
        obs = m["observacoes"] or ""
        st.markdown(f"{icon} `{m['data'][:16]}` | **{sinal}{m['quantidade']}** unid.{custo_str} | {obs}")
else:
    st.info("Nenhuma movimentação registrada.")
