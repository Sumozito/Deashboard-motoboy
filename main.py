import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (VISUAL LIMPO E SEM ADM)
st.set_page_config(
    page_title="CPMA Mobile",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# 2. CSS PARA OCULTAR TODA A BARRA SUPERIOR E ADM
st.markdown("""
    <style>
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {display: none !important;}
    .block-container { padding-top: 1rem !important; background-color: #0e1117; }
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 3. INICIALIZAÇÃO DOS DADOS (EVITA O NAMEERROR)
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Criamos o 'df' aqui para garantir que ele sempre exista
try:
    df = conn.read(spreadsheet=url, ttl="0")
except Exception:
    df = pd.DataFrame(columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])

st.title("🚀 CPMA Mobile")

# --- BARRA LATERAL PARA LANÇAMENTOS ---
with st.sidebar.expander("➕ REGISTRAR NOVO TURNO", expanded=False):
    with st.form("registro"):
        d = st.date_input("Data", datetime.now())
        a = st.selectbox("Plataforma", ["iFood", "99 Moto", "Uber", "Particular"])
        rb = st.number_input("Ganhos Brutos (R$)", min_value=0.0, format="%.2f")
        k = st.number_input("KM", min_value=0.0, step=0.1, format="%.1f")
        ds = st.number_input("Combustível/Extra (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("FINALIZAR E SALVAR"):
            novo = pd.DataFrame([[d.strftime('%Y-%m-%d'), a, rb, k, ds, (rb-ds)]], 
                                columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])
            df_atualizado = pd.concat([df, novo], ignore_index=True)
            conn.update(spreadsheet=url, data=df_atualizado)
            st.rerun()

# --- GRÁFICO E HISTÓRICO ---
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values('Data')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Bruto'], name='Bruto', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro'], name='Lucro Real', line=dict(color='#39d353', width=4)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Despesas'], name='Custo', line=dict(color='#f85149', width=2, dash='dot')))

    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#30363d')
    )

    # config={'displayModeBar': False} remove a barra de ferramentas do gráfico que você circulou
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.divider()
    st.subheader("📝 Histórico")
    df_edit = st.data_editor(df, use_container_width=True)
    if st.button("Confirmar Edição"):
        conn.update(spreadsheet=url, data=df_edit)
        st.rerun()
else:
    st.info("Aguardando o primeiro lançamento para gerar o gráfico.")
