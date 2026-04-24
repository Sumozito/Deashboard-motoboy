import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configurações de Design
st.set_page_config(page_title="CPMA Digital - Motoboy Pro", layout="wide")

# Estilização de Alto Contraste
st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    div[data-testid="stMetric"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricLabel"] { color: #bbbbbb !important; }
    div[data-testid="stMetricValue"] { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Gestão Profissional de Entregas")

# LÓGICA DE DADOS (Persistência na Sessão)
if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        'Data', 'Plataforma', 'Receita Bruta', 'KM Rodado', 'Gasolina', 'Alimentação', 'Manutenção'
    ])

# SIDEBAR: ENTRADA DE DADOS
st.sidebar.header("📝 Lançamento de Turno")
with st.sidebar.form("form_diario", clear_on_submit=True):
    data = st.date_input("Data", datetime.now())
    app = st.selectbox("Plataforma", ["99 Moto", "iFood", "Uber Flash", "Particular"])
    valor = st.number_input("Faturamento Bruto (R$)", min_value=0.0, step=1.0, format="%.2f")
    km = st.number_input("KM Rodado (ex: 21.9)", min_value=0.0, step=0.1, format="%.1f")
    gasosa = st.number_input("Gasto Gasolina (R$)", min_value=0.0, step=1.0, format="%.2f")
    almoço = st.number_input("Alimentação (R$)", min_value=0.0, step=1.0, format="%.2f")
    manut = st.number_input("Manutenção Realizada (R$)", min_value=0.0, step=1.0, format="%.2f")
    
    submit = st.form_submit_button("Salvar Turno")
    
    if submit:
        novo_dado = pd.DataFrame([[pd.to_datetime(data), app, valor, km, gasosa, almoço, manut]], 
                                columns=st.session_state.dados.columns)
        st.session_state.dados = pd.concat([st.session_state.dados, novo_dado], ignore_index=True)
        st.rerun()

# PROCESSAMENTO
df = st.session_state.dados
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'])
    # Cálculo de Lucro Líquido por linha (Receita - Gasolina - Alimentação - Manutenção - Reserva Técnica 0.10/km)
    df['Lucro Líquido'] = df['Receita Bruta'] - df['Gasolina'] - df['Alimentação'] - df['Manutenção'] - (df['KM Rodado'] * 0.10)
    
    total_bruto = df['Receita Bruta'].sum()
    total_km = df['KM Rodado'].sum()
    reserva_tecnica = total_km * 0.10
    lucro_total = df['Lucro Líquido'].sum()

    # MÉTRICAS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento Total", f"R$ {total_bruto:,.2f}")
    col2.metric("Lucro Real (Líquido)", f"R$ {lucro_total:,.2f}")
    col3.metric("Média R$ / KM", f"R$ {(total_bruto/total_km if total_km > 0 else 0):.2f}")
    col4.metric("Distância Total", f"{total_km:.1f} km")

    # GRÁFICO CLEAN (LINHAS)
    st.subheader("📈 Evolução Financeira")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Receita Bruta'], name='Receita Bruta', line=dict(color='#00ff00', width=3)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Lucro Líquido'], name='Lucro Líquido', line=dict(color='#00bcff', width=3)))
    fig.add_trace(go.Scatter(x=df['Data'], y=df['Gasolina'], name='Custo Gasolina', line=dict(color='#ff4444', width=2, dash='dot')))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[0, max(df['Receita Bruta'].max() * 1.1, 100)]), # Começa do zero
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # META EDITÁVEL
    st.divider()
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("🎯 Configurar Meta")
        valor_meta = st.number_input("Defina o valor da meta (R$)", min_value=0.0, value=5000.0, step=100.0)
        progresso = min(lucro_total / valor_meta, 1.0) if valor_meta > 0 else 0
        st.write(f"**Progresso: {progresso*100:.1f}%**")
        st.progress(progresso)
    with c2:
        st.subheader("🔧 Saúde do Veículo")
        st.info(f"Fundo de Manutenção sugerido (acumulado por KM): **R$ {reserva_tecnica:.2f}**")
        if df['Manutenção'].sum() > 0:
            st.write(f"Total já gasto em manutenção: R$ {df['Manutenção'].sum():.2f}")

    # HISTÓRICO EDITÁVEL
    st.subheader("📝 Histórico e Edição")
    st.write("Você pode alterar qualquer valor diretamente na tabela abaixo:")
    df_editado = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "Data": st.column_config.DateColumn("Data"),
            "Plataforma": st.column_config.SelectboxColumn("App", options=["99 Moto", "iFood", "Uber Flash", "Particular"]),
            "Lucro Líquido": st.column_config.NumberColumn("Lucro Líquido", disabled=True, format="R$ %.2f")
        }
    )
    if st.button("Salvar Alterações do Histórico"):
        st.session_state.dados = df_editado
        st.success("Histórico atualizado!")
        st.rerun()

else:
    st.info("Aguardando lançamentos na barra lateral...")
