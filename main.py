import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Configuração da página para parecer um App de celular
st.set_page_config(page_title="CPMA Clone", layout="centered")

# Credenciais organizadas para evitar o erro de TypeError
creds = {
    "type": "service_account",
    "project_id": "controlemotoboy",
    "private_key_id": "5f529abb4cc2ca81c93d5f81fb17684fec1b47ad",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDjHXqXW5cDB7hh\ngvNNxpJwZjBF20Ymd+RJ0kDa+jwUqB+5eNeHYfnKGH84ct+s5YL22zvo4tjYn9J3\neKqxeNw+KO05rQXKnARyJyVEih8EvaZK5ivZat+RoHGGt8CrPwqmqlUPf/6XOrY5\n0DO37T13g0V5HHVHt2klHBstSSxQ87Hx2zBYnkkINJSZOTWwUuzB7OdIkDMoUr4q\nE50mEQV4LSCEn72W8wNjKDDOgiNgyK8GPeg9nd3BSrHDkDt2H9Lott3iEdJKsRvc\nUYKtc0rV4/+kxju7dA3aSdMNHimMMMqz6bq7tncrVvrUGId0oSqO4Gwq1asL8KYj\nRltBSTblAgMBAAECggEANdt/fwWh9768r2kLk/HHN77P6zzus4AiY4wnw5XsKfTd\ngxDgQXNPNijdgHAjUT+i8TG3kQg8ZpBt61Vy2v+fcOEpMlBwy2V4m25jhM+hP/FO\nTjwrgVU5+7F5wnnwR1u9hZzma3TNlaS/YlHYdeEdPqpjTu9b83wPw9RYsIJF71MM\ne7jCQAn5KfNHA2Exy10aNK8YWiOj1U37PeFpKvd7aHxcKNCj5Xb19RWzwNh1RRsw\nLrj9Nfc3+IYQtvnM7qhJQMo9aKAV+ZjDPRD+w4C6g1FNT6aWNYJLi8En5r7fEXn8\nYyhubWN3DpNN1GFHOGCXqK/UGYlKvzoP9wUPUiTVmQKBgQD6AiT0pV65t2Uut2td\nzUvfT/g0SPeIo/cA5bbLIqBYHkv7OSnXrI/6Kn5l9ULBixysRhnM9muhktTbch97\nEj1J9K4OPqqemNG0CZWcZzjcFL6YlXQPTrOATMBB8xmnoYSa5LafMhU5GSJhWZsL\nOBKlbVMEmnZlNxayjmqxax6tvQKBgQDojuEuWT5+eEqEQBA3LZZC8DT3G4RbL/hB\nEGopgQB4T5Nk4hcw+VVtVLiev1VL8SHFQLI7B3lt63EzTsJitoO53t8rg8Sn5Ddg\n6Fqoe5DPF4ekJeslUc67BhlPR6yfZXfxaPageslUc67BhlPR6yfZXfxaPNsngD0ox\nCppJupL9bN0ZVuGPIaJHtINex4zr0cSQKBgQDwOjFCdsifkW6DRjG/r23RRWlM7DQ\nWMt88GH7dkAccxPfjjRj8qU6rZjuQQuwDR2Wkz7Mo9DuVxJ4Nwwom2u7Tam35OBQA\nUv1ljrQY1kKXjsNZoHol30yx4o32kN486gGeSFiGfbxQ4irb+hr128pm9LaJvNY5\nCYcgyaIRmsmezQKBgQDiTG7pKCS88pcofCKLXwvyFUalExzHkzVTMwLrYkGv0VeP\nesawfF/ZpPCGYY9B9+IxzRPihxJtmQctsz1Ky2oBS9QExxNtgJE29sOJYbx3GOGA\nJPnd9e5iZbvpPsjGzvlZbBQ8JMCvTaJgQfLLPucanxB280VblRZ2HSsAH8U8KQKB\ngHxPlqQXzoNUH/ZjRSjE0OH8930l7ZKFySv+MKBri3rw/eZ/hvfbkOA9fBYOhVzw\nNa6LmjnDtRkUErOI9jLkh59MxKzT73eF7k/SODSoRskf/gEQuv9OmAAqWEWVttVL\nSOWyAEgkYT7DnJ5c6KzUK52kAz66uAO/LWVwJPvh4W4C\n-----END PRIVATE KEY-----\n",
    "client_email": "controlemotoboy@controlemotoboy.iam.gserviceaccount.com",
}

# Limpeza da chave
creds["private_key"] = creds["private_key"].replace("\\n", "\n")

# URL da sua planilha
URL = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=drivesdk"

# CONEXÃO BLINDADA
try:
    conn = st.connection("gsheets", 
                         type=GSheetsConnection, 
                         project_id=creds["project_id"], 
                         private_key=creds["private_key"], 
                         client_email=creds["client_email"])
except Exception as e:
    st.error(f"Erro na conexão: {e}")
    st.stop()

# Função para carregar os dados
def carregar():
    return conn.read(spreadsheet=URL, worksheet="dados", ttl=0)

# Início do App
st.title("📊 Gestão MotoristaSOS")

try:
    df = carregar()
    
    # Cálculos para o Dashboard
    if not df.empty:
        df['bruto'] = pd.to_numeric(df['bruto'], errors='coerce').fillna(0)
        df['combustivel'] = pd.to_numeric(df['combustivel'], errors='coerce').fillna(0)
        df['outras'] = pd.to_numeric(df['outras'], errors='coerce').fillna(0)
        df['km'] = pd.to_numeric(df['km'], errors='coerce').fillna(0)
        
        ganho_total = df['bruto'].sum()
        gasto_total = df['combustivel'].sum() + df['outras'].sum()
        lucro_real = ganho_total - gasto_total
        
        # Estilo CPMA (Métricas em destaque)
        m1, m2 = st.columns(2)
        m1.metric("Ganho Bruto", f"R$ {ganho_total:.2f}")
        m1.metric("KM Total", f"{df['km'].sum():.0f} km")
        m2.metric("Lucro Líquido", f"R$ {lucro_real:.2f}")
        m2.metric("Total Gastos", f"R$ {gasto_total:.2f}", delta_color="inverse")

    st.divider()

    # Formulário de Lançamento
    st.subheader("📝 Novo Lançamento")
    with st.form("add_registro", clear_on_submit=True):
        f_data = st.date_input("Data", datetime.now())
        f_bruto = st.number_input("Quanto ganhou hoje? (R$)", min_value=0.0)
        f_km = st.number_input("Quantos KM rodou?", min_value=0.0)
        f_gas = st.number_input("Gasto com Combustível (R$)", min_value=0.0)
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
            st.success("Dados salvos com sucesso!")
            st.rerun()

    if st.checkbox("Ver histórico detalhado"):
        st.dataframe(df)

except Exception as e:
    st.warning("Aguardando dados ou erro na leitura da planilha.")
    st.info("Verifique se a aba se chama 'dados' e tem os cabeçalhos corretos.")
