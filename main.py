import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuração de Layout e Estilo Dark Profissional
st.set_page_config(page_title="CPMA Pro - Gestão", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #00ff00 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# URL da sua planilha convertida para CSV
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/gviz/tq?tqx=out:csv"

def carregar_dados():
    try:
        data = pd.read_csv(url)
        # Limpeza: remove colunas ou linhas que contenham códigos HTML por erro
        data = data[~data.stack().str.contains('<').unstack().any(axis=1)]
        return data
    except:
        return pd.DataFrame(columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])

df = carregar_dados()
if 'meta' not in st.session_state: st.session_state.meta = 5000.0

st.sidebar.header("⚙️ Configurações")
st.session_state.meta = st.sidebar.number_input("Meta de Lucro (R$)", value=st.session_state.meta, step=100.0)

st.title("📈 CPMA - Dashboard Profissional")

# --- GRÁFICO ESTILO BOLSA DE VALORES ---
# Só exibe se houver dados válidos na coluna Data
if not df.empty and 'Data' in df.columns and len(df.dropna(subset=['Data'])) > 0:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data']).sort_values('Data')

    fig = go.Figure()
    # Faturamento Bruto (Azul)
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Bruto'], name='Bruto', line=dict(color='#1f77b4', width=2)))
    # Lucro Líquido (Verde vibrante - Destaque)
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro'], name='Lucro Real', line=dict(color='#00ff00', width=5)))
    # Despesas (Vermelho pontilhado)
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Despesas'], name='Despesas', line=dict(color='#ff4b4b', width=2, dash='dot')))

    fig.update_layout(template="plotly_dark", hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Métricas de Resumo
    c1, c2, c3 = st.columns(3)
    lucro_total = pd.to_numeric(df['Lucro'], errors='coerce').sum()
    c1.metric("Lucro Total", f"R$ {lucro_total:,.2f}")
    c2.metric("Meta", f"R$ {st.session_state.meta:,.2f}")
    c3.metric("Progresso", f"{(lucro_total/st.session_state.meta)*100:.1f}%")
else:
    st.warning("⚠️ Planilha lida, mas sem dados válidos. Limpe sua planilha e use apenas a primeira linha para os títulos: Data, App, Bruto, KM, Despesas, Lucro.")

st.subheader("📝 Histórico")
st.data_editor(df, use_container_width=True)
