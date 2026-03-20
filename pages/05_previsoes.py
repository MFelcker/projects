import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression
import database as db
from style import RECEITA_COR, LUCRO_COR, DESPESA_COR

st.title("Previsões")

historico = db.get_historico_mensal(meses=24)

if len(historico) < 3:
    st.warning(
        f"São necessários pelo menos **3 meses** de dados para gerar previsões.  \n"
        f"Atualmente: **{len(historico)} mês(es)** registrado(s)."
    )
    st.stop()

df = pd.DataFrame(historico)
df["mes_num"] = range(len(df))
X = df["mes_num"].values.reshape(-1, 1)

# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
modelo_receita = LinearRegression().fit(X, df["receita"].values)
modelo_despesa = LinearRegression().fit(X, df["despesas"].values)

MESES_FUTUROS = 3
ultimo_idx = df["mes_num"].iloc[-1]
X_futuro = np.array([[ultimo_idx + i + 1] for i in range(MESES_FUTUROS)])

receita_prev = modelo_receita.predict(X_futuro)
despesa_prev = modelo_despesa.predict(X_futuro)
lucro_prev = receita_prev - despesa_prev

# Labels dos meses futuros
ultimo_mes = datetime.strptime(df["mes"].iloc[-1], "%Y-%m")
meses_labels = []
for i in range(1, MESES_FUTUROS + 1):
    m = ultimo_mes.month + i
    a = ultimo_mes.year
    while m > 12:
        m -= 12
        a += 1
    meses_labels.append(f"{a:04d}-{m:02d}")

# ---------------------------------------------------------------------------
# KPIs de Previsão
# ---------------------------------------------------------------------------
st.subheader("Previsão — Próximos 3 Meses")

for i, label in enumerate(meses_labels):
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Receita ({label})", f"R$ {max(0, receita_prev[i]):,.2f}")
    c2.metric(f"Despesas ({label})", f"R$ {max(0, despesa_prev[i]):,.2f}")
    c3.metric(f"Lucro ({label})", f"R$ {lucro_prev[i]:,.2f}")

st.divider()

# ---------------------------------------------------------------------------
# Tendência
# ---------------------------------------------------------------------------
tendencia = modelo_receita.coef_[0]
if tendencia > 0:
    st.success(f":material/trending_up: Tendência de **crescimento** na receita: +R$ {tendencia:,.2f}/mês")
elif tendencia < 0:
    st.error(f":material/trending_down: Tendência de **queda** na receita: R$ {tendencia:,.2f}/mês")
else:
    st.info(":material/trending_flat: Receita estável")

st.divider()

# ---------------------------------------------------------------------------
# Gráfico Histórico + Previsão
# ---------------------------------------------------------------------------
st.subheader("Histórico + Previsão")

fig = go.Figure()

# Dados reais
fig.add_trace(go.Scatter(
    x=list(df["mes"]), y=list(df["receita"]),
    mode="lines+markers", name="Receita (real)",
    line=dict(color=RECEITA_COR, width=3),
))
fig.add_trace(go.Scatter(
    x=list(df["mes"]), y=list(df["lucro"]),
    mode="lines+markers", name="Lucro (real)",
    line=dict(color=LUCRO_COR, width=3),
))

# Conexão real → previsão
fig.add_trace(go.Scatter(
    x=[df["mes"].iloc[-1], meses_labels[0]],
    y=[df["receita"].iloc[-1], max(0, receita_prev[0])],
    mode="lines", showlegend=False,
    line=dict(color=RECEITA_COR, width=1, dash="dot"),
))
fig.add_trace(go.Scatter(
    x=[df["mes"].iloc[-1], meses_labels[0]],
    y=[df["lucro"].iloc[-1], lucro_prev[0]],
    mode="lines", showlegend=False,
    line=dict(color=LUCRO_COR, width=1, dash="dot"),
))

# Previsão
fig.add_trace(go.Scatter(
    x=meses_labels, y=[max(0, v) for v in receita_prev],
    mode="lines+markers", name="Receita (previsão)",
    line=dict(color=RECEITA_COR, width=2, dash="dash"),
))
fig.add_trace(go.Scatter(
    x=meses_labels, y=list(lucro_prev),
    mode="lines+markers", name="Lucro (previsão)",
    line=dict(color=LUCRO_COR, width=2, dash="dash"),
))

fig.add_hline(y=0, line_dash="dash", line_color=DESPESA_COR, opacity=0.3)
fig.update_layout(
    xaxis_title="Mês", yaxis_title="R$", height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#14375A"),
)
st.plotly_chart(fig, use_container_width=True)

st.caption("Previsões baseadas em regressão linear sobre dados históricos. "
           "Quanto mais dados, mais precisas as projeções.")
