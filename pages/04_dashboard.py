import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import database as db
from style import CATEGORIAS, RECEITA_COR, DESPESA_COR, LUCRO_COR, NEUTRO_COR, CHART_COLORS

st.title("Dashboard")

# ---------------------------------------------------------------------------
# KPIs do mês com comparação mês anterior
# ---------------------------------------------------------------------------
now = datetime.now()
resumo_atual = db.get_resumo_mensal()

# Mês anterior
mes_ant = now.month - 1
ano_ant = now.year
if mes_ant == 0:
    mes_ant = 12
    ano_ant -= 1
resumo_anterior = db.get_resumo_mensal(ano=ano_ant, mes=mes_ant)

def calc_delta(atual, anterior):
    if anterior == 0:
        return None
    pct = ((atual - anterior) / anterior) * 100
    return f"{pct:+.0f}% vs mês anterior"

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Faturamento (mês)", f"R$ {resumo_atual['receita']:,.2f}",
    delta=calc_delta(resumo_atual["receita"], resumo_anterior["receita"]),
)
col2.metric(
    "Despesas (mês)", f"R$ {resumo_atual['despesas']:,.2f}",
    delta=calc_delta(resumo_atual["despesas"], resumo_anterior["despesas"]),
    delta_color="inverse",
)
col3.metric(
    "Lucro (mês)", f"R$ {resumo_atual['lucro']:,.2f}",
    delta=f"{resumo_atual['margem']:.1f}% margem" if resumo_atual["receita"] > 0 else None,
)
col4.metric(
    "Aluguéis (mês)", resumo_atual["num_alugueis"],
    delta=calc_delta(resumo_atual["num_alugueis"], resumo_anterior["num_alugueis"]),
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

# Evolução do Lucro + Aluguéis
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

st.divider()

# ---------------------------------------------------------------------------
# Receita por Máquina (mensal)
# ---------------------------------------------------------------------------
st.subheader("Receita por Máquina")

receita_maq = db.get_receita_por_maquina_mensal()
if receita_maq:
    df_maq = pd.DataFrame(receita_maq)
    fig_maq = px.bar(
        df_maq, x="mes", y="receita", color="maquina",
        labels={"mes": "Mês", "receita": "Receita (R$)", "maquina": "Máquina"},
        color_discrete_sequence=CHART_COLORS,
        barmode="group",
    )
    fig_maq.update_layout(
        height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#14375A"),
    )
    st.plotly_chart(fig_maq, use_container_width=True)

# ---------------------------------------------------------------------------
# ROI por Máquina
# ---------------------------------------------------------------------------
roi_data = db.get_roi_por_maquina()
if roi_data:
    st.subheader("ROI por Máquina")
    df_roi = pd.DataFrame(roi_data)
    df_roi["lucro_liquido"] = df_roi["receita_gerada"] - df_roi["custo_maquina"]
    df_roi["roi_pct"] = ((df_roi["receita_gerada"] - df_roi["custo_maquina"]) / df_roi["custo_maquina"] * 100).round(1)

    fig_roi = go.Figure()
    fig_roi.add_trace(go.Bar(
        x=df_roi["nome"], y=df_roi["receita_gerada"],
        name="Receita Gerada", marker_color=RECEITA_COR,
    ))
    fig_roi.add_trace(go.Bar(
        x=df_roi["nome"], y=df_roi["custo_maquina"],
        name="Custo da Máquina", marker_color=DESPESA_COR,
    ))
    fig_roi.update_layout(
        barmode="group", xaxis_title="Máquina", yaxis_title="R$", height=350,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#14375A"),
    )
    st.plotly_chart(fig_roi, use_container_width=True)

    cols = st.columns(len(roi_data))
    for i, maq in enumerate(roi_data):
        roi = ((maq["receita_gerada"] - maq["custo_maquina"]) / maq["custo_maquina"] * 100) if maq["custo_maquina"] > 0 else 0
        cols[i].metric(
            maq["nome"],
            f"ROI: {roi:.0f}%",
            delta=f"{maq['total_alugueis']} aluguéis | R$ {maq['receita_gerada']:,.0f} receita",
        )

st.divider()

# ---------------------------------------------------------------------------
# Dias da Semana mais populares
# ---------------------------------------------------------------------------
dias_semana = db.get_dias_semana_populares()
if dias_semana:
    col_ds, col_cat = st.columns(2)

    with col_ds:
        st.subheader("Aluguéis por Dia da Semana")
        df_dias = pd.DataFrame(dias_semana)
        fig_dias = px.bar(
            df_dias, x="dia_semana", y="total",
            labels={"dia_semana": "Dia", "total": "Aluguéis"},
            color_discrete_sequence=[NEUTRO_COR],
        )
        fig_dias.update_layout(
            height=350, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#14375A"),
        )
        st.plotly_chart(fig_dias, use_container_width=True)

    with col_cat:
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
                height=350, paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#14375A"),
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Nenhuma despesa registrada.")

st.divider()

# ---------------------------------------------------------------------------
# Tabela resumo com download
# ---------------------------------------------------------------------------
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

csv = df_display.to_csv(index=False).encode("utf-8")
st.download_button(
    ":material/download: Exportar Resumo Mensal (CSV)",
    data=csv, file_name="resumo_mensal.csv", mime="text/csv",
)
