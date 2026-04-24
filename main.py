import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Dashboard Motoboy Pro", layout="wide")

st.title("📊 Gestão Profissional de Entregas")

# Inicializar o histórico na memória (se não existir)
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        'Data', 'Plataforma', 'Receita', 'KM', 'Gasolina', 'Alimentação', 'Manutenção'
    ])

# --- SIDEBAR: LANÇAMENTO ---
st.sidebar.header("📝 Lançamento de Turno")

with st.sidebar.form("formulario_entrega"):
    data_input = st.date_input("Data", value=datetime.now())
    app = st.selectbox("Plataforma", ["iFood", "99 Moto", "Uber Moto", "Particular", "Outros"])
    valor = st.number_input("Faturamento Bruto (R$)", min_value=0.0, step=5.0)
    km = st.number_input("KM Rodado", min_value=0.0, step=1.0)
    gasosa = st.number_input("Gasto Gasolina (R$)", min_value=0.0, step=1.0)
    almoco = st.number_input("Alimentação (R$)", min_value=0.0, step=1.0)
    manut = st.number_input("Manutenção Realizada (R$)", min_value=0.0, step=1.0)
    
    submetido = st.form_submit_button("Salvar Turno")

if submetido:
    # Formata a data para padrão BR antes de salvar
    data_br = data_input.strftime('%d/%m/%Y')
    
    # Nova linha de dados corrigida
    nova_linha = pd.DataFrame([{
        'Data': data_br,
        'Plataforma': app,
        'Receita': valor,
        'KM': km,
        'Gasolina': gasosa,
        'Alimentação': almoco,
        'Manutenção': manut
    }])
    
    # Adiciona ao histórico sem erro de índice
    st.session_state.dados = pd.concat([st.session_state.dados, nova_linha], ignore_index=True)
    st.success("Dados salvos com sucesso!")

# --- DASHBOARD VISUAL ---
df = st.session_state.dados

if not df.empty:
    # Métricas
    total_receita = df['Receita'].sum()
    total_km = df['KM'].sum()
    total_custos = df['Gasolina'].sum() + df['Alimentação'].sum() + df['Manutenção'].sum()
    lucro = total_receita - total_custos
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Receita Total", f"R$ {total_receita:.2f}")
    c2.metric("Lucro Líquido", f"R$ {lucro:.2f}", delta_color="normal")
    c3.metric("KM Total", f"{total_km:.1f} km")

    st.divider()

    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("Receita por Plataforma")
        fig1 = px.pie(df, values='Receita', names='Plataforma', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_graf2:
        st.subheader("Evolução Diária")
        fig2 = px.bar(df, x='Data', y='Receita', color='Plataforma', barmode='group')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Histórico Detalhado")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Aguardando o primeiro lançamento para gerar os gráficos.")
