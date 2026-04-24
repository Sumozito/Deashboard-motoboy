import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Dashboard Motoboy Pro", layout="wide")

st.title("🚀 Painel de Controle - Motoboy Extra")
st.markdown("Foco em Lucratividade e Manutenção Preventiva")

# --- SIDEBAR: ENTRADA DE DADOS ---
st.sidebar.header("📥 Lançamento Diário")
data = st.sidebar.date_input("Data do Trampo")
plataforma = st.sidebar.selectbox("Plataforma", ["iFood", "99 Moto", "Uber Flash", "Particular"])
receita = st.sidebar.number_input("Receita Bruta (R$)", min_value=0.0, step=10.0)
km_rodado = st.sidebar.number_input("KM Rodado no dia", min_value=0, step=1)
gasolina = st.sidebar.number_input("Gasto com Gasolina (R$)", min_value=0.0, step=5.0)
alimentacao = st.sidebar.number_input("Alimentação na Rua (R$)", min_value=0.0, step=5.0)

# Simulação de Banco de Dados (Em um caso real, salvaria em CSV ou SQL)
if st.sidebar.button("Salvar Dados"):
    st.sidebar.success("Dados salvos com sucesso (Simulação)")

# --- DADOS DE EXEMPLO (Para visualizar o Dashboard) ---
data_fake = {
    'Data': pd.to_datetime(['2026-04-20', '2026-04-21', '2026-04-22', '2026-04-23']),
    'Receita': [180, 210, 150, 250],
    'KM': [120, 140, 100, 160],
    'Gasolina': [40, 45, 35, 50],
    'Manutencao_Reserva': [6, 7, 5, 8] # R$ 0,05 por KM
}
df = pd.DataFrame(data_fake)

# Cálculos Rápidos
total_receita = df['Receita'].sum()
total_km = df['KM'].sum()
total_gastos = df['Gasolina'].sum() + df['Manutencao_Reserva'].sum()
lucro_liquido = total_receita - total_gastos
ganho_por_km = total_receita / total_km

# --- LINHA 1: MÉTRICAS PRINCIPAIS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Receita Total", f"R$ {total_receita:.2f}")
col2.metric("Lucro Líquido", f"R$ {lucro_liquido:.2f}", delta=f"{lucro_liquido/total_receita*100:.1f}% Margem")
col3.metric("KM Total Rodado", f"{total_km} km")
col4.metric("Ganho por KM", f"R$ {ganho_por_km:.2f}")

st.divider()

# --- LINHA 2: GRÁFICOS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Faturamento Diário")
    fig_fat = px.line(df, x='Data', y='Receita', markers=True, line_shape='spline')
    st.plotly_chart(fig_fat, use_container_width=True)

with col_right:
    st.subheader("Custo de Manutenção Acumulado")
    # Alerta para o plano Mottu Conquiste
    reserva_acumulada = df['Manutencao_Reserva'].sum()
    st.info(f"💰 Você deve ter **R$ {reserva_acumulada:.2f}** reservados para sua próxima manutenção.")
    fig_km = px.bar(df, x='Data', y='KM', color_discrete_sequence=['orange'])
    st.plotly_chart(fig_km, use_container_width=True)

# --- TABELA DE HISTÓRICO ---
st.subheader("📋 Histórico de Movimentações")
st.dataframe(df, use_container_width=True)
