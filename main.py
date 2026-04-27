import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Moto SOS", layout="centered")

# URL da sua planilha (Já conferida)
URL = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=drivesdk"

# Conexão direta (O Streamlit Cloud vai ler das Secrets automaticamente)
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📲 MotoristaSOS - Lançamentos")

# Função simples para ler
def carregar_dados():
    try:
        return conn.read(spreadsheet=URL, worksheet="dados", ttl=0)
    except:
        return pd.DataFrame()

df = carregar_dados()

# Mostra se há dados ou não
if not df.empty:
    st.write(f"Você tem {len(df)} turnos registrados.")
else:
    st.info("Nenhum dado encontrado. Faça seu primeiro lançamento abaixo.")

st.divider()

# Formulário simplificado
with st.form("lancamento"):
    f_data = st.date_input("Data", datetime.now())
    f_bruto = st.number_input("Ganhos (R$)", min_value=0.0)
    f_km = st.number_input("KM", min_value=0.0)
    f_gas = st.number_input("Combustível (R$)", min_value=0.0)
    f_outras = st.number_input("Outras (R$)", min_value=0.0)
    
    if st.form_submit_button("SALVAR"):
        novo = pd.DataFrame([{
            "data": f_data.strftime("%d/%m/%Y"),
            "bruto": f_bruto,
            "km": f_km,
            "combustivel": f_gas,
            "outras": f_outras
        }])
        df_novo = pd.concat([df, novo], ignore_index=True)
        conn.update(spreadsheet=URL, worksheet="dados", data=df_novo)
        st.success("Salvo!")
        st.rerun()

st.dataframe(df)
