import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configuração de Layout "Dark Mode" Pro
st.set_page_config(page_title="PRO Finance", page_icon="📈", layout="wide")

# Estilização customizada via CSS
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

# --- SIDEBAR (Entradas) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1611/1611154.png", width=80)
    st.title("PRO Control v1.0")
    st.divider()
    
    with st.form("nova_transacao", clear_on_submit=True):
        data = st.date_input("Data da Transação", datetime.now())
        tipo = st.selectbox("Fluxo", ["Receita", "Despesa"])
        
        if tipo == "Receita":
            cats = ["Salário", "Freelance", "Investimentos", "Extra"]
        elif tipo == "Despesa":
            cats = ["Mercado", "Alimentação", "Casa", "Lazer", "Transporte", "Saúde", "Educação"]
            
        cat = st.selectbox("Categoria", cats)
        val = st.number_input("Valor (R$)", min_value=0.01, step=0.50)
        met = st.selectbox("Método", ["PIX", "Crédito", "Débito", "Dinheiro"])
        
        btn_salvar = st.form_submit_button("Lançar Transação")

    if btn_salvar:
        nova_linha = pd.DataFrame([[pd.to_datetime(data), tipo, cat, val, met]], 
                                  columns=["Data", "Tipo", "Categoria", "Valor", "Método"])
        df = pd.concat([df, nova_linha], ignore_index=True)
        df.to_csv(ARQUIVO_DADOS, index=False)
        st.success("Lançamento concluído!")
        st.rerun()

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Dashboard Executivo")

# Cálculos de Métricas
if not df.empty:
    total_receita = df[df['Tipo'] == 'Receita']['Valor'].sum()
    total_despesa = df[df['Tipo'] == 'Despesa']['Valor'].sum()
    saldo = total_receita - total_despesa
    cor_saldo = "normal" if saldo >= 0 else "inverse"

    # Topo: Cards de Resumo
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Receitas", f"R$ {total_receita:,.2f}", delta_color="normal")
    m2.metric("Total de Despesas", f"R$ {total_despesa:,.2f}", delta_color="inverse")
    m3.metric("Saldo Atual", f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}", delta_color=cor_saldo)

    st.divider()

    # Meio: Gráficos
    g1, g2 = st.columns([1, 1])

    with g1:
        st.subheader("Onde seu dinheiro vai?")
        df_gastos = df[df['Tipo'] == 'Despesa']
        if not df_gastos.empty:
            fig_pizza = px.pie(df_gastos, values='Valor', names='Categoria', 
                             hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pizza, use_container_width=True)

    with g2:
        st.subheader("Meios de Pagamento")
        if not df_gastos.empty:
            fig_col = px.bar(df_gastos, x='Método', y='Valor', color='Método',
                           text_auto='.2s', title="Gastos por Forma de Pagamento")
            st.plotly_chart(fig_col, use_container_width=True)

    # Base: Tabela e Controle
    st.divider()
    st.subheader("📑 Histórico de Movimentações")
    
    # Ordenar por data mais recente
    df_view = df.sort_values(by="Data", ascending=False)
    st.dataframe(df_view, use_container_width=True)

    if st.button("🗑️ Limpar último registro"):
        if not df.empty:
            df = df.drop(df.index[-1])
            df.to_csv(ARQUIVO_DADOS, index=False)
            st.warning("Último registro removido.")
            st.rerun()
else:
    st.info("Aguardando os primeiros lançamentos para gerar o relatório profissional...")