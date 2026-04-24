import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuração e Estilo
st.set_page_config(page_title="CPMA Pro - Gestão de Ativos", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; }
    div[data-testid="stMetricValue"] { color: #238636 !important; }
    </style>
    """, unsafe_allow_html=True)

# CONEXÃO COM GOOGLE SHEETS 
# O link abaixo é da sua planilha "Base de Dados Dashboard Motoboy"
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Carregar dados da planilha
df = conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5,6], ttl="0")
meta_valor = 5000.0 # Valor padrão caso a planilha esteja vazia

st.title("📈 CPMA - Dashboard Profissional")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Gestão de Dados")
nova_meta = st.sidebar.number_input("Ajustar Meta (R$)", value=meta_valor, step=100.0)

with st.sidebar.expander("➕ Novo Lançamento"):
    with st.form("registro"):
        d = st.date_input("Data", datetime.now())
        a = st.selectbox("App", ["iFood", "99 Moto", "Particular"])
        rb = st.number_input("Faturamento Bruto", min_value=0.0, format="%.2f")
        k = st.number_input("KM Rodado", min_value=0.0, step=0.1)
        ds = st.number_input("Despesas", min_value=0.0)
        
        if st.form_submit_button("Salvar Permanentemente"):
            # Lógica para salvar na planilha 
            novo_dado = pd.DataFrame([[d.strftime('%Y-%m-%d'), a, rb, k, ds, (rb - ds)]], 
                                     columns=['Data', 'Plataforma', 'Receita Bruta (R$)', 'KM Rodado', 'Gasolina (R$)', 'Lucro Líquido (R$)'])
            df_atualizado = pd.concat([df, novo_dado], ignore_index=True)
            conn.update(spreadsheet=url, data=df_atualizado)
            st.sidebar.success("Dados salvos na nuvem!")
            st.rerun()

# --- GRÁFICO ESTILO BOLSA DE VALORES ---
if not df.empty:
    st.subheader("Gráfico de Performance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Receita Bruta (R$)'], name='Bruto', line=dict(color='#1f77b4')))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro Líquido (R$)'], name='Lucro Real', line=dict(color='#2ea043', width=4)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Gasolina (R$)'], name='Custo', line=dict(color='#da3633', dash='dot')))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Histórico Editável direto no Dashboard
    st.subheader("📝 Editar Histórico")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("Confirmar Edições"):
        conn.update(spreadsheet=url, data=edited_df)
        st.success("Planilha atualizada!")
