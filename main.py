import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuração de Layout
st.set_page_config(page_title="CPMA Pro", layout="wide")

# Estilo Dark Mode e Cores
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# URL da sua planilha (Versão CSV direta)
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/gviz/tq?tqx=out:csv"

def carregar_dados():
    try:
        # Lê a planilha
        data = pd.read_csv(url)
        # Se a planilha tiver dados, garante que a coluna Data seja tratada como data
        if not data.empty and 'Data' in data.columns:
            data['Data'] = pd.to_datetime(data['Data'], errors='coerce')
            data = data.dropna(subset=['Data'])
        return data
    except:
        # Se der erro ou estiver vazia, cria o modelo limpo
        return pd.DataFrame(columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])

df = carregar_dados()

# Sidebar para Metas e Lançamentos
if 'meta' not in st.session_state: st.session_state.meta = 5000.0

st.sidebar.header("⚙️ Configurações")
st.session_state.meta = st.sidebar.number_input("Sua Meta (R$)", value=st.session_state.meta, step=100.0)

st.title("📈 CPMA - Dashboard Profissional")

# --- GRÁFICO ESTILO BOLSA ---
if not df.empty and len(df) >= 1:
    df = df.sort_values('Data')
    
    fig = go.Figure()
    # Linha Azul (Bruto)
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Bruto'], name='Faturamento Bruto', line=dict(color='#1f77b4', width=2)))
    # Linha Verde Grossa (Lucro Líquido)
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro'], name='Lucro Real', line=dict(color='#00ff00', width=5)))
    # Linha Vermelha Pontilhada (Gastos)
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Despesas'], name='Despesas', line=dict(color='#ff4b4b', width=2, dash='dot')))

    fig.update_layout(template="plotly_dark", hovermode="x unified", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Métricas Rápidas
    c1, c2, c3 = st.columns(3)
    total_lucro = df['Lucro'].sum()
    c1.metric("Lucro Acumulado", f"R$ {total_lucro:,.2f}")
    c2.metric("Meta Objetivo", f"R$ {st.session_state.meta:,.2f}")
    c3.metric("Progresso", f"{(total_lucro/st.session_state.meta)*100:.1f}%")
else:
    st.warning("⚠️ Planilha vazia ou títulos incorretos. Adicione os títulos: Data, App, Bruto, KM, Despesas, Lucro na primeira linha da sua planilha.")

# Histórico Editável
st.subheader("📝 Histórico e Edição")
st.data_editor(df, use_container_width=True)
