import streamlit as st
import pandas as pd
from datetime import date, timedelta
import database as db

st.title("📋 Aluguéis")

maquinas = db.listar_maquinas()

if not maquinas:
    st.warning("Nenhuma máquina cadastrada. Cadastre suas máquinas na aba **Manutenção**.")

# --- Novo Aluguel ---
st.subheader("Novo Aluguel")

with st.form("form_aluguel", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        cliente_nome = st.text_input("Nome do cliente *")
        cliente_telefone = st.text_input("Telefone")
        maquina_opcoes = {m["nome"]: m["id"] for m in maquinas}
        maquina_sel = st.selectbox(
            "Máquina *",
            options=list(maquina_opcoes.keys()) if maquina_opcoes else ["Nenhuma"],
        )

    with col2:
        data_inicio = st.date_input("Data do aluguel", value=date.today())
        dias = st.radio("Duração", options=[1, 2], format_func=lambda x: f"{x} dia(s) - R$ {'80' if x == 1 else '120'}", horizontal=True)
        produto_extra = st.number_input("Produto extra (unid. 500ml)", min_value=0, max_value=50, value=0)

    observacoes = st.text_area("Observações", height=68)

    # Resumo do valor
    valor_base = 80.0 if dias == 1 else 120.0
    valor_extra = produto_extra * 15.0
    valor_total = valor_base + valor_extra

    st.markdown(f"""
    **Resumo:** Diária R$ {valor_base:.2f} + Produto extra R$ {valor_extra:.2f} = **R$ {valor_total:.2f}**
    *(1 unidade de 500ml inclusa + {produto_extra} extra(s))*
    """)

    estoque_atual = db.get_estoque_atual()
    qtd_necessaria = 1 + produto_extra

    submitted = st.form_submit_button("Registrar Aluguel", type="primary", use_container_width=True)

    if submitted:
        if not cliente_nome:
            st.error("Informe o nome do cliente.")
        elif not maquina_opcoes:
            st.error("Cadastre uma máquina primeiro.")
        elif estoque_atual < qtd_necessaria:
            st.error(f"Estoque insuficiente! Disponível: {estoque_atual} unidade(s). Necessário: {qtd_necessaria}.")
        else:
            maquina_id = maquina_opcoes[maquina_sel]
            aluguel_id = db.registrar_aluguel(
                maquina_id, cliente_nome, cliente_telefone,
                data_inicio.isoformat(), dias, produto_extra, observacoes,
            )
            st.success(f"Aluguel #{aluguel_id} registrado com sucesso! Total: R$ {valor_total:.2f}")
            st.rerun()

# --- Estoque rápido ---
estoque_atual = db.get_estoque_atual()
if estoque_atual <= 5:
    st.warning(f"⚠️ Estoque baixo: apenas {estoque_atual} unidade(s) de produto restante(s)!")

st.divider()

# --- Lista de Aluguéis ---
st.subheader("Histórico de Aluguéis")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtro_status = st.selectbox("Status", ["Todos", "ativo", "finalizado", "cancelado"])
with col_f2:
    filtro_data_ini = st.date_input("De", value=date.today() - timedelta(days=30), key="filtro_ini")
with col_f3:
    filtro_data_fim = st.date_input("Até", value=date.today(), key="filtro_fim")

alugueis = db.listar_alugueis(
    status=filtro_status if filtro_status != "Todos" else None,
    data_inicio=filtro_data_ini.isoformat(),
    data_fim=filtro_data_fim.isoformat(),
)

if alugueis:
    for a in alugueis:
        status_emoji = {"ativo": "🟢", "finalizado": "✅", "cancelado": "❌"}.get(a["status"], "")
        with st.expander(f"{status_emoji} #{a['id']} - {a['cliente_nome']} | {a['maquina_nome']} | {a['data_inicio']} | R$ {a['valor_total']:.2f}"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Valor Total", f"R$ {a['valor_total']:.2f}")
            col2.metric("Dias", a["dias"])
            col3.metric("Produto Extra", f"{a['produto_extra_qtd']} unid.")

            if a["observacoes"]:
                st.text(f"Obs: {a['observacoes']}")

            if a["status"] == "ativo":
                c1, c2 = st.columns(2)
                if c1.button("✅ Finalizar", key=f"fin_{a['id']}"):
                    db.finalizar_aluguel(a["id"])
                    st.success("Aluguel finalizado!")
                    st.rerun()
                if c2.button("❌ Cancelar", key=f"can_{a['id']}"):
                    db.cancelar_aluguel(a["id"])
                    st.warning("Aluguel cancelado. Estoque devolvido.")
                    st.rerun()
else:
    st.info("Nenhum aluguel encontrado no período.")
