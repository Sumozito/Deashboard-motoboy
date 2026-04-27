import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Configuração visual do App
st.set_page_config(page_title="CPMA Clone - Financeiro", layout="centered")

# URL da sua planilha (que você forneceu)
url_planilha = "https://docs.google.com/spreadsheets/d/12xdQ_4kXifbdK7JQedxXBVOK2-GOrkXEkY_hpdYFiEo/edit?usp=drivesdk"

# Credenciais inseridas direto no código para facilitar o seu acesso no telemóvel
creds = {
    "type": "service_account",
    "project_id": "controlemotoboy",
    "private_key_id": "5f529abb4cc2ca81c93d5f81fb17684fec1b47ad",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDjHXqXW5cDB7hh\ngvNNxpJwZjBF20Ymd+RJ0kDa+jwUqB+5eNeHYfnKGH84ct+s5YL22zvo4tjYn9J3\neKqxeNw+KO05rQXKnARyJyVEih8EvaZK5ivZat+RoHGGt8CrPwqmqlUPf/6XOrY5\n0DO37T13g0V5HHVHt2klHBstSSxQ87Hx2zBYnkkINJSZOTWwUuzB7OdIkDMoUr4q\nE50mEQV4LSCEn72W8wNjKDDOgiNgyK8GPeg9nd3BSrHDkDt2H9Lott3iEdJKsRvc\nUYKtc0rV4/+kxju7dA3aSdMNHimMMMqz6bq7tncrVvrUGId0oSqO4Gwq1asL8KYj\nRltBSTblAgMBAAECggEANdt/fwWh9768r2kLk/HHN77P6zzus4AiY4wnw5XsKfTd\ngxDgQXNPNijdgHAjUT+i8TG3kQg8ZpBt61Vy2v+fcOEpMlBwy2V4m25jhM+hP/FO\nTjwrgVU5+7F5wnnwR1u9hZzma3TNlaS/YlHYdeEdPqpjTu9b83wPw9RYsIJF71MM\ne7jCQAn5KfNHA2Exy10aNK8YWiOj1U37PeFpKvd7aHxcKNCj5Xb19RWzwNh1RRsw\nLrj9Nfc3+IYQtvnM7qhJQMo9aKAV+ZjDPRD+w4C6g1FNT6aWNYJLi8En5r7fEXn8\nYyhubWN3DpNN1GFHOGCXqK/UGYlKvzoP9wUPUiTVmQKBgQD6AiT0pV65t2Uut2td\nzUvfT/g0SPeIo/cA5bbLIqBYHkv7OSnXrI/6Kn5l9ULBixysRhnM9muhktTbch97\nEj1J9K4OPqqemNG0CZWcZzjcFL6YlXQPTrOATMBB8xmnoYSa5LafMhU5GSJhWZsL\nOBKlbVMEmnZlNxayjmqxax6tvQKBgQDojuEuWT5+eEqEQBA3LZZC8DT3G4RbL/hB\nEGopgQB4T5Nk4hcw+VVtVLiev1VL8SHFQLI7B3lt63EzTsJitoO53t8rg8Sn5Ddg\n6Fqoe5DPF4ekJeslUc67BhlPR6yfZXfxaPageslUc67BhlPR6yfZXfxaPNsngD0ox\nCppJupL9bN0ZVuGPIaJHtINex4zr0cSQKBgQDwOjFCdsifkW6DRjG/r23RRWlM7DQ\nWMt88GH7dkAccxPfjjRj8qU6rZjuQQuwDR2Wkz7Mo9DuVxJ4Nwwom2u7Tam35OBQA\nUv1ljrQY1kKXjsNZoHol30yx4o32kN486gGeSFiGfbxQ4irb+hr128pm9LaJvNY5\nCYcgyaIRmsmezQKBgQDiTG7pKCS88pcofCKLXwvyFUalExzHkzVTMwLrYkGv0VeP\nesawfF/ZpPCGYY9B9+IxzRPihxJtmQctsz1Ky2oBS9QExxNtgJE29sOJYbx3GOGA\nJPnd9e5iZbvpPsjGzvlZbBQ8JMCvTaJgQfLLPucanxB280VblRZ2HSsAH8U8KQKB\ngHxPlqQXzoNUH/ZjRSjE0OH8930l7ZKFySv+MKBri3rw/eZ/hvfbkOA9fBYOhVzw\nNa6LmjnDtRkUErOI9jLkh59MxKzT73eF7k/SODSoRskf/gEQuv9OmAAqWEWVttVL\nSOWyAEgkYT7DnJ5c6KzUK52kAz66uAO/LWVwJPvh4W4C\n-----END PRIVATE KEY-----\n",
    "client_email": "controlemotoboy@controlemotoboy.iam.gserviceaccount.com",
}

# Tratamento da chave
creds["private_key"] = creds["private_key"].replace("\\n", "\n")

# Estabelecer conexão
conn = st.connection("gsheets", type=GSheetsConnection, **creds)

# Função para ler os dados
def carregar_dados():
    try:
        return conn.read(spreadsheet=url_planilha, worksheet="dados", ttl=0)
    except:
        return pd.DataFrame(columns=["data", "bruto", "km", "combustivel", "outras"])

df = carregar_dados()

# --- INTERFACE ---
st.title("🚀 Controle Financeiro Diário")

# Dashboards (Métricas)
if not df.empty:
    for col in ['bruto', 'km', 'combustivel', 'outras']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    lucro = df['bruto'].sum() - (df['combustivel'].sum() + df['outras'].sum())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ganho Bruto", f"R$ {df['bruto'].sum():.2f}")
    col2.metric("Lucro Líquido", f"R$ {lucro:.2f}")
    col3.metric("KM Total", f"{df['km'].sum()} km")

st.divider()

# Formulário de Lançamento
with st.form("novo_registro"):
    st.subheader("📝 Lançar Turno")
    f_data = st.date_input("Data", datetime.now())
    f_bruto = st.number_input("Ganhos Brutos (R$)", min_value=0.0)
    f_km = st.number_input("KM Rodados", min_value=0.0)
    f_gas = st.number_input("Combustível (R$)", min_value=0.0)
    f_outras = st.number_input("Outras Despesas (R$)", min_value=0.0)
    
    if st.form_submit_button("Salvar Lançamento"):
        novo_item = pd.DataFrame([{
            "data": f_data.strftime("%d/%m/%Y"),
            "bruto": f_bruto,
            "km": f_km,
            "combustivel": f_gas,
            "outras": f_outras
        }])
        df_final = pd.concat([df, novo_item], ignore_index=True)
        conn.update(spreadsheet=url_planilha, worksheet="dados", data=df_final)
        st.success("Salvo com sucesso na sua planilha!")
        st.rerun()

# Histórico
if st.checkbox("Ver Histórico"):
    st.dataframe(df, use_container_width=True)
