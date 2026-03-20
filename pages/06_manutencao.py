import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import database as db

st.title("🔧 Manutenção e Vida Útil das Peças")

maquinas = db.listar_maquinas()

# --- Cadastro de Máquina ---
st.subheader("Cadastrar Máquina")

with st.form("form_maquina", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nome_maq = st.text_input("Nome/Modelo *", placeholder="Ex: Extratora WAP")
        data_compra = st.date_input("Data da compra", value=date.today())
        valor_total = st.number_input("Valor total (R$)", min_value=0.0, step=50.0, format="%.2f")
    with col2:
        parcelas_total = st.number_input("Total de parcelas", min_value=0, step=1)
        valor_parcela = st.number_input("Valor da parcela (R$)", min_value=0.0, step=10.0, format="%.2f")
        parcelas_pagas = st.number_input("Parcelas já pagas", min_value=0, step=1)

    if st.form_submit_button("Cadastrar Máquina", type="primary"):
        if not nome_maq:
            st.error("Informe o nome da máquina.")
        else:
            db.adicionar_maquina(
                nome_maq, data_compra.isoformat(), valor_total,
                parcelas_total, valor_parcela, parcelas_pagas,
            )
            st.success(f"Máquina '{nome_maq}' cadastrada!")

            # Cadastrar peças padrão
            pecas_padrao = [
                ("Filtro HEPA", 90, 35.0),
                ("Filtro de espuma", 60, 20.0),
                ("Mangueira de sucção", 365, 50.0),
                ("Escova rotativa", 180, 45.0),
                ("Correia", 365, 25.0),
                ("Vedação do reservatório", 365, 30.0),
            ]
            maquinas_atualizadas = db.listar_maquinas()
            nova_maq_id = maquinas_atualizadas[-1]["id"]
            for nome_peca, vida, custo in pecas_padrao:
                db.adicionar_peca(nova_maq_id, nome_peca, vida, custo, date.today().isoformat())

            st.info("Peças padrão cadastradas automaticamente (Filtro HEPA, Filtro de espuma, "
                    "Mangueira, Escova, Correia, Vedação).")
            st.rerun()

# --- Situação das Máquinas ---
if maquinas:
    st.divider()
    st.subheader("Situação das Máquinas")

    for maq in maquinas:
        restantes = maq["parcelas_total"] - maq["parcelas_pagas"]
        valor_restante = restantes * maq["valor_parcela"]

        with st.expander(f"🏭 {maq['nome']} {'(Quitada)' if restantes <= 0 else f'({restantes} parcelas restantes)'}"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Valor Total", f"R$ {maq['valor_total']:.2f}")
            col2.metric("Parcelas Pagas", f"{maq['parcelas_pagas']}/{maq['parcelas_total']}")
            col3.metric("Valor Restante", f"R$ {valor_restante:.2f}")

st.divider()

# --- Vida Útil das Peças ---
st.subheader("Vida Útil das Peças")

if maquinas:
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
                cor = "🔴"
                barra_cor = "red"
            elif info["status"] == "atencao":
                cor = "🟡"
                barra_cor = "orange"
            else:
                cor = "🟢"
                barra_cor = "green"

            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

            with col1:
                st.markdown(f"**{cor} {peca['nome']}** ({peca['maquina_nome']})")
                st.progress(info["percentual"] / 100,
                            text=f"{info['percentual']:.0f}% usado | {info['dias_restantes']} dias restantes")

            with col2:
                st.caption("Instalação")
                st.text(peca["data_instalacao"])

            with col3:
                st.caption("Próxima troca")
                st.text(info["data_proxima_troca"])

            with col4:
                st.caption("Custo reposição")
                st.text(f"R$ {peca['custo_reposicao']:.2f}")

            st.markdown("---")

        # --- Estimativa Anual ---
        st.subheader("Estimativa de Gasto Anual com Manutenção")
        custo_anual = {}
        for peca in pecas:
            maq_nome = peca["maquina_nome"]
            trocas_ano = 365 / peca["vida_util_dias"] if peca["vida_util_dias"] > 0 else 0
            custo = trocas_ano * peca["custo_reposicao"]
            custo_anual[maq_nome] = custo_anual.get(maq_nome, 0) + custo

        for maq_nome, custo in custo_anual.items():
            st.metric(f"Custo anual estimado - {maq_nome}", f"R$ {custo:.2f}")

        total_anual = sum(custo_anual.values())
        st.metric("Total anual (todas as máquinas)", f"R$ {total_anual:.2f}")

    else:
        st.info("Nenhuma peça cadastrada para esta máquina.")
else:
    st.info("Cadastre uma máquina acima para gerenciar suas peças.")

st.divider()

# --- Registrar Troca ---
st.subheader("Registrar Troca de Peça")

pecas_todas = db.listar_pecas()
if pecas_todas:
    with st.form("form_troca"):
        peca_opcoes = {f"{p['nome']} ({p['maquina_nome']})": p["id"] for p in pecas_todas}
        peca_sel = st.selectbox("Peça", options=list(peca_opcoes.keys()))

        peca_selecionada = next(p for p in pecas_todas if p["id"] == peca_opcoes[peca_sel])

        col1, col2 = st.columns(2)
        with col1:
            data_troca = st.date_input("Data da troca", value=date.today())
        with col2:
            custo_troca = st.number_input(
                "Custo (R$)", min_value=0.0, step=5.0,
                value=peca_selecionada["custo_reposicao"], format="%.2f",
            )

        obs_troca = st.text_input("Observações")

        if st.form_submit_button("Registrar Troca", type="primary"):
            db.registrar_troca_peca(peca_opcoes[peca_sel], data_troca.isoformat(), custo_troca, obs_troca)
            st.success(f"Troca registrada! Despesa de R$ {custo_troca:.2f} lançada automaticamente.")
            st.rerun()

    # Histórico de trocas
    st.subheader("Histórico de Trocas")
    trocas = db.listar_trocas()
    if trocas:
        df_trocas = pd.DataFrame(trocas)
        df_trocas = df_trocas.rename(columns={
            "data_troca": "Data",
            "peca_nome": "Peça",
            "maquina_nome": "Máquina",
            "custo": "Custo (R$)",
            "observacoes": "Obs",
        })
        st.dataframe(
            df_trocas[["Data", "Peça", "Máquina", "Custo (R$)", "Obs"]],
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("Nenhuma troca registrada ainda.")
