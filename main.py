import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA (LAYOUT MOBILE)
st.set_page_config(page_title="CPMA Mobile", layout="wide")

# Estilo Dark e Ajustes de Layout Antigo
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetric"] { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 10px;
    }
    div[data-testid="stMetricValue"] { color: #00ff00 !important; font-size: 22px !important; }
    .stButton>button { width: 100%; border-radius: 8px; height: 45px; background-color: #2ea043; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS (SQLITE)
def init_db():
    conn = sqlite3.connect('entregas.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS turnos 
                 (data TEXT, app TEXT, bruto REAL, km REAL, despesas REAL, lucro REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (meta REAL, perc_manut REAL)''')
    c.execute("SELECT meta FROM config")
    if not c.fetchone():
        c.execute("INSERT INTO config VALUES (5000.0, 0.05)") # Meta e 5% para manutenção
    conn.commit()
    return conn

conn = init_db()

# 3. INTERFACE PRINCIPAL
st.title("🚀 CPMA Mobile")

# Carregar Configurações
config_df = pd.read_sql("SELECT * FROM config", conn)
meta_atual = float(config_df.iloc[0]['meta'])
perc_manut = float(config_df.iloc[0]['perc_manut'])

# FORMULÁRIO DE LANÇAMENTO (LAYOUT INTEGRADO)
with st.expander("➕ REGISTRAR NOVO TURNO", expanded=True):
    with st.form("form_mobile", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            data = st.date_input("Data", datetime.now())
        with col_b:
            app = st.selectbox("Plataforma", ["iFood", "99 Moto", "Uber", "Particular"])
        
        bruto = st.number_input("Ganhos Brutos (R$)", min_value=0.0, format="%.2f")
        km = st.number_input("KM", min_value=0.0, step=0.1, format="%.1f") # Ajustado para apenas KM
        gastos = st.number_input("Combustível/Extra (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("FINALIZAR E SALVAR"):
            lucro = bruto - gastos
            c = conn.cursor()
            c.execute("INSERT INTO turnos VALUES (?,?,?,?,?,?)", 
                      (data.strftime('%Y-%m-%d'), app, bruto, km, gastos, lucro))
            conn.commit()
            st.success("Salvo!")
            st.rerun()

# 4. DASHBOARD E MÉTRICAS
df = pd.read_sql("SELECT * FROM turnos ORDER BY data ASC", conn)

if not df.empty:
    # Gráfico de Linhas (Bolsa de Valores) - Estilo Antigo
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['data'], y=df['bruto'], name='Bruto', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['data'], y=df['lucro'], name='Lucro Real', line=dict(color='#00ff00', width=4)))
    fig.add_trace(go.Scatter(x=df['data'], y=df['despesas'], name='Custo', line=dict(color='#ff4b4b', dash='dot')))
    
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=20,b=0),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    # CÁLCULO DE MANUTENÇÃO (Ex: 5% do Bruto acumulado)
    manutencao_acumulada = df['bruto'].sum() * perc_manut
    lucro_total = df['lucro'].sum()

    # BLOCOS DE MÉTRICAS (Layout Antigo)
    m1, m2, m3 = st.columns(3)
    m1.metric("Lucro Total", f"R$ {lucro_total:,.2f}")
    m2.metric("Fundo Manutenção", f"R$ {manutencao_acumulada:,.2f}", delta="Reserva")
    m3.metric("Progresso Meta", f"{(lucro_total/meta_atual)*100:.1f}%")

    # Meta Editável
    st.divider()
    nova_meta = st.number_input("Ajustar Meta (R$)", value=meta_atual, step=100.0)
    if nova_meta != meta_atual:
        c = conn.cursor()
        c.execute("UPDATE config SET meta = ?", (nova_meta,))
        conn.commit()
        st.rerun()

    # Histórico para edição rápida
    st.subheader("📋 Histórico")
    st.data_editor(df, use_container_width=True, hide_index=True)
else:
    st.info("Aguardando o primeiro registro...")
