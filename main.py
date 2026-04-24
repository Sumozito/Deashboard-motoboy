import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configurações de Design
st.set_page_config(page_title="CPMA Digital - Motoboy Pro", layout="wide")

# Estilização CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Gestão Profissional de Entregas")
st.subheader("Controle de Receitas, Despesas e Metas de Longo Prazo")

# LÓGICA DE DADOS
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        'Data', 'Plataforma', 'Receita Bruta', 'KM Rodado', 'Gasolina', 'Alimentação', 'Outros'
    ])

# SIDEBAR: ENTRADA DE DADOS
st.sidebar.header("📝 Lançamento de Turno")
with st.sidebar.form("form_diario"):
    data = st.date_input("Data", datetime.now())
    app = st.selectbox("App Principal", ["iFood", "99 Moto", "Uber Flash", "Entrega Particular"])
    valor = st.number_input("Faturamento Bruto (R$)", min_value=0.0)
    km = st.number_input("KM Rodado Total", min_value=0)
    gasosa = st.number_input("Gasto Gasolina (R$)", min_value=0.0)
    almoço = st.number_input("Alimentação/Extra (R$)", min_value=0.0)
    
    # LINHA CORRIGIDA ABAIXO:
    submit = st.form_submit_button("Salvar Turno")
    
    if submit:
        novo_dado = pd.DataFrame([[data, app, valor, km, gasosa, almoço, 0]], 
                                columns=st.session_state.dados.columns)
        st.session_state.dados = pd.concat([st.session_state.dados, novo_dado], ignore_index=True)
        st.sidebar.success("Turno registrado!")

# PROCESSAMENTO DOS INDICADORES
df = st.session_state.dados
if not df.empty:
    total_bruto = df['Receita Bruta'].sum()
    total_km = df['KM Rodado'].sum()
    total_despesas = df['Gasolina'].sum() + df['Alimentação'].sum()
    
    # Reserva de Manutenção (R$ 0,10 por KM)
    reserva_manutencao = total_km * 0.10
    lucro_real = total_bruto - total_despesas - reserva_manutencao
    
    # DASHBOARD VISUAL
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento Acumulado", f"R$ {total_bruto:,.2f}")
    col2.metric("Lucro Líquido Real", f"R$ {lucro_real:,.2f}")
    col3.metric("Eficiência (R$/KM)", f"R$ {(total_bruto/total_km if total_km > 0 else 0):.2f}")
    col4.metric("KM Total", f"{total_km} km")

    st.divider()

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Histórico de Ganhos vs Despesas")
        fig = px.area(df, x='Data', y=['Receita Bruta', 'Gasolina'], 
                     title="Evolução Financeira", color_discrete_sequence=['#2ecc71', '#e74c3c'])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🎯 Meta: Próximo Objetivo")
        # Exemplo de meta de R$ 5.000,00
        progresso = min(lucro_real / 5000, 1.0) if lucro_real > 0 else 0
        st.progress(progresso)
        st.write(f"Você já conquistou **{progresso*100:.1f}%** da meta.")
        st.info(f"🔧 **Fundo de Manutenção:** R$ {reserva_manutencao:.2f}")

    st.subheader("📋 Detalhamento de Atividades")
    st.table(df.sort_values(by='Data', ascending=False))
else:
    st.info("Aguardando o primeiro lançamento para gerar o dashboard...")
