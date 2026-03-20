import streamlit as st
import database as db
from style import inject_css, render_sidebar_brand

st.set_page_config(
    page_title="Operário - Gestão",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
db.init_db()
render_sidebar_brand()

pages = st.navigation({
    "Operações": [
        st.Page("pages/01_alugueis.py", title="Aluguéis", icon=":material/assignment:"),
        st.Page("pages/02_despesas.py", title="Despesas", icon=":material/payments:"),
        st.Page("pages/03_estoque.py", title="Estoque", icon=":material/inventory_2:"),
    ],
    "Análises": [
        st.Page("pages/04_dashboard.py", title="Dashboard", icon=":material/bar_chart:"),
        st.Page("pages/05_previsoes.py", title="Previsões", icon=":material/trending_up:"),
    ],
    "Máquinas": [
        st.Page("pages/06_manutencao.py", title="Manutenção", icon=":material/build:"),
    ],
})

pages.run()
