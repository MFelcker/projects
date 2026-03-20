import streamlit as st
import pandas as pd
from datetime import date
import database as db

st.title("Manutenção e Vida Útil")

maquinas = db.listar_maquinas()

# ---------------------------------------------------------------------------
# Cadastro de Máquina
# ---------------------------------------------------------------------------
st.subheader("Cadastrar Máquina")

with st.form("form_maquina", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nome_maq = st.text_input("Nome / Modelo *", placeholder="Ex: Extratora WAP")
        data_compra = st.date_input("Data da compra", value=date.today())
        valor_total = st.number_input("Valor total (R$)", min_value=0.0, step=50.0, format="%.2f")
    with col2:
        parcelas_total = st.number_input("Total de parcelas", min_value=0, step=1)
        valor_parcela = st.number_input("Valor da parcela (R$)", min_value=0.0, step=10.0, format="%.2f")
        parcelas_pagas = st.number_input("Parcelas já pagas", min_value=0, step=1)

    if st.form_submit_button("Cadastrar Máquina", type="primary"):
        if not nome_maq.strip():
            st.error("Informe o nome da máquina.")
        else:
            db.adicionar_maquina(
                nome_maq.strip(), data_compra.isoformat(), valor_total,
                parcelas_total, valor_parcela, parcelas_pagas,
            )
            st.success(f"Máquina '{nome_maq}' cadastrada!")

            # Cadastrar peças padrão
            PECAS_PADRAO = [
                ("Filtro HEPA", 90, 35.0),
                ("Filtro de espuma", 60, 20.0),
                ("Mangueira de sucção", 365, 50.0),
                ("Escova rotativa", 180, 45.0),
                ("Correia", 365, 25.0),
                ("Vedação do reservatório", 365, 30.0),
            ]
            maquinas_atuais = db.listar_maquinas()
            nova_id = maquinas_atuais[-1]["id"]
            for nome_p, vida, custo in PECAS_PADRAO:
                db.adicionar_peca(nova_id, nome_p, vida, custo, date.today().isoformat())

            st.info("Peças padrão cadastradas automaticamente.")
            st.rerun()

# ---------------------------------------------------------------------------
# Situação das Máquinas
# ---------------------------------------------------------------------------
if maquinas:
    st.divider()
    st.subheader("Situação das Máquinas")

    for maq in maquinas:
        restantes = maq["parcelas_total"] - maq["parcelas_pagas"]
        valor_restante = restantes * maq["valor_parcela"]
        tag = "Quitada" if restantes <= 0 else f"{restantes} parcelas restantes"

        with st.expander(f":material/precision_manufacturing: {maq['nome']} — {tag}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Valor Total", f"R$ {maq['valor_total']:,.2f}")
            c2.metric("Parcelas", f"{maq['parcelas_pagas']}/{maq['parcelas_total']}")
            c3.metric("Valor Restante", f"R$ {valor_restante:,.2f}")

st.divider()

# ---------------------------------------------------------------------------
# Vida Útil das Peças
# ---------------------------------------------------------------------------
st.subheader("Vida Útil das Peças")

if not maquinas:
    st.info("Cadastre uma máquina para gerenciar peças.")
    st.stop()

maq_filtro = st.selectbox(
    "Filtrar por máquina",
    options=["Todas"] + [m["nome"] for m in maquinas],
)
maquina_id_filtro = None
if maq_filtro != "Todas":
    maquina_id_filtro = next(m["id"] for m in maquinas if m["nome"] == maq_filtro)

pecas = db.listar_pecas(maquina_id=maquina_id_filtro)

if pecas:
    for peca in pecas:
        info = db.get_status_peca(peca)

        if info["status"] == "vencida":
            icon = ":material/error:"
        elif info["status"] == "atencao":
            icon = ":material/warning:"
        else:
            icon = ":material/check_circle:"

        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

        with c1:
            st.markdown(f"**{icon} {peca['nome']}** ({peca['maquina_nome']})")
            st.progress(
                info["percentual"] / 100,
                text=f"{info['percentual']:.0f}% usado — {info['dias_restantes']} dias restantes",
            )

        with c2:
            st.caption("Instalação")
            st.text(peca["data_instalacao"])

        with c3:
            st.caption("Próxima troca")
            st.text(info["data_proxima_troca"])

        with c4:
            st.caption("Custo reposição")
            st.text(f"R$ {peca['custo_reposicao']:,.2f}")

        st.markdown("---")

    # Estimativa anual
    st.subheader("Estimativa de Gasto Anual com Manutenção")
    custo_anual = {}
    for peca in pecas:
        nome_maq = peca["maquina_nome"]
        trocas_ano = 365 / peca["vida_util_dias"] if peca["vida_util_dias"] > 0 else 0
        custo_anual[nome_maq] = custo_anual.get(nome_maq, 0) + trocas_ano * peca["custo_reposicao"]

    cols = st.columns(len(custo_anual) + 1)
    for i, (nome_maq, custo) in enumerate(custo_anual.items()):
        cols[i].metric(nome_maq, f"R$ {custo:,.2f}")
    cols[-1].metric("Total", f"R$ {sum(custo_anual.values()):,.2f}")

else:
    st.info("Nenhuma peça cadastrada para esta máquina.")

st.divider()

# ---------------------------------------------------------------------------
# Registrar Troca
# ---------------------------------------------------------------------------
st.subheader("Registrar Troca de Peça")

pecas_todas = db.listar_pecas()
if not pecas_todas:
    st.info("Cadastre máquinas e peças para registrar trocas.")
    st.stop()

with st.form("form_troca"):
    peca_opcoes = {f"{p['nome']} ({p['maquina_nome']})": p["id"] for p in pecas_todas}
    peca_sel = st.selectbox("Peça", options=list(peca_opcoes.keys()))
    peca_selecionada = next(p for p in pecas_todas if p["id"] == peca_opcoes[peca_sel])

    c1, c2 = st.columns(2)
    with c1:
        data_troca = st.date_input("Data da troca", value=date.today())
    with c2:
        custo_troca = st.number_input(
            "Custo (R$)", min_value=0.0, step=5.0,
            value=peca_selecionada["custo_reposicao"], format="%.2f",
        )
    obs_troca = st.text_input("Observações")

    if st.form_submit_button("Registrar Troca", type="primary"):
        db.registrar_troca_peca(
            peca_opcoes[peca_sel], data_troca.isoformat(),
            custo_troca, obs_troca.strip(),
        )
        st.success(f"Troca registrada! Despesa de R$ {custo_troca:,.2f} lançada.")
        st.rerun()

# Histórico de trocas
st.subheader("Histórico de Trocas")
trocas = db.listar_trocas()
if trocas:
    df_trocas = pd.DataFrame(trocas).rename(columns={
        "data_troca": "Data", "peca_nome": "Peça",
        "maquina_nome": "Máquina", "custo": "Custo (R$)", "observacoes": "Obs",
    })
    st.dataframe(
        df_trocas[["Data", "Peça", "Máquina", "Custo (R$)", "Obs"]],
        use_container_width=True, hide_index=True,
    )
else:
    st.info("Nenhuma troca registrada.")
