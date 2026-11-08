# Dashboard de Análise de Vendas — Entrega final

## Como executar no Windows
1. Extraia o ZIP para uma pasta.
2. Abra a pasta extraída.
3. Dê dois cliques em `EXECUTAR.bat`.
4. Aguarde a instalação das dependências e a abertura do navegador.

Alternativa pelo terminal:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Funcionalidades
- Dashboard com faturamento, número de transações, ticket médio e vendedores.
- Filtros por categoria, vendedor e período.
- Gráficos de faturamento por categoria, por vendedor e evolução mensal.
- Listagem dos registros e exportação CSV.
- Cadastro, edição e exclusão de vendas.
- Importação de uma nova base CSV.
- Persistência das alterações no arquivo `vendas.csv`.

## Estrutura esperada do CSV
`Data,Categoria,Valor_Venda,Vendedor`

O arquivo `vendas.csv` incluído contém a base inicial da primeira etapa.
