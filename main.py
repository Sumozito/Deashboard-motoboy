import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuração e Estilo Dark
st.set_page_config(page_title="CPMA Pro - Gestão de Ativos", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #00ff00 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# URL da sua planilha (Versão Exportação CSV para evitar erros de login)
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60) # Atualiza os dados a cada 1 minuto
def carregar_dados():
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame(columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])

df = carregar_dados()

if 'meta_valor' not in st.session_state:
    st.session_state.meta_valor = 5000.0

st.title("📈 CPMA - Dashboard Profissional")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configurações")
st.session_state.meta_valor = st.sidebar.number_input("Meta (R$)", value=st.session_state.meta_valor, step=100.0)

with st.sidebar.expander("➕ Lançar Novo Turno"):
    with st.form("add_registro"):
        d = st.date_input("Data", datetime.now())
        a = st.selectbox("App", ["iFood", "99 Moto", "Particular"])
        rb = st.number_input("Bruto (R$)", min_value=0.0, format="%.2f")
        k = st.number_input("KM Rodado", min_value=0.0, step=0.1)
        ds = st.number_input("Despesas (R$)", min_value=0.0)
        
        if st.form_submit_button("Salvar Turno"):
            # Aqui você pode copiar os dados e colar na planilha manualmente se a conexão falhar
            st.warning("⚠️ Para salvar permanentemente neste modelo simplificado, adicione a linha na planilha. Em breve ativaremos o salvamento automático via API.")
            st.write(f"Sugestão de linha: {d}, {a}, {rb}, {k}, {ds}, {rb-ds}")

# --- GRÁFICO ESTILO BOLSA ---
if not df.empty and len(df) > 1:
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values('Data')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Bruto'], name='Bruto', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro'], name='Lucro Real', line=dict(color='#2ea043', width=4)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Despesas'], name='Gastos', line=dict(color='#da3633', dash='dot')))
    
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Métricas
    c1, c2, c3 = st.columns(3)
    lucro_total = df['Lucro'].sum()
    c1.metric("Lucro Acumulado", f"R$ {lucro_total:,.2f}")
    c2.metric("Meta", f"R$ {st.session_state.meta_valor:,.2f}")
    c3.metric("Progresso", f"{(lucro_total/st.session_state.meta_valor)*100:.1f}%")
else:
    st.info("📊 Os dados serão carregados assim que você preencher as primeiras linhas na sua Planilha do Google e o acesso estiver como 'Qualquer pessoa com o link'.")

st.subheader("📋 Visualização da Base de Dados")
st.dataframe(df, use_container_width=True)
