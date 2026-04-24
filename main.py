import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (LIMPA)
st.set_page_config(
    page_title="CPMA Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    menu_items=None
)

# 2. CSS PARA CORES E OCULTAR BARRAS DE ADM
st.markdown("""
    <style>
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stToolbar"] {display: none !important;}
    
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Estilo dos Cartões de Métricas */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 12px;
    }
    div[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 16px !important; }
    div[data-testid="stMetricValue"] { color: #39d353 !important; font-weight: bold !important; }
    
    /* Impede que o gráfico atrapalhe a rolagem da página */
    .stPlotlyChart { pointer-events: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO COM A BASE DE DADOS
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(spreadsheet=url, ttl="0")
except:
    df = pd.DataFrame(columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])

st.title("🚀 CPMA Mobile")

# 4. BARRA LATERAL (LANÇAMENTOS E META)
st.sidebar.header("⚙️ Configurações")
if 'meta_v' not in st.session_state:
    st.session_state.meta_v = 5000.0
st.session_state.meta_v = st.sidebar.number_input("Valor da Meta (R$)", value=st.session_state.meta_v, step=100.0)

with st.sidebar.expander("➕ REGISTRAR TURNO", expanded=False):
    with st.form("registro"):
        d = st.date_input("Data", datetime.now())
        a = st.selectbox("App", ["iFood", "99 Moto", "Particular", "Uber Flash"])
        rb = st.number_input("Bruto (R$)", min_value=0.0, format="%.2f")
        k = st.number_input("KM", min_value=0.0, step=0.1, format="%.1f")
        ds = st.number_input("Despesas (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("SALVAR"):
            novo = pd.DataFrame([[d.strftime('%Y-%m-%d'), a, rb, k, ds, (rb-ds)]], 
                                columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])
            df_at = pd.concat([df, novo], ignore_index=True)
            conn.update(spreadsheet=url, data=df_at)
            st.rerun()

# 5. EXIBIÇÃO DAS MÉTRICAS (VOLTARAM)
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values('Data')

    c1, c2, c3, c4 = st.columns(4)
    lucro_total = df['Lucro'].sum()
    c1.metric("Lucro Líquido", f"R$ {lucro_total:,.2f}")
    c2.metric("Receita Bruta", f"R$ {df['Bruto'].sum():,.2f}")
    c3.metric("KM Total", f"{df['KM'].sum():,.1f}")
    c4.metric("R$ / KM", f"R$ {(df['Bruto'].sum()/df['KM'].sum() if df['KM'].sum() > 0 else 0):.2f}")

    # 6. GRÁFICO PARALISADO (ESTÁTICO)
    st.subheader("📊 Performance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Bruto'], name='Bruto', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro'], name='Lucro', line=dict(color='#39d353', width=4)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Despesas'], name='Custo', line=dict(color='#f85149', width=2, dash='dot')))

    fig.update_layout(
        template="plotly_dark", hovermode=False, dragmode=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True)
    )
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

    # Meta
    st.subheader(f"🎯 Meta: R$ {st.session_state.meta_v:,.2f}")
    prog = min(lucro_total / st.session_state.meta_v, 1.0) if st.session_state.meta_v > 0 else 0
    st.progress(prog)

    # Histórico
    st.divider()
    st.subheader("📝 Histórico")
    df_ed = st.data_editor(df, use_container_width=True)
    if st.button("Confirmar Alterações"):
        conn.update(spreadsheet=url, data=df_ed)
        st.rerun()
else:
    st.info("Aguardando lançamentos...")
