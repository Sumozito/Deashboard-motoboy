import streamlit as st
# ... seus outros imports ...

# 1. CSS CIRÚRGICO: Esconde apenas as opções de desenvolvedor e o rodapé
st.markdown("""
    <style>
    /* Esconde botões de Share, Star, GitHub e o menu de edição do topo */
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    
    /* Esconde o rodapé 'Made with Streamlit' */
    footer {visibility: hidden;}
    
    /* Remove a barra flutuante de edição (stToolbar) */
    div[data-testid="stToolbar"] {display: none !important;}

    /* Mantém o fundo escuro e o botão de menu (hambúrguer) visível */
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# ... resto do seu código de conexão e lógica ...

# 2. GRÁFICO SEM FERRAMENTAS (ModeBar)
# Na hora de exibir o gráfico, use o parâmetro config para esconder a barra que você circulou
if not df.empty:
    # ... sua lógica de criação do fig (go.Figure) ...
    
    # O comando abaixo exibe o gráfico SEM as opções de zoom/autoscale
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
