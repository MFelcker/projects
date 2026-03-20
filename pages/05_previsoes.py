import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import database as db

st.title("🔮 Previsões de Faturamento e Lucro")

historico = db.get_historico_mensal(meses=24)

if len(historico) < 3:
    st.warning(
        f"São necessários pelo menos **3 meses** de dados para gerar previsões. "
        f"Atualmente você tem **{len(historico)} mês(es)** de dados.\n\n"
        "Continue registrando seus aluguéis e despesas para desbloquear esta funcionalidade!"
    )
    st.stop()

df = pd.DataFrame(historico)
df["mes_num"] = range(len(df))

# --- Regressão Linear para Receita ---
from sklearn.linear_model import LinearRegression

X = df["mes_num"].values.reshape(-1, 1)

# Previsão de receita
modelo_receita = LinearRegression()
modelo_receita.fit(X, df["receita"].values)

# Previsão de despesas
modelo_despesa = LinearRegression()
modelo_despesa.fit(X, df["despesas"].values)

# Gerar previsões para os próximos 3 meses
meses_futuros = 3
ultimo_mes_num = df["mes_num"].iloc[-1]
X_futuro = np.array([[ultimo_mes_num + i + 1] for i in range(meses_futuros)])

receita_prevista = modelo_receita.predict(X_futuro)
despesa_prevista = modelo_despesa.predict(X_futuro)
lucro_previsto = receita_prevista - despesa_prevista

# Gerar labels dos meses futuros
ultimo_mes = datetime.strptime(df["mes"].iloc[-1], "%Y-%m")
meses_labels = []
for i in range(1, meses_futuros + 1):
    mes = ultimo_mes.month + i
    ano = ultimo_mes.year
    while mes > 12:
        mes -= 12
        ano += 1
    meses_labels.append(f"{ano:04d}-{mes:02d}")

# --- KPIs de Previsão ---
st.subheader("Previsão para os Próximos 3 Meses")

for i, label in enumerate(meses_labels):
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Receita ({label})", f"R$ {max(0, receita_prevista[i]):.2f}")
    col2.metric(f"Despesas ({label})", f"R$ {max(0, despesa_prevista[i]):.2f}")
    col3.metric(f"Lucro ({label})", f"R$ {lucro_previsto[i]:.2f}")

st.divider()

# --- Tendência ---
tendencia_receita = modelo_receita.coef_[0]
if tendencia_receita > 0:
    st.success(f"📈 Tendência de **crescimento** na receita: +R$ {tendencia_receita:.2f}/mês")
elif tendencia_receita < 0:
    st.error(f"📉 Tendência de **queda** na receita: R$ {tendencia_receita:.2f}/mês")
else:
    st.info("➡️ Receita estável")

st.divider()

# --- Gráfico Histórico + Previsão ---
st.subheader("Gráfico: Histórico + Previsão")

todos_meses = list(df["mes"]) + meses_labels
receita_total = list(df["receita"]) + [max(0, v) for v in receita_prevista]
despesa_total = list(df["despesas"]) + [max(0, v) for v in despesa_prevista]
lucro_total = list(df["lucro"]) + list(lucro_previsto)

fig = go.Figure()

# Histórico
fig.add_trace(go.Scatter(
    x=list(df["mes"]), y=list(df["receita"]),
    mode="lines+markers", name="Receita (real)",
    line=dict(color="#2ecc71", width=3),
))
fig.add_trace(go.Scatter(
    x=list(df["mes"]), y=list(df["lucro"]),
    mode="lines+markers", name="Lucro (real)",
    line=dict(color="#3498db", width=3),
))

# Previsão
fig.add_trace(go.Scatter(
    x=meses_labels, y=[max(0, v) for v in receita_prevista],
    mode="lines+markers", name="Receita (previsão)",
    line=dict(color="#2ecc71", width=2, dash="dash"),
))
fig.add_trace(go.Scatter(
    x=meses_labels, y=list(lucro_previsto),
    mode="lines+markers", name="Lucro (previsão)",
    line=dict(color="#3498db", width=2, dash="dash"),
))

# Linha de conexão entre real e previsão
fig.add_trace(go.Scatter(
    x=[df["mes"].iloc[-1], meses_labels[0]],
    y=[df["receita"].iloc[-1], max(0, receita_prevista[0])],
    mode="lines", showlegend=False,
    line=dict(color="#2ecc71", width=1, dash="dot"),
))
fig.add_trace(go.Scatter(
    x=[df["mes"].iloc[-1], meses_labels[0]],
    y=[df["lucro"].iloc[-1], lucro_previsto[0]],
    mode="lines", showlegend=False,
    line=dict(color="#3498db", width=1, dash="dot"),
))

fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.3)
fig.update_layout(
    xaxis_title="Mês", yaxis_title="R$", height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig, use_container_width=True)

st.caption("⚠️ Previsões baseadas em regressão linear simples sobre dados históricos. "
           "Quanto mais dados, mais precisas serão as previsões.")
