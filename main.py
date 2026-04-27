import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Meu Controle Financeiro", layout="centered")

# CREDENCIAIS (Para evitar erro de formatação nas Secrets do Streamlit)
# Substitua APENAS o que está entre aspas se você criar uma nova conta de serviço
creds = {
    "type": "service_account",
    "project_id": "controlemotoboy",
    "private_key_id": "5f529abb4cc2ca81c93d5f81fb17684fec1b47ad",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDjHXqXW5cDB7hh\ngvNNxpJwZjBF20Ymd+RJ0kDa+jwUqB+5eNeHYfnKGH84ct+s5YL22zvo4tjYn9J3\neKqxeNw+KO05rQXKnARyJyVEih8EvaZK5ivZat+RoHGGt8CrPwqmqlUPf/6XOrY5\n0DO37T13g0V5HHVHt2klHBstSSxQ87Hx2zBYnkkINJSZOTWwUuzB7OdIkDMoUr4q\nE50mEQV4LSCEn72W8wNjKDDOgiNgyK8GPeg9nd3BSrHDkDt2H9Lott3iEdJKsRvc\nUYKtc0rV4/+kxju7dA3aSdMNHimMMMqz6bq7tncrVvrUGId0oSqO4Gwq1asL8KYj\nRltBSTblAgMBAAECggEANdt/fwWh9768r2kLk/HHN77P6zzus4AiY4wnw5XsKfTd\ngxDgQXNPNijdgHAjUT+i8TG3kQg8ZpBt61Vy2v+fcOEpMlBwy2V4m25jhM+hP/FO\nTjwrgVU5+7F5wnnwR1u9hZzma3TNlaS/YlHYdeEdPqpjTu9b83wPw9RYsIJF71MM\ne7jCQAn5KfNHA2Exy10aNK8YWiOj1U37PeFpKvd7aHxcKNCj5Xb19RWzwNh1RRsw\nLrj9Nfc3+IYQtvnM7qhJQMo9aKAV+ZjDPRD+w4C6g1FNT6aWNYJLi8En5r7fEXn8\nYyhubWN3DpNN1GFHOGCXqK/UGYlKvzoP9wUPUiTVmQKBgQD6AiT0pV65t2Uut2td\nzUvfT/g0SPeIo/cA5bbLIqBYHkv7OSnXrI/6Kn5l9ULBixysRhnM9muhktTbch97\nEj1J9K4OPqqemNG0CZWcZzjcFL6YlXQPTrOATMBB8xmnoYSa5LafMhU5GSJhWZsL\nOBKlbVMEmnZlNxayjmqxax6tvQKBgQDojuEuWT5+eEqEQBA3LZZC8DT3G4RbL/hB\nEGopgQB4T5Nk4hcw+VVtVLiev1VL8SHFQLI7B3lt63EzTsJitoO53t8rg8Sn5Ddg\n6Fqoe5DPF4ekJeslUc67BhlPR6yfZXfxaPageslUc67BhlPR6yfZXfxaPNsngD0ox\nCppJupL9bN0ZVuGPIaJHtINex4zr0cSQKBgQDwOjFCdsifkW6DRjG/r23RRWlM7DQ\nWMt88GH7dkAccxPfjjRj8qU6rZjuQQuwDR2Wkz7Mo9DuVxJ4Nwwom2u7Tam35OBQA\nUv1ljrQY1kKXjsNZoHol30yx4o32kN486gGeSFiGfbxQ4irb+hr128pm9LaJvNY5\nCYcgyaIRmsmezQKBgQDiTG7pKCS88pcofCKLXwvyFUalExzHkzVTMwLrYkGv0VeP\nesawfF/ZpPCGYY9B9+IxzRPihxJtmQctsz1Ky2oBS9QExxNtgJE29sOJYbx3GOGA\nJPnd9e5iZbvpPsjGzvlZbBQ8JMCvTaJgQfLLPucanxB280VblRZ2HSsAH8U8KQKB\ngHxPlqQXzoNUH/ZjRSjE0OH8930l7ZKFySv+MKBri3rw/eZ/hvfbkOA9fBYOhVzw\nNa6LmjnDtRkUErOI9jLkh59MxKzT73eF7k/SODSoRskf/gEQuv9OmAAqWEWVttVL\nSOWyAEgkYT7DnJ5c6KzUK52kAz66uAO/LWVwJPvh4W4C\n-----END PRIVATE KEY-----\n",
    "client_email": "controlemotoboy@controlemotoboy.iam.gserviceaccount.com",
}

# Tratamento da chave para evitar erro de leitura
creds["private_key"] = creds["private_key"].replace("\\n", "\n")

# CONEXÃO COM A PLANILHA
conn = st.connection("gsheets", type=GSheetsConnection, **creds)

def buscar_dados():
    return conn.read(worksheet="dados", ttl=0)

df = buscar_dados()

# INTERFACE ESTILO APP
st.title("📊 CPMA Clone - Finanças")

# 1. RESUMO (DASHBOARD)
if not df.empty:
    # Garantir que os números sejam lidos como números
    for col in ['bruto', 'km', 'combustivel', 'outras']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    total_bruto = df['bruto'].sum()
    total_km = df['km'].sum()
    total_despesas = df['combustivel'].sum() + df['outras'].sum()
    lucro_real = total_bruto - total_despesas

    c1, c2 = st.columns(2)
    c1.metric("Ganho Total", f"R$ {total_bruto:.2f}")
    c1.metric("KM Total", f"{total_km} km")
    c2.metric("Lucro Real", f"R$ {lucro_real:.2f}", delta_color="normal")
    c2.metric("Despesas", f"R$ {total_despesas:.2f}", delta="-")

st.divider()

# 2. FORMULÁRIO DE LANÇAMENTO
st.subheader("➕ Novo Lançamento")
with st.form("registro", clear_on_submit=True):
    data = st.date_input("Data", datetime.now())
    bruto = st.number_input("Ganhos Brutos (R$)", min_value=0.0, step=10.0)
    km = st.number_input("KM Rodado no dia", min_value=0.0, step=1.0)
    combustivel = st.number_input("Gasto com Combustível (R$)", min_value=0.0, step=5.0)
    outras = st.number_input("Outras Despesas (R$)", min_value=0.0, step=5.0)
    
    if st.form_submit_button("Salvar Turno"):
        novo_dado = pd.DataFrame([{
            "data": data.strftime('%d/%m/%Y'),
            "bruto": bruto,
            "km": km,
            "combustivel": combustivel,
            "outras": outras
        }])
        
        df_atualizado = pd.concat([df, novo_dado], ignore_index=True)
        conn.update(worksheet="dados", data=df_atualizado)
        st.success("Lançamento realizado com sucesso!")
        st.rerun()

# 3. HISTÓRICO
if st.checkbox("Mostrar histórico de lançamentos"):
    st.dataframe(df, use_container_width=True)
