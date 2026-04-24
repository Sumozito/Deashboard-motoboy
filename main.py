import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="CPMA Mobile",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS ESPECÍFICO PARA OCULTAR APENAS O QUE VOCÊ CIRCULOU
st.markdown("""
    <style>
    /* Esconde botões de Share, Star e GitHub, mas mantém o menu de 3 linhas */
    header[data-testid="stHeader"] > div:first-child {
        visibility: hidden;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    
    /* Esconde o rodapé 'Made with Streamlit' */
    footer {visibility: hidden;}
    
    /* Remove a barra flutuante de edição (stToolbar) */
    div[data-testid="stToolbar"] {display: none !important;}

    /* Estilização geral */
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO COM GOOGLE SHEETS
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(spreadsheet=url, ttl="0")
except:
    df = pd.DataFrame(columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])

st.title("🚀 CPMA Mobile")

# --- BARRA LATERAL (LANÇAMENTOS E METAS) ---
# Agora o botão de 3 linhas vai funcionar para abrir aqui
st.sidebar.header("⚙️ Painel de Controle")

if 'meta_valor' not in st.session_state:
    st.session_state.meta_valor = 5000.0
st.session_state.meta_valor = st.sidebar.number_input("Valor da Meta (R$)", value=st.session_state.meta_valor, step=100.0)

with st.sidebar.expander("➕ REGISTRAR TURNO", expanded=False):
    with st.form("registro"):
        d = st.date_input("Data", datetime.now())
        a = st.selectbox("App", ["iFood", "99 Moto", "Uber", "Particular"])
        rb = st.number_input("Ganhos Brutos (R$)", min_value=0.0, format="%.2f")
        k = st.number_input("KM Rodado", min_value=0.0, step=0.1, format="%.1f")
        ds = st.number_input("Despesas (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("SALVAR NO HISTÓRICO"):
            novo = pd.DataFrame([[d.strftime('%Y-%m-%d'), a, rb, k, ds, (rb-ds)]], 
                                columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])
            df_atualizado = pd.concat([df, novo], ignore_index=True)
            conn.update(spreadsheet=url, data=df_atualizado)
            st.sidebar.success("Salvo!")
            st.rerun()

# --- DASHBOARD ---
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values('Data')

    # Métricas
    lucro_total = df['Lucro'].sum()
    c1, c2 = st.columns(2)
    c1.metric("Lucro Líquido", f"R$ {lucro_total:,.2f}")
    c2.metric("KM Total", f"{df['KM'].sum():,.1f} km")

    # Gráfico de Linhas (Sem barra de ferramentas)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Bruto'], name='Bruto', line=dict(color='#1f77b4')))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro'], name='Lucro', line=dict(color='#39d353', width=4)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Despesas'], name='Custo', line=dict(color='#f85149', dash='dot')))

    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Meta
    st.write(f"### Meta: {st.session_state.meta_valor:,.2f}")
    prog = min(lucro_total / st.session_state.meta_valor, 1.0) if st.session_state.meta_valor > 0 else 0
    st.progress(prog)

    # Histórico Editável
    st.divider()
    st.subheader("📝 Editar Histórico")
    df_edit = st.data_editor(df, use_container_width=True)
    if st.button("CONFIRMAR EDIÇÕES"):
        conn.update(spreadsheet=url, data=df_edit)
        st.success("Atualizado!")
        st.rerun()
