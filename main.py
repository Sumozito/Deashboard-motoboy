import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (VISUAL LIMPO)
st.set_page_config(
    page_title="CPMA Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# 2. CSS PARA CORES, CONTRASTE E ESCONDER OPÇÕES DE ADM
st.markdown("""
    <style>
    /* Esconder menus de desenvolvedor */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    
    /* Fundo Escuro e Cartões de Alto Contraste */
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 2px solid #30363d;
        padding: 15px;
        border-radius: 12px;
    }
    div[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 16px !important; }
    div[data-testid="stMetricValue"] { color: #39d353 !important; font-weight: bold !important; }
    
    /* Estilo da Tabela e Inputs */
    .stTable { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO COM A BASE DE DADOS (GOOGLE SHEETS)
# Substitua pela sua URL se necessário, mas o sistema lerá das "Secrets"
url = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Carregar dados
try:
    df = conn.read(spreadsheet=url, ttl="0")
except:
    df = pd.DataFrame(columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])

st.title("📈 CPMA - Gestão Profissional")

# 4. BARRA LATERAL (CONFIGURAÇÕES E LANÇAMENTOS)
st.sidebar.header("⚙️ Painel de Controle")

# Meta Editável
if 'meta_valor' not in st.session_state:
    st.session_state.meta_valor = 5000.0
st.session_state.meta_valor = st.sidebar.number_input("Ajustar Valor da Meta (R$)", value=st.session_state.meta_valor, step=100.0)

with st.sidebar.expander("➕ Lançar Novo Dia"):
    with st.form("novo_registro"):
        data_f = st.date_input("Data", datetime.now())
        app_f = st.selectbox("Plataforma", ["iFood", "99 Moto", "Particular", "Uber Flash"])
        bruto_f = st.number_input("Receita Bruta (R$)", min_value=0.0, format="%.2f")
        km_f = st.number_input("KM Rodado (ex: 21.9)", min_value=0.0, step=0.1, format="%.1f")
        desp_f = st.number_input("Despesas (Gasolina/Alimentação)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("FINALIZAR E SALVAR"):
            novo_dado = pd.DataFrame([[
                data_f.strftime('%Y-%m-%d'), 
                app_f, bruto_f, km_f, desp_f, (bruto_f - desp_f)
            ]], columns=['Data', 'App', 'Bruto', 'KM', 'Despesas', 'Lucro'])
            
            df_atualizado = pd.concat([df, novo_dado], ignore_index=True)
            conn.update(spreadsheet=url, data=df_atualizado)
            st.sidebar.success("✅ Salvo com sucesso!")
            st.rerun()

# 5. DASHBOARD VISUAL
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'])
    df = df.sort_values('Data')

    # Métricas Principais
    c1, c2, c3, c4 = st.columns(4)
    lucro_total = df['Lucro'].sum()
    c1.metric("Lucro Líquido", f"R$ {lucro_total:,.2f}")
    c2.metric("Bruto Total", f"R$ {df['Bruto'].sum():,.2f}")
    c3.metric("KM Total", f"{df['KM'].sum():,.1f} km")
    c4.metric("Eficiência R$/KM", f"R$ {(df['Bruto'].sum()/df['KM'].sum() if df['KM'].sum() > 0 else 0):.2f}")

    # Gráfico Estilo Bolsa de Valores (Linhas)
    st.subheader("📊 Gráfico de Performance Financeira")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Bruto'], name='Receita Bruta', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro'], name='Lucro Líquido (Real)', line=dict(color='#39d353', width=4)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Despesas'], name='Despesas', line=dict(color='#f85149', width=2, dash='dot')))
    
    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Barra de Meta
    st.subheader(f"🎯 Meta: {st.session_state.meta_valor:,.2f}")
    progresso = min(lucro_total / st.session_state.meta_valor, 1.0) if st.session_state.meta_valor > 0 else 0
    st.progress(progresso)
    st.write(f"Você já conquistou **{progresso*100:.1f}%** do seu objetivo.")

    # 6. HISTÓRICO EDITÁVEL
    st.divider()
    st.subheader("📝 Editar ou Corrigir Dados")
    df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("CONFIRMAR ALTERAÇÕES NO HISTÓRICO"):
        conn.update(spreadsheet=url, data=df_editado)
        st.success("✅ Histórico atualizado na nuvem!")
        st.rerun()
else:
    st.info("Aguardando o primeiro lançamento para ativar o gráfico.")
