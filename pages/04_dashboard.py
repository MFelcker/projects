import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import database as db

st.title("📊 Dashboard")

# --- KPIs do mês ---
resumo = db.get_resumo_mensal()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento (mês)", f"R$ {resumo['receita']:.2f}")
col2.metric("Despesas (mês)", f"R$ {resumo['despesas']:.2f}")
col3.metric("Lucro (mês)", f"R$ {resumo['lucro']:.2f}",
            delta=f"{resumo['margem']:.1f}% margem" if resumo['receita'] > 0 else None)
col4.metric("Aluguéis (mês)", resumo["num_alugueis"],
            delta=f"Ticket médio: R$ {resumo['ticket_medio']:.2f}" if resumo["num_alugueis"] > 0 else None)

st.divider()

# --- Histórico Mensal ---
historico = db.get_historico_mensal(meses=12)

if historico:
    df = pd.DataFrame(historico)

    # Gráfico de Faturamento x Despesas
    st.subheader("Faturamento e Despesas Mensais")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["mes"], y=df["receita"], name="Receita", marker_color="#2ecc71"))
    fig.add_trace(go.Bar(x=df["mes"], y=df["despesas"], name="Despesas", marker_color="#e74c3c"))
    fig.update_layout(barmode="group", xaxis_title="Mês", yaxis_title="R$", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de Lucro
    st.subheader("Evolução do Lucro")
    fig_lucro = px.line(df, x="mes", y="lucro", markers=True,
                        labels={"mes": "Mês", "lucro": "Lucro (R$)"})
    fig_lucro.update_traces(line_color="#3498db", line_width=3)
    fig_lucro.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    fig_lucro.update_layout(height=350)
    st.plotly_chart(fig_lucro, use_container_width=True)

    # Aluguéis por mês
    st.subheader("Quantidade de Aluguéis por Mês")
    fig_alug = px.bar(df, x="mes", y="num_alugueis",
                      labels={"mes": "Mês", "num_alugueis": "Aluguéis"},
                      color_discrete_sequence=["#9b59b6"])
    fig_alug.update_layout(height=300)
    st.plotly_chart(fig_alug, use_container_width=True)

    # Tabela resumo
    st.subheader("Resumo Mensal")
    df_display = df.copy()
    df_display.columns = ["Mês", "Receita", "Despesas", "Lucro", "Aluguéis"]
    df_display["Margem %"] = (df_display["Lucro"] / df_display["Receita"] * 100).round(1)
    df_display["Margem %"] = df_display["Margem %"].fillna(0)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

else:
    st.info("Ainda não há dados suficientes para exibir o dashboard. Registre alguns aluguéis primeiro!")

# --- Despesas por Categoria ---
st.divider()
st.subheader("Despesas por Categoria")

cat_data = db.get_despesas_por_categoria()
if cat_data:
    CATEGORIAS = {
        "produto": "Produto de limpeza",
        "parcela_maquina": "Parcela da máquina",
        "manutencao": "Manutenção",
        "marketing": "Marketing / Tráfego",
        "suprimentos": "Suprimentos",
        "outros": "Outros",
    }
    df_cat = pd.DataFrame(cat_data)
    df_cat["categoria"] = df_cat["categoria"].map(CATEGORIAS)
    fig_cat = px.pie(df_cat, names="categoria", values="total",
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig_cat.update_layout(height=400)
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("Nenhuma despesa registrada ainda.")
