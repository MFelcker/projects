import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import database as db

st.title("Redes Sociais")

# ---------------------------------------------------------------------------
# Registrar Métricas
# ---------------------------------------------------------------------------
st.subheader("Registrar Métricas do Instagram")

with st.form("form_rede_social", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        data_registro = st.date_input("Data", value=date.today())
        seguidores = st.number_input("Total de seguidores", min_value=0, step=1, value=0)
        novos_seguidores = st.number_input("Novos seguidores (no período)", min_value=0, step=1, value=0)

    with col2:
        postagens = st.number_input("Postagens publicadas", min_value=0, step=1, value=0)
        curtidas = st.number_input("Curtidas (total no período)", min_value=0, step=1, value=0)
        comentarios = st.number_input("Comentários (total no período)", min_value=0, step=1, value=0)

    with col3:
        alcance = st.number_input("Alcance (contas alcançadas)", min_value=0, step=1, value=0)
        observacoes = st.text_area("Observações", height=118)

    if st.form_submit_button("Registrar Métricas", type="primary", use_container_width=True):
        db.registrar_rede_social(
            data_registro.isoformat(), "instagram", seguidores, postagens,
            curtidas, comentarios, alcance, novos_seguidores, observacoes.strip(),
        )
        st.success("Métricas registradas!")
        st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Histórico e Gráficos
# ---------------------------------------------------------------------------
st.subheader("Histórico de Métricas")

col_f1, col_f2 = st.columns(2)
with col_f1:
    filtro_ini = st.date_input("De", value=date.today() - timedelta(days=90), key="rs_ini")
with col_f2:
    filtro_fim = st.date_input("Até", value=date.today(), key="rs_fim")

registros = db.listar_redes_sociais(
    plataforma="instagram",
    data_inicio=filtro_ini.isoformat(),
    data_fim=filtro_fim.isoformat(),
)

if registros:
    # KPIs do registro mais recente
    ultimo = registros[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seguidores", f"{ultimo['seguidores']:,}")
    c2.metric("Postagens (último)", ultimo["postagens"])
    c3.metric("Curtidas (último)", f"{ultimo['curtidas']:,}")
    c4.metric("Alcance (último)", f"{ultimo['alcance']:,}")

    # Gráficos
    df = pd.DataFrame(registros).sort_values("data")

    if len(df) >= 2:
        st.subheader("Evolução")

        tab1, tab2 = st.tabs(["Seguidores", "Engajamento"])

        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["data"], y=df["seguidores"],
                mode="lines+markers", name="Seguidores",
                line=dict(color="#3AA8D8", width=3),
            ))
            if df["novos_seguidores"].sum() > 0:
                fig.add_trace(go.Bar(
                    x=df["data"], y=df["novos_seguidores"],
                    name="Novos seguidores", marker_color="#7DC8E8", opacity=0.6,
                ))
            fig.update_layout(
                xaxis_title="Data", yaxis_title="Quantidade",
                template="plotly_white", height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df["data"], y=df["curtidas"],
                mode="lines+markers", name="Curtidas",
                line=dict(color="#1A6B9C", width=2),
            ))
            fig2.add_trace(go.Scatter(
                x=df["data"], y=df["comentarios"],
                mode="lines+markers", name="Comentários",
                line=dict(color="#27AE60", width=2),
            ))
            fig2.add_trace(go.Scatter(
                x=df["data"], y=df["alcance"],
                mode="lines+markers", name="Alcance",
                line=dict(color="#F39C12", width=2),
            ))
            fig2.update_layout(
                xaxis_title="Data", yaxis_title="Quantidade",
                template="plotly_white", height=350,
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Histórico editável
    st.subheader("Registros")

    for r in registros:
        label = (
            f"{r['data']} — {r['seguidores']:,} seg. | "
            f"{r['postagens']} posts | {r['curtidas']:,} curtidas"
        )

        with st.expander(label):
            with st.form(f"edit_rs_{r['id']}"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    e_data = st.date_input("Data", value=date.fromisoformat(r["data"]), key=f"rsd_{r['id']}")
                    e_seg = st.number_input("Seguidores", min_value=0, value=int(r["seguidores"]), key=f"rss_{r['id']}")
                    e_novos = st.number_input("Novos seguidores", min_value=0, value=int(r["novos_seguidores"]), key=f"rsn_{r['id']}")
                with ec2:
                    e_post = st.number_input("Postagens", min_value=0, value=int(r["postagens"]), key=f"rsp_{r['id']}")
                    e_curt = st.number_input("Curtidas", min_value=0, value=int(r["curtidas"]), key=f"rsc_{r['id']}")
                    e_com = st.number_input("Comentários", min_value=0, value=int(r["comentarios"]), key=f"rsco_{r['id']}")
                with ec3:
                    e_alc = st.number_input("Alcance", min_value=0, value=int(r["alcance"]), key=f"rsa_{r['id']}")
                    e_obs = st.text_input("Observações", value=r["observacoes"] or "", key=f"rso_{r['id']}")

                fc1, fc2 = st.columns([3, 1])
                salvar = fc1.form_submit_button("Salvar Alterações", type="primary")
                excluir = fc2.form_submit_button("Excluir")

                if salvar:
                    db.atualizar_rede_social(
                        r["id"], e_data.isoformat(), e_seg, e_post,
                        e_curt, e_com, e_alc, e_novos, e_obs.strip(),
                    )
                    st.success("Registro atualizado!")
                    st.rerun()
                if excluir:
                    db.excluir_rede_social(r["id"])
                    st.success("Registro excluído!")
                    st.rerun()
else:
    st.info("Nenhum registro encontrado. Comece registrando as métricas do seu Instagram!")
