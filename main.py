import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="CPMA Clone", layout="centered")

# URL da sua planilha
URL = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=drivesdk"

# CONEXÃO SIMPLIFICADA (O Streamlit vai buscar tudo nas Secrets automaticamente)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro ao conectar: {e}")
    st.stop()

# Função para carregar os dados
def carregar():
    return conn.read(spreadsheet=URL, worksheet="dados", ttl=0)

st.title("📊 Gestão MotoristaSOS")

try:
    df = carregar()
    
    if not df.empty:
        # Converter colunas para números para evitar erros de soma
        cols_num = ['bruto', 'combustivel', 'outras', 'km']
        for col in cols_num:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        ganho_total = df['bruto'].sum()
        gasto_total = df['combustivel'].sum() + df['outras'].sum()
        lucro_real = ganho_total - gasto_total
        
        # Dashboard estilo CPMA
        m1, m2 = st.columns(2)
        m1.metric("Ganho Bruto", f"R$ {ganho_total:.2f}")
        m1.metric("KM Total", f"{df['km'].sum():.0f} km")
        m2.metric("Lucro Líquido", f"R$ {lucro_real:.2f}")
        m2.metric("Total Gastos", f"R$ {gasto_total:.2f}")

    st.divider()

    # Formulário de Lançamento
    st.subheader("📝 Novo Lançamento")
    with st.form("add_registro", clear_on_submit=True):
        f_data = st.date_input("Data", datetime.now())
        f_bruto = st.number_input("Ganhos Brutos (R$)", min_value=0.0)
        f_km = st.number_input("KM Rodados", min_value=0.0)
        f_gas = st.number_input("Combustível (R$)", min_value=0.0)
        f_outras = st.number_input("Outras Despesas (R$)", min_value=0.0)
        
        if st.form_submit_button("Salvar no App"):
            novo_dado = pd.DataFrame([{
                "data": f_data.strftime("%d/%m/%Y"),
                "bruto": f_bruto,
                "km": f_km,
                "combustivel": f_gas,
                "outras": f_outras
            }])
            
            df_atualizado = pd.concat([df, novo_dado], ignore_index=True)
            conn.update(spreadsheet=URL, worksheet="dados", data=df_atualizado)
            st.success("Dados salvos!")
            st.rerun()

    if st.checkbox("Ver histórico"):
        st.dataframe(df)

except Exception as e:
    st.info("Adicione o seu primeiro lançamento para começar!")
