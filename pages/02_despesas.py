import streamlit as st
import pandas as pd
from datetime import date, timedelta
import database as db
from style import CATEGORIAS

st.title("Despesas")

# ---------------------------------------------------------------------------
# Registrar Despesa
# ---------------------------------------------------------------------------
st.subheader("Registrar Despesa")

maquinas = db.listar_maquinas()

with st.form("form_despesa", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        data_despesa = st.date_input("Data", value=date.today())
        categoria = st.selectbox(
            "Categoria",
            options=list(CATEGORIAS.keys()),
            format_func=lambda x: CATEGORIAS[x],
        )

    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.01, step=0.50, format="%.2f")
        maquina_opcoes = {"Nenhuma": None}
        maquina_opcoes.update({m["nome"]: m["id"] for m in maquinas})
        maquina_sel = st.selectbox("Máquina (opcional)", options=list(maquina_opcoes.keys()))

    descricao = st.text_input("Descrição")

    if st.form_submit_button("Registrar Despesa", type="primary", use_container_width=True):
        db.registrar_despesa(
            data_despesa.isoformat(), categoria, descricao.strip(),
            valor, maquina_opcoes[maquina_sel],
        )
        st.success(f"Despesa de R$ {valor:,.2f} registrada!")
        st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Histórico
# ---------------------------------------------------------------------------
st.subheader("Histórico de Despesas")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtro_data_ini = st.date_input("De", value=date.today() - timedelta(days=60), key="d_ini")
with col_f2:
    filtro_data_fim = st.date_input("Até", value=date.today(), key="d_fim")
with col_f3:
    filtro_cat = st.selectbox(
        "Categoria",
        options=["Todas"] + list(CATEGORIAS.keys()),
        format_func=lambda x: "Todas" if x == "Todas" else CATEGORIAS[x],
        key="filtro_cat",
    )

despesas = db.listar_despesas(
    data_inicio=filtro_data_ini.isoformat(),
    data_fim=filtro_data_fim.isoformat(),
    categoria=filtro_cat if filtro_cat != "Todas" else None,
)

if despesas:
    total = sum(d["valor"] for d in despesas)
    st.metric("Total no período", f"R$ {total:,.2f}")

    df = pd.DataFrame(despesas)
    df["categoria"] = df["categoria"].map(CATEGORIAS).fillna(df["categoria"])
    df = df.rename(columns={
        "data": "Data", "categoria": "Categoria", "descricao": "Descrição",
        "valor": "Valor (R$)", "maquina_nome": "Máquina",
    })
    st.dataframe(
        df[["Data", "Categoria", "Descrição", "Valor (R$)", "Máquina"]],
        use_container_width=True, hide_index=True,
    )

    # Totais por categoria
    st.subheader("Totais por Categoria")
    cat_totals = db.get_despesas_por_categoria(
        filtro_data_ini.isoformat(), filtro_data_fim.isoformat(),
    )
    if cat_totals:
        n = min(len(cat_totals), 6)
        cols = st.columns(n)
        for i, ct in enumerate(cat_totals[:n]):
            cols[i].metric(
                CATEGORIAS.get(ct["categoria"], ct["categoria"]),
                f"R$ {ct['total']:,.2f}",
            )
else:
    st.info("Nenhuma despesa encontrada no período.")
