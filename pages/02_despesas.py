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

    cat_keys = list(CATEGORIAS.keys())
    cat_labels = list(CATEGORIAS.values())

    for d in despesas:
        cat_display = CATEGORIAS.get(d["categoria"], d["categoria"])
        label = f"R$ {d['valor']:,.2f} — {cat_display} — {d['data']}"
        if d.get("descricao"):
            label += f" | {d['descricao']}"

        with st.expander(label):
            with st.form(f"edit_desp_{d['id']}"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    edit_data = st.date_input(
                        "Data", value=date.fromisoformat(d["data"]), key=f"dd_{d['id']}",
                    )
                    cat_idx = cat_keys.index(d["categoria"]) if d["categoria"] in cat_keys else 0
                    edit_cat = st.selectbox(
                        "Categoria", options=cat_keys,
                        index=cat_idx,
                        format_func=lambda x: CATEGORIAS[x],
                        key=f"dc_{d['id']}",
                    )
                with ec2:
                    edit_valor = st.number_input(
                        "Valor (R$)", min_value=0.01, step=0.50,
                        value=float(d["valor"]), format="%.2f", key=f"dv_{d['id']}",
                    )
                    edit_desc = st.text_input(
                        "Descrição", value=d["descricao"] or "", key=f"de_{d['id']}",
                    )

                fc1, fc2 = st.columns([3, 1])
                salvar = fc1.form_submit_button("Salvar Alterações", type="primary")
                excluir = fc2.form_submit_button("Excluir")

                if salvar:
                    db.atualizar_despesa(
                        d["id"], edit_data.isoformat(), edit_cat,
                        edit_desc.strip(), edit_valor,
                    )
                    st.success("Despesa atualizada!")
                    st.rerun()
                if excluir:
                    db.excluir_despesa(d["id"])
                    st.success("Despesa excluída!")
                    st.rerun()

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
