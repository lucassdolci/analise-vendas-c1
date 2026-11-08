import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

st.set_page_config(page_title="Painel de Vendas", page_icon="📊", layout="wide")

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "vendas.csv"
COLUNAS = ["Data", "Categoria", "Valor_Venda", "Vendedor"]

st.markdown("""
<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {background: #f5f7fb; padding: 16px; border-radius: 10px;}
    div[data-testid="stSidebar"] {background: #f7f8fa;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=COLUNAS)
    df = pd.read_csv(DATA_FILE)
    for coluna in COLUNAS:
        if coluna not in df.columns:
            df[coluna] = None
    df = df[COLUNAS].copy()
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Valor_Venda"] = pd.to_numeric(df["Valor_Venda"], errors="coerce").fillna(0)
    df["Categoria"] = df["Categoria"].fillna("Sem categoria").astype(str)
    df["Vendedor"] = df["Vendedor"].fillna("Não informado").astype(str)
    return df.dropna(subset=["Data"])

def salvar_dados(df):
    saida = df[COLUNAS].copy()
    saida["Data"] = pd.to_datetime(saida["Data"]).dt.strftime("%Y-%m-%d")
    saida.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    carregar_dados.clear()

def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

df = carregar_dados()

st.title("📊 Dashboard de Análise de Vendas")
st.caption("Acompanhe o faturamento, compare categorias e vendedores e gerencie os registros.")

with st.sidebar:
    st.header("Filtros")
    if df.empty:
        categorias = vendedores = []
        df_filtrado = df.copy()
    else:
        categorias = sorted(df["Categoria"].unique().tolist())
        vendedores = sorted(df["Vendedor"].unique().tolist())
        categorias_sel = st.multiselect("Categorias", categorias, default=categorias)
        vendedores_sel = st.multiselect("Vendedores", vendedores, default=vendedores)
        data_min = df["Data"].min().date()
        data_max = df["Data"].max().date()
        periodo = st.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max)
        if isinstance(periodo, tuple) and len(periodo) == 2:
            inicio, fim = periodo
        else:
            inicio = fim = periodo
        df_filtrado = df[
            df["Categoria"].isin(categorias_sel)
            & df["Vendedor"].isin(vendedores_sel)
            & (df["Data"].dt.date >= inicio)
            & (df["Data"].dt.date <= fim)
        ]

    st.divider()
    st.caption("Os filtros afetam os indicadores e gráficos do painel.")

st.subheader("Visão geral")
total = df_filtrado["Valor_Venda"].sum() if not df_filtrado.empty else 0
qtd = len(df_filtrado)
ticket = total / qtd if qtd else 0
col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento", moeda(total))
col2.metric("Transações", f"{qtd:,}".replace(",", "."))
col3.metric("Ticket médio", moeda(ticket))
col4.metric("Vendedores", df_filtrado["Vendedor"].nunique() if qtd else 0)

if df.empty:
    st.info("A base está vazia. Cadastre uma venda na aba **Gerenciar vendas**.")
else:
    tab1, tab2, tab3 = st.tabs(["📈 Análise", "📋 Vendas", "✏️ Gerenciar vendas"])

    with tab1:
        a, b = st.columns(2)
        with a:
            por_categoria = df_filtrado.groupby("Categoria", as_index=False)["Valor_Venda"].sum().sort_values("Valor_Venda", ascending=False)
            fig = px.bar(por_categoria, x="Categoria", y="Valor_Venda", color="Categoria",
                         title="Faturamento por categoria", text_auto=".2s")
            fig.update_layout(showlegend=False, yaxis_title="Faturamento (R$)", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with b:
            por_vendedor = df_filtrado.groupby("Vendedor", as_index=False)["Valor_Venda"].sum().sort_values("Valor_Venda", ascending=False)
            fig = px.bar(por_vendedor, x="Vendedor", y="Valor_Venda", color="Vendedor",
                         title="Faturamento por vendedor", text_auto=".2s")
            fig.update_layout(showlegend=False, yaxis_title="Faturamento (R$)", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        mensal = df_filtrado.assign(Mês=df_filtrado["Data"].dt.to_period("M").astype(str)).groupby("Mês", as_index=False)["Valor_Venda"].sum()
        fig = px.line(mensal, x="Mês", y="Valor_Venda", markers=True, title="Evolução mensal do faturamento")
        fig.update_layout(yaxis_title="Faturamento (R$)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

        if not por_categoria.empty:
            st.markdown("**Resumo por categoria**")
            resumo = por_categoria.copy()
            resumo["Valor_Venda"] = resumo["Valor_Venda"].map(moeda)
            st.dataframe(resumo, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Registros no período selecionado")
        tabela = df_filtrado.copy()
        tabela["Data"] = tabela["Data"].dt.strftime("%d/%m/%Y")
        tabela["Valor_Venda"] = tabela["Valor_Venda"].map(moeda)
        st.dataframe(tabela, use_container_width=True, hide_index=True)
        csv = df_filtrado[COLUNAS].to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Baixar vendas filtradas (CSV)", csv, "vendas_filtradas.csv", "text/csv")

    with tab3:
        st.subheader("Cadastrar venda")
        with st.form("nova_venda", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nova_data = c1.date_input("Data", value=date.today())
            nova_categoria = c2.text_input("Categoria", placeholder="Ex.: Eletrônicos")
            c3, c4 = st.columns(2)
            novo_valor = c3.number_input("Valor da venda (R$)", min_value=0.01, step=10.0, format="%.2f")
            novo_vendedor = c4.text_input("Vendedor", placeholder="Nome do vendedor")
            cadastrar = st.form_submit_button("Adicionar venda", type="primary")
            if cadastrar:
                if not nova_categoria.strip() or not novo_vendedor.strip():
                    st.error("Preencha a categoria e o vendedor.")
                else:
                    novo = pd.DataFrame([{
                        "Data": pd.Timestamp(nova_data), "Categoria": nova_categoria.strip(),
                        "Valor_Venda": float(novo_valor), "Vendedor": novo_vendedor.strip()
                    }])
                    salvar_dados(pd.concat([df, novo], ignore_index=True))
                    st.success("Venda cadastrada.")
                    st.rerun()

        st.divider()
        st.subheader("Editar ou excluir venda")
        if df.empty:
            st.info("Não há vendas cadastradas.")
        else:
            opcoes = {f"#{i} | {row['Data'].strftime('%d/%m/%Y')} | {row['Categoria']} | {moeda(row['Valor_Venda'])} | {row['Vendedor']}": i
                      for i, row in df.iterrows()}
            escolha = st.selectbox("Selecione um registro", list(opcoes.keys()))
            idx = opcoes[escolha]
            registro = df.loc[idx]
            with st.form("editar_venda"):
                c1, c2 = st.columns(2)
                ed_data = c1.date_input("Data", value=registro["Data"].date(), key="ed_data")
                ed_categoria = c2.text_input("Categoria", value=registro["Categoria"], key="ed_categoria")
                c3, c4 = st.columns(2)
                ed_valor = c3.number_input("Valor (R$)", min_value=0.01, value=float(registro["Valor_Venda"]), step=10.0, key="ed_valor")
                ed_vendedor = c4.text_input("Vendedor", value=registro["Vendedor"], key="ed_vendedor")
                salvar = st.form_submit_button("Salvar alterações", type="primary")
                if salvar:
                    if not ed_categoria.strip() or not ed_vendedor.strip():
                        st.error("Preencha a categoria e o vendedor.")
                    else:
                        df.loc[idx, COLUNAS] = [pd.Timestamp(ed_data), ed_categoria.strip(), float(ed_valor), ed_vendedor.strip()]
                        salvar_dados(df)
                        st.success("Venda atualizada.")
                        st.rerun()
            if st.button("🗑️ Excluir venda selecionada", type="secondary"):
                st.session_state["confirmar_exclusao"] = idx
            if st.session_state.get("confirmar_exclusao") == idx:
                st.warning("Confirme a exclusão deste registro.")
                sim, nao = st.columns(2)
                if sim.button("Confirmar exclusão", type="primary"):
                    salvar_dados(df.drop(index=idx).reset_index(drop=True))
                    st.session_state.pop("confirmar_exclusao", None)
                    st.success("Venda excluída.")
                    st.rerun()
                if nao.button("Cancelar"):
                    st.session_state.pop("confirmar_exclusao", None)
                    st.rerun()

st.divider()
with st.expander("Importar base CSV"):
    arquivo = st.file_uploader("Selecione um CSV com as colunas Data, Categoria, Valor_Venda e Vendedor", type=["csv"])
    if arquivo is not None and st.button("Substituir base atual pelo arquivo", type="primary"):
        try:
            importado = pd.read_csv(arquivo)
            faltantes = [c for c in COLUNAS if c not in importado.columns]
            if faltantes:
                st.error("Colunas ausentes: " + ", ".join(faltantes))
            else:
                importado = importado[COLUNAS].copy()
                importado["Data"] = pd.to_datetime(importado["Data"], errors="raise")
                importado["Valor_Venda"] = pd.to_numeric(importado["Valor_Venda"], errors="raise")
                if (importado["Valor_Venda"] < 0).any():
                    st.error("A base contém valores negativos.")
                else:
                    salvar_dados(importado)
                    st.success("Base importada.")
                    st.rerun()
        except Exception as erro:
            st.error(f"Não foi possível importar o arquivo: {erro}")
