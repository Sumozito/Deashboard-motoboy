import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA (FOCO EM CELULAR)
st.set_page_config(page_title="CPMA App", layout="wide")

# Estilo Dark Mode Profissional
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 15px; 
        padding: 10px;
    }
    div[data-testid="stMetricValue"] { color: #00ff00 !important; font-size: 24px !important; }
    .stButton>button { width: 100%; border-radius: 10px; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS INTERNO (SQLITE)
def init_db():
    conn = sqlite3.connect('entregas.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS turnos 
                 (data TEXT, app TEXT, bruto REAL, km REAL, despesas REAL, lucro REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (meta REAL)''')
    # Inicia meta padrão se não existir
    c.execute("SELECT meta FROM config")
    if not c.fetchone():
        c.execute("INSERT INTO config VALUES (5000.0)")
    conn.commit()
    return conn

conn = init_db()

# Funções de Dados
def salvar_turno(d, a, b, k, ds):
    lucro = b - ds
    c = conn.cursor()
    c.execute("INSERT INTO turnos VALUES (?,?,?,?,?,?)", (d, a, b, k, ds, lucro))
    conn.commit()

def atualizar_meta(nova_meta):
    c = conn.cursor()
    c.execute("UPDATE config SET meta = ?", (nova_meta,))
    conn.commit()

# 3. INTERFACE DO APP
st.title("🚀 CPMA Mobile")

# Carregar Configurações
meta_atual = pd.read_sql("SELECT meta FROM config", conn).iloc[0]['meta']

# ABA DE LANÇAMENTO (COMO UM APP)
with st.expander("➕ REGISTRAR NOVO TURNO", expanded=True):
    with st.form("form_app", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", datetime.now())
        with col2:
            app = st.selectbox("Plataforma", ["iFood", "99 Moto", "Uber", "Particular"])
        
        bruto = st.number_input("Ganhos Brutos (R$)", min_value=0.0, step=10.0, format="%.2f")
        km = st.number_input("Quilometragem (KM)", min_value=0.0, step=0.1, format="%.1f")
        gastos = st.number_input("Combustível/Extra (R$)", min_value=0.0, step=5.0, format="%.2f")
        
        if st.form_submit_button("FINALIZAR E SALVAR"):
            salvar_turno(data.strftime('%Y-%m-%d'), app, bruto, km, gastos)
            st.success("Turno salvo com sucesso!")
            st.rerun()

# 4. DASHBOARD DE PERFORMANCE
df = pd.read_sql("SELECT * FROM turnos ORDER BY data ASC", conn)

if not df.empty:
    # Gráfico de Linhas (Bolsa de Valores)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['data'], y=df['bruto'], name='Bruto', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['data'], y=df['lucro'], name='Lucro', line=dict(color='#00ff00', width=4)))
    fig.add_trace(go.Scatter(x=df['data'], y=df['despesas'], name='Custo', line=dict(color='#ff4b4b', dash='dot')))
    
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=20,b=0),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    # Métricas
    lucro_total = df['lucro'].sum()
    c1, c2 = st.columns(2)
    c1.metric("Lucro Total", f"R$ {lucro_total:,.2f}")
    
    # Meta Editável Direto
    nova_meta = c2.number_input("Meta (R$)", value=float(meta_atual), step=100.0)
    if nova_meta != meta_atual:
        atualizar_meta(nova_meta)
        st.rerun()

    # Barra de Progresso
    progresso = min(lucro_total / nova_meta, 1.0) if nova_meta > 0 else 0
    st.progress(progresso)
    st.caption(f"Faltam R$ {(nova_meta - lucro_total):,.2f} para o objetivo.")

    # Histórico Editável
    st.subheader("📋 Histórico")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", hide_index=True)
    if st.button("CONFIRMAR EDIÇÕES NO BANCO"):
        edited_df.to_sql('turnos', conn, if_exists='replace', index=False)
        st.success("Banco de dados atualizado!")
        st.rerun()
else:
    st.info("Nenhum dado registrado. Comece lançando seu primeiro turno acima!")
