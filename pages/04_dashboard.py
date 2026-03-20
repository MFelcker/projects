import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
from style import CATEGORIAS, RECEITA_COR, DESPESA_COR, LUCRO_COR, NEUTRO_COR, CHART_COLORS

st.title("Dashboard")

# ---------------------------------------------------------------------------
# KPIs do mês
# ---------------------------------------------------------------------------
resumo = db.get_resumo_mensal()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento (mês)", f"R$ {resumo['receita']:,.2f}")
col2.metric("Despesas (mês)", f"R$ {resumo['despesas']:,.2f}")
col3.metric(
    "Lucro (mês)", f"R$ {resumo['lucro']:,.2f}",
    delta=f"{resumo['margem']:.1f}% margem" if resumo["receita"] > 0 else None,
)
col4.metric(
    "Aluguéis (mês)", resumo["num_alugueis"],
    delta=f"Ticket médio: R$ {resumo['ticket_medio']:,.2f}" if resumo["num_alugueis"] > 0 else None,
)

st.divider()

# ---------------------------------------------------------------------------
# Histórico Mensal
# ---------------------------------------------------------------------------
historico = db.get_historico_mensal(meses=12)

if not historico:
    st.info("Registre aluguéis para visualizar o dashboard.")
    st.stop()

df = pd.DataFrame(historico)

# Faturamento x Despesas
st.subheader("Faturamento e Despesas Mensais")
fig = go.Figure()
fig.add_trace(go.Bar(x=df["mes"], y=df["receita"], name="Receita", marker_color=RECEITA_COR))
fig.add_trace(go.Bar(x=df["mes"], y=df["despesas"], name="Despesas", marker_color=DESPESA_COR))
fig.update_layout(
    barmode="group", xaxis_title="Mês", yaxis_title="R$", height=400,
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#14375A"),
)
st.plotly_chart(fig, use_container_width=True)

# Evolução do Lucro
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Evolução do Lucro")
    fig_lucro = px.line(df, x="mes", y="lucro", markers=True,
                        labels={"mes": "Mês", "lucro": "Lucro (R$)"})
    fig_lucro.update_traces(line_color=LUCRO_COR, line_width=3)
    fig_lucro.add_hline(y=0, line_dash="dash", line_color=DESPESA_COR, opacity=0.4)
    fig_lucro.update_layout(
        height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#14375A"),
    )
    st.plotly_chart(fig_lucro, use_container_width=True)

with col_g2:
    st.subheader("Aluguéis por Mês")
    fig_alug = px.bar(df, x="mes", y="num_alugueis",
                      labels={"mes": "Mês", "num_alugueis": "Aluguéis"},
                      color_discrete_sequence=[NEUTRO_COR])
    fig_alug.update_layout(
        height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#14375A"),
    )
    st.plotly_chart(fig_alug, use_container_width=True)

# Tabela resumo
st.subheader("Resumo Mensal")
df_display = df.rename(columns={
    "mes": "Mês", "receita": "Receita (R$)", "despesas": "Despesas (R$)",
    "lucro": "Lucro (R$)", "num_alugueis": "Aluguéis",
})
df_display["Margem %"] = (
    (df_display["Lucro (R$)"] / df_display["Receita (R$)"] * 100)
    .round(1).fillna(0)
)
st.dataframe(df_display, use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Despesas por Categoria
# ---------------------------------------------------------------------------
st.subheader("Despesas por Categoria")

cat_data = db.get_despesas_por_categoria()
if cat_data:
    df_cat = pd.DataFrame(cat_data)
    df_cat["categoria"] = df_cat["categoria"].map(CATEGORIAS).fillna(df_cat["categoria"])
    fig_cat = px.pie(
        df_cat, names="categoria", values="total",
        color_discrete_sequence=CHART_COLORS,
    )
    fig_cat.update_layout(
        height=400, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#14375A"),
    )
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("Nenhuma despesa registrada ainda.")
