import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Vendas - C1", layout="wide")

st.title("📊 Dashboard de Análise de Vendas - C1")

# Carregar dados
@st.cache_data
def load_data():
    return pd.read_csv("vendas.csv")

df = load_data()

# Filtro
categoria_sel = st.sidebar.multiselect("Selecione a Categoria:", options=df["Categoria"].unique(), default=df["Categoria"].unique())
df_filtered = df[df["Categoria"].isin(categoria_sel)]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total de Vendas", f"R$ {df_filtered['Valor_Venda'].sum():,.2f}")
col2.metric("Qtd. Transações", len(df_filtered))
col3.metric("Ticket Médio", f"R$ {df_filtered['Valor_Venda'].mean():,.2f}")

st.markdown("---")

# Gráfico
fig = px.bar(df_filtered, x="Categoria", y="Valor_Venda", color="Categoria", title="Vendas por Categoria", barmode="group")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Base de Dados Filtrada")
st.dataframe(df_filtered)
