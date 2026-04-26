import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO DE TELA (LAYOUT MOBILE)
st.set_page_config(page_title="CPMA Mobile", layout="wide")

# Estilo Dark e Ajustes de Layout
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
    .stPlotlyChart { pointer-events: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM GOOGLE SHEETS (Substituindo SQLite)
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler os dados da planilha
def load_data():
    return conn.read(worksheet="Página1", ttl="0") # ttl="0" força ler dado novo sempre

df = load_data()

# 3. INTERFACE PRINCIPAL
st.title("🚀 CPMA Mobile")

# Configurações fixas (Você pode ajustar a meta aqui ou criar outra aba na planilha para isso)
meta_atual = 5000.0
perc_manut = 0.05

# FORMULÁRIO DE LANÇAMENTO
with st.expander("➕ REGISTRAR NOVO TURNO", expanded=True):
    with st.form("form_mobile", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            data_input = st.date_input("Data", datetime.now())
        with col_b:
            app_input = st.selectbox("Plataforma", ["iFood", "99 Moto", "Uber", "Particular"])
        
        bruto_input = st.number_input("Ganhos Brutos (R$)", min_value=0.0, format="%.2f")
        km_input = st.number_input("KM", min_value=0.0, step=0.1, format="%.1f") 
        gastos_input = st.number_input("Combustível/Extra (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("FINALIZAR E SALVAR"):
            lucro_calc = bruto_input - gastos_input
            
            # Criar nova linha para o DataFrame
            nova_linha = pd.DataFrame([{
                "data": data_input.strftime('%Y-%m-%d'),
                "app": app_input,
                "bruto": bruto_input,
                "km": km_input,
                "despesas": gastos_input,
                "lucro": lucro_calc
            }])
            
            # Combinar com dados existentes e salvar no Google Sheets
            df_atualizado = pd.concat([df, nova_linha], ignore_index=True)
            conn.update(worksheet="Página1", data=df_atualizado)
            
            st.success("Salvo na Nuvem!")
            st.rerun()

# 4. DASHBOARD E MÉTRICAS
if not df.empty:
    # Garantir que as colunas numéricas estão corretas
    df['bruto'] = pd.to_numeric(df['bruto'])
    df['lucro'] = pd.to_numeric(df['lucro'])
    df['despesas'] = pd.to_numeric(df['despesas'])

    # Gráfico Estilo Bolsa de Valores
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['data'], y=df['bruto'], name='Bruto', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['data'], y=df['lucro'], name='Lucro Real', line=dict(color='#00ff00', width=4)))
    fig.add_trace(go.Scatter(x=df['data'], y=df['despesas'], name='Custo', line=dict(color='#ff4b4b', dash='dot')))
    
    fig.update_layout(
        template="plotly_dark", height=300, 
        margin=dict(l=0,r=0,t=20,b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        dragmode=False, hovermode=False,
        xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

    # CÁLCULOS
    manutencao_acumulada = df['bruto'].sum() * perc_manut
    lucro_total = df['lucro'].sum()

    # BLOCOS DE MÉTRICAS
    m1, m2, m3 = st.columns(3)
    m1.metric("Lucro Total", f"R$ {lucro_total:,.2f}")
    m2.metric("Manutenção", f"R$ {manutencao_acumulada:,.2f}")
    m3.metric("Meta", f"{(lucro_total/meta_atual)*100:.1f}%")

    # Histórico
    st.subheader("📋 Histórico")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Botão para limpar/reiniciar (Cuidado: isso apaga a planilha!)
    if st.button("Limpar Dados da Nuvem"):
        if st.checkbox("Tenho certeza que quero apagar tudo"):
            df_vazio = pd.DataFrame(columns=["data", "app", "bruto", "km", "despesas", "lucro"])
            conn.update(worksheet="Página1", data=df_vazio)
            st.rerun()
else:
    st.info("Aguardando o primeiro registro na nuvem...")
