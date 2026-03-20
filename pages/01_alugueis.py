import streamlit as st
import pandas as pd
from datetime import date, timedelta
import database as db

st.title("Aluguéis")

maquinas = db.listar_maquinas()

if not maquinas:
    st.warning("Nenhuma máquina cadastrada. Vá até a aba **Manutenção** para cadastrar.")
    st.stop()

# ---------------------------------------------------------------------------
# Novo Aluguel
# ---------------------------------------------------------------------------
st.subheader("Novo Aluguel")

estoque_atual = db.get_estoque_atual()
if estoque_atual <= 5:
    st.warning(f"Estoque baixo: apenas **{estoque_atual}** unidade(s) de produto.")

with st.form("form_aluguel", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        cliente_nome = st.text_input("Nome do cliente *")
        cliente_telefone = st.text_input("Telefone")
        maquina_opcoes = {m["nome"]: m["id"] for m in maquinas}
        maquina_sel = st.selectbox("Máquina *", options=list(maquina_opcoes.keys()))

    with col2:
        data_inicio = st.date_input("Data do aluguel", value=date.today())
        dias = st.radio(
            "Duração",
            options=[1, 2],
            format_func=lambda x: f"{x} dia(s) — R$ {'80,00' if x == 1 else '120,00'}",
            horizontal=True,
        )
        produto_extra = st.number_input(
            "Produto extra (unid. 500ml — R$ 15,00 cada)",
            min_value=0, max_value=50, value=0,
        )

    col_obs, col_preco = st.columns(2)
    with col_obs:
        observacoes = st.text_area("Observações", height=68)
    with col_preco:
        valor_sugerido = 80.0 if dias == 1 else 120.0
        valor_personalizado = st.checkbox("Valor personalizado")
        if valor_personalizado:
            valor_base = st.number_input(
                "Valor do aluguel (R$)", min_value=0.0,
                step=10.0, value=valor_sugerido, format="%.2f",
            )
        else:
            valor_base = valor_sugerido

    valor_extra = produto_extra * 15.0
    valor_total = valor_base + valor_extra

    st.info(
        f"**Resumo:** Aluguel R$ {valor_base:,.2f} + "
        f"Produto extra R$ {valor_extra:,.2f} = **R$ {valor_total:,.2f}**  \n"
        f"*(1 unidade de 500ml inclusa + {produto_extra} extra)*"
    )

    qtd_necessaria = 1 + produto_extra
    submitted = st.form_submit_button("Registrar Aluguel", type="primary", use_container_width=True)

    if submitted:
        if not cliente_nome.strip():
            st.error("Informe o nome do cliente.")
        elif estoque_atual < qtd_necessaria:
            st.error(
                f"Estoque insuficiente! Disponível: {estoque_atual} — "
                f"Necessário: {qtd_necessaria}."
            )
        else:
            aluguel_id = db.registrar_aluguel(
                maquina_opcoes[maquina_sel], cliente_nome.strip(),
                cliente_telefone.strip(), data_inicio.isoformat(),
                dias, produto_extra, observacoes.strip(),
                valor_custom=valor_base if valor_personalizado else None,
            )
            st.success(f"Aluguel #{aluguel_id} registrado! Total: R$ {valor_total:,.2f}")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Histórico de Aluguéis
# ---------------------------------------------------------------------------
st.subheader("Histórico de Aluguéis")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtro_status = st.selectbox("Status", ["Todos", "ativo", "finalizado", "cancelado"])
with col_f2:
    filtro_data_ini = st.date_input("De", value=date.today() - timedelta(days=60), key="f_ini")
with col_f3:
    filtro_data_fim = st.date_input("Até", value=date.today(), key="f_fim")

alugueis = db.listar_alugueis(
    status=filtro_status if filtro_status != "Todos" else None,
    data_inicio=filtro_data_ini.isoformat(),
    data_fim=filtro_data_fim.isoformat(),
)

if alugueis:
    STATUS_LABEL = {"ativo": "Em andamento", "finalizado": "Finalizado", "cancelado": "Cancelado"}

    for a in alugueis:
        status_icon = {"ativo": ":material/circle:", "finalizado": ":material/check_circle:", "cancelado": ":material/cancel:"}.get(a["status"], "")
        label = f"{status_icon} #{a['id']} — {a['cliente_nome']} | {a['maquina_nome']} | {a['data_inicio']} | R$ {a['valor_total']:,.2f}"

        with st.expander(label):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Valor Total", f"R$ {a['valor_total']:,.2f}")
            c2.metric("Dias", a["dias"])
            c3.metric("Produto Extra", f"{a['produto_extra_qtd']} unid.")
            c4.metric("Status", STATUS_LABEL.get(a["status"], a["status"]))

            if a["observacoes"]:
                st.caption(f"Obs: {a['observacoes']}")

            if a["status"] == "ativo":
                bc1, bc2 = st.columns(2)
                if bc1.button("Finalizar", key=f"fin_{a['id']}", use_container_width=True):
                    db.finalizar_aluguel(a["id"])
                    st.rerun()
                if bc2.button("Cancelar", key=f"can_{a['id']}", use_container_width=True):
                    db.cancelar_aluguel(a["id"])
                    st.rerun()
else:
    st.info("Nenhum aluguel encontrado no período selecionado.")
