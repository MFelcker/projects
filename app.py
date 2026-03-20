import streamlit as st
import database as db

st.set_page_config(
    page_title="Gestão Extratoras",
    page_icon="🧹",
    layout="wide",
)

db.init_db()

pages = st.navigation({
    "Operações": [
        st.Page("pages/01_alugueis.py", title="Aluguéis", icon="📋"),
        st.Page("pages/02_despesas.py", title="Despesas", icon="💸"),
        st.Page("pages/03_estoque.py", title="Estoque", icon="📦"),
    ],
    "Análises": [
        st.Page("pages/04_dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/05_previsoes.py", title="Previsões", icon="🔮"),
    ],
    "Máquinas": [
        st.Page("pages/06_manutencao.py", title="Manutenção", icon="🔧"),
    ],
})

pages.run()
