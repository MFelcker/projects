import streamlit as st
from datetime import date, datetime
import database as db

st.title("Máquinas")

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
            st.rerun()

# ---------------------------------------------------------------------------
# Situação das Máquinas (com edição)
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

            st.markdown("---")
            st.markdown("**Editar informações**")

            with st.form(f"edit_maq_{maq['id']}"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    edit_nome = st.text_input("Nome / Modelo", value=maq["nome"], key=f"en_{maq['id']}")
                    edit_data = st.date_input(
                        "Data da compra",
                        value=datetime.strptime(maq["data_compra"], "%Y-%m-%d").date() if maq["data_compra"] else date.today(),
                        key=f"ed_{maq['id']}",
                    )
                    edit_valor = st.number_input(
                        "Valor total (R$)", min_value=0.0, step=50.0,
                        value=float(maq["valor_total"]), format="%.2f", key=f"ev_{maq['id']}",
                    )
                with ec2:
                    edit_parcelas = st.number_input(
                        "Total de parcelas", min_value=0, step=1,
                        value=int(maq["parcelas_total"]), key=f"ep_{maq['id']}",
                    )
                    edit_valor_parcela = st.number_input(
                        "Valor da parcela (R$)", min_value=0.0, step=10.0,
                        value=float(maq["valor_parcela"]), format="%.2f", key=f"evp_{maq['id']}",
                    )
                    edit_pagas = st.number_input(
                        "Parcelas já pagas", min_value=0, step=1,
                        value=int(maq["parcelas_pagas"]), key=f"epp_{maq['id']}",
                    )

                if st.form_submit_button("Salvar Alterações", type="primary"):
                    db.atualizar_maquina(
                        maq["id"], edit_nome.strip(), edit_data.isoformat(),
                        edit_valor, edit_parcelas, edit_valor_parcela, edit_pagas,
                    )
                    st.success("Máquina atualizada!")
                    st.rerun()
