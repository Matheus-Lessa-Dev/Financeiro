import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuração de Layout
st.set_page_config(page_title="PRO Finance", page_icon="📈", layout="wide")

# Estilização CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

ARQUIVO_DADOS = "dados_financeiros.csv"

# Carregar dados
if os.path.exists(ARQUIVO_DADOS):
    df = pd.read_csv(ARQUIVO_DADOS)
    df['Data'] = pd.to_datetime(df['Data'])
else:
    df = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor", "Método"])

# --- SIDEBAR (LOGICA CORRIGIDA) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1611/1611154.png", width=80)
    st.title("PRO Control v2.0")
    st.divider()
    
    # FORA DO FORM: Usamos uma chave (key) para garantir a atualização instantânea
    tipo = st.selectbox("Fluxo", ["Receita", "Despesa"], key="tipo_fluxo")
    
    # Define categorias baseado na escolha ACIMA
    if tipo == "Receita":
        cats = ["Salário", "Freelance", "Investimentos", "Extra"]
    else:
        cats = ["Mercado", "Alimentação", "Casa", "Lazer", "Transporte", "Saúde", "Educação"]

    # O FORMULÁRIO agora contém apenas o que NÃO muda a estrutura da página
    with st.form("formulario_transacao", clear_on_submit=True):
        data = st.date_input("Data", datetime.now())
        cat = st.selectbox("Categoria", cats) # Já virá atualizado!
        val = st.number_input("Valor (R$)", min_value=0.01, step=0.50)
        met = st.selectbox("Método", ["PIX", "Crédito", "Débito", "Dinheiro"])
        
        submit = st.form_submit_button("Lançar Transação")

    if submit:
        nova_linha = pd.DataFrame([[pd.to_datetime(data), tipo, cat, val, met]], 
                                  columns=["Data", "Tipo", "Categoria", "Valor", "Método"])
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(ARQUIVO_DADOS, index=False)
        st.success(f"{tipo} registrada!")
        st.rerun()

# --- DASHBOARD (O RESTO DO CÓDIGO SEGUE IGUAL) ---
st.title("📊 Dashboard Executivo")

if not df.empty:
    df['Valor'] = pd.to_numeric(df['Valor'])
    total_receita = df[df['Tipo'] == 'Receita']['Valor'].sum()
    total_despesa = df[df['Tipo'] == 'Despesa']['Valor'].sum()
    saldo = total_receita - total_despesa
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Receitas", f"R$ {total_receita:,.2f}")
    m2.metric("Total de Despesas", f"R$ {total_despesa:,.2f}", delta_color="inverse")
    m3.metric("Saldo Atual", f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}")

    st.divider()
    g1, g2 = st.columns(2)

    with g1:
        df_gastos = df[df['Tipo'] == 'Despesa']
        if not df_gastos.empty:
            fig_pizza = px.pie(df_gastos, values='Valor', names='Categoria', hole=0.4)
            st.plotly_chart(fig_pizza, use_container_width=True)
    
    with g2:
        if not df_gastos.empty:
            fig_col = px.bar(df_gastos, x='Método', y='Valor', color='Método', text_auto='.2s')
            st.plotly_chart(fig_col, use_container_width=True)

    st.divider()
    st.subheader("📑 Histórico")
    st.dataframe(df.sort_values(by="Data", ascending=False), use_container_width=True)

    if st.button("🗑️ Limpar último registro"):
        df = df.drop(df.index[-1])
        df.to_csv(ARQUIVO_DADOS, index=False)
        st.rerun()
else:
    st.info("Adicione transações na barra lateral.")