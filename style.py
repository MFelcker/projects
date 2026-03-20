"""
Identidade visual e constantes compartilhadas - Operário Serviços e Locações.
Paleta extraída da logo: azul marinho + azul claro.
"""

# ---------------------------------------------------------------------------
# Paleta de cores
# ---------------------------------------------------------------------------
NAVY = "#14375A"
BLUE = "#1A6B9C"
ACCENT = "#3AA8D8"
LIGHT_BLUE = "#7DC8E8"
BG_LIGHT = "#F0F6FB"
WHITE = "#FFFFFF"
SUCCESS = "#27AE60"
DANGER = "#E74C3C"
WARNING = "#F39C12"

# Cores para gráficos Plotly
CHART_COLORS = [ACCENT, NAVY, LIGHT_BLUE, SUCCESS, WARNING, DANGER, "#8E44AD", "#E67E22"]
RECEITA_COR = ACCENT
DESPESA_COR = DANGER
LUCRO_COR = SUCCESS
NEUTRO_COR = NAVY

# ---------------------------------------------------------------------------
# Categorias de despesas (fonte única de verdade)
# ---------------------------------------------------------------------------
CATEGORIAS = {
    "produto": "Produto de limpeza",
    "parcela_maquina": "Parcela da máquina",
    "manutencao": "Manutenção",
    "marketing": "Marketing / Tráfego",
    "suprimentos": "Suprimentos",
    "outros": "Outros",
}

# ---------------------------------------------------------------------------
# CSS customizado
# ---------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
    /* --- Importar fonte --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* --- Geral --- */
    html, body, .stApp {{
        font-family: 'Inter', sans-serif;
    }}

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, #1E4D78 100%);
    }}
    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stSelectbox label {{
        color: {LIGHT_BLUE} !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15) !important;
    }}

    /* --- Logo no sidebar --- */
    .sidebar-logo {{
        text-align: center;
        padding: 1.2rem 0 0.5rem 0;
    }}
    .sidebar-logo img {{
        max-width: 140px;
        border-radius: 12px;
    }}
    .sidebar-brand {{
        text-align: center;
        padding: 0.5rem 0 0.2rem 0;
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: 3px;
        color: {WHITE} !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    .sidebar-subtitle {{
        text-align: center;
        font-size: 0.65rem;
        font-weight: 500;
        letter-spacing: 2px;
        color: {LIGHT_BLUE} !important;
        margin-bottom: 1rem;
    }}

    /* --- Títulos --- */
    h1 {{
        color: {NAVY} !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        border-bottom: 3px solid {ACCENT};
        padding-bottom: 0.5rem !important;
    }}
    h2, h3 {{
        color: {NAVY} !important;
        font-weight: 600 !important;
    }}

    /* --- Metric cards --- */
    div[data-testid="stMetric"] {{
        background: {WHITE};
        border: 1px solid #E2EBF3;
        border-left: 4px solid {ACCENT};
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 3px rgba(20,55,90,0.08);
    }}
    div[data-testid="stMetric"] label {{
        color: {BLUE} !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {NAVY} !important;
        font-weight: 700 !important;
    }}

    /* --- Botões --- */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {ACCENT} 0%, {BLUE} 100%) !important;
        color: {WHITE} !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(58,168,216,0.3);
    }}
    .stFormSubmitButton > button:hover {{
        box-shadow: 0 4px 12px rgba(58,168,216,0.4) !important;
        transform: translateY(-1px);
    }}
    .stButton > button:not([kind="primary"]) {{
        border: 1.5px solid {ACCENT} !important;
        color: {ACCENT} !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        background: {WHITE} !important;
    }}
    .stButton > button:not([kind="primary"]):hover {{
        background: {BG_LIGHT} !important;
    }}

    /* --- Forms --- */
    div[data-testid="stForm"] {{
        background: {BG_LIGHT};
        border: 1px solid #D6E4F0;
        border-radius: 12px;
        padding: 1.2rem;
    }}

    /* --- Expanders --- */
    details[data-testid="stExpander"] {{
        border: 1px solid #D6E4F0 !important;
        border-radius: 8px !important;
        background: {WHITE};
    }}
    details[data-testid="stExpander"] summary {{
        font-weight: 500;
    }}

    /* --- DataFrames --- */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
    }}

    /* --- Progress bar --- */
    .stProgress > div > div {{
        background-color: {ACCENT} !important;
    }}

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab"] {{
        color: {NAVY};
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom-color: {ACCENT} !important;
        color: {ACCENT} !important;
    }}

    /* --- Alerts com bordas suaves --- */
    .stAlert {{
        border-radius: 8px !important;
    }}

    /* --- Divider --- */
    hr {{
        border-color: #D6E4F0 !important;
    }}

    /* --- Esconde link de âncora dos headers --- */
    .stMarkdown a[href^="#"] {{
        display: none !important;
    }}
</style>
"""


def inject_css():
    """Injeta o CSS customizado na página."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar_brand():
    """Renderiza a marca no sidebar."""
    import streamlit as st
    import os

    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

    with st.sidebar:
        if os.path.exists(logo_path):
            st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
            st.image(logo_path, width=140)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sidebar-brand">OPERARIO</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="sidebar-subtitle">SERVI\u00c7OS E LOCA\u00c7\u00d5ES</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
