import streamlit as st
import pandas as pd
import io

import warnings
warnings.filterwarnings("ignore")

# --- Configurações da Página ---
st.set_page_config(
    page_title="Agente AI - Análise de Dados",
    page_icon="📊",
    layout="wide"
)

# --- Função para carregar e preparar os dados ---
@st.cache_data
def carregar_dados(caminho_arquivo):
    """
    Carrega os dados do arquivo CSV e realiza uma limpeza inicial.
    """
    try:
        df = pd.read_csv(caminho_arquivo)
        # --- Limpeza e conversão de tipos ---
        # Converte a coluna 'lance máx' para um tipo numérico (float)
        # Remove o símbolo '%' e substitui a vírgula por ponto decimal
        if 'lance máx' in df.columns:
            df['lance máx'] = df['lance máx'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
        else:
            st.error("A coluna 'lance máx' não foi encontrada no arquivo.")
            return pd.DataFrame() # Retorna um DataFrame vazio se a coluna não existir

        # Garante que 'prazo rest' é um tipo numérico
        if 'prazo rest' in df.columns:
            df['prazo rest'] = pd.to_numeric(df['prazo rest'], errors='coerce').fillna(0)
        else:
            st.error("A coluna 'prazo rest' não foi encontrada no arquivo.")
            return pd.DataFrame() # Retorna um DataFrame vazio se a coluna não existir

        return df
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado. Verifique se ele está no mesmo diretório que o script.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar ou processar o arquivo: {e}")
        return None


# --- Função para converter o DataFrame para Excel em memória ---
def to_excel(df):
    """
    Converte um DataFrame para um arquivo Excel (.xlsx) em bytes.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='DadosFiltrados')
    processed_data = output.getvalue()
    return processed_data


# --- Carregamento dos dados ---
df_original = carregar_dados("result.csv")
df_original = df_original.drop('Unnamed: 0', axis=1)

# Se o DataFrame não for carregado com sucesso, interrompe a execução
if df_original is None or df_original.empty:
    st.warning("Por favor, carregue um arquivo CSV válido para continuar.")
    st.stop()

# --- Layout Centralizado: Imagem e Título ---
col1, col2, col3 = st.columns([1, 2, 1]) # Divide a tela em 3 colunas para centralizar

with col2:
    # Adicione o nome do seu arquivo de imagem aqui.
    # A imagem deve estar na mesma pasta que o seu script.
    try:
        st.image("a.jpeg", use_column_width=True)
    except Exception:
        st.warning("Arquivo 'imagem.png' não encontrado. Coloque um arquivo de imagem no diretório para exibi-lo aqui.")

    st.title("Agente AI para Análise de Dados")


# --- Barra Lateral (Sidebar) para Filtros e Ordenação ---
st.sidebar.header("Opções de Filtro e Ordenação")

# Clonar o dataframe para manipulação
df_filtrado = df_original.copy()

# --- Filtro: Prazo Restante ---
st.sidebar.subheader("Filtrar por 'Prazo Restante'")
operador_prazo = st.sidebar.selectbox(
    "Condição para o prazo:",
    ["Nenhum", "Maior que", "Menor que", "Igual a"],
    key="op_prazo"
)
if operador_prazo != "Nenhum":
    valor_prazo = st.sidebar.number_input("Valor do prazo:", step=1, key="val_prazo")

    if operador_prazo == "Maior que":
        df_filtrado = df_filtrado[df_filtrado['prazo rest'] > valor_prazo]
    elif operador_prazo == "Menor que":
        df_filtrado = df_filtrado[df_filtrado['prazo rest'] < valor_prazo]
    elif operador_prazo == "Igual a":
        df_filtrado = df_filtrado[df_filtrado['prazo rest'] == valor_prazo]


# --- Filtro: % Lance Máximo ---
st.sidebar.subheader("Filtrar por 'lance máx'")
operador_lance = st.sidebar.selectbox(
    "Condição para o lance:",
    ["Nenhum", "Maior que", "Menor que", "Igual a"],
    key="op_lance"
)
if operador_lance != "Nenhum":
    valor_lance = st.sidebar.number_input("Valor do % de lance (ex: 50.5):", step=0.1, format="%.2f", key="val_lance")

    if operador_lance == "Maior que":
        df_filtrado = df_filtrado[df_filtrado['lance máx'] > valor_lance]
    elif operador_lance == "Menor que":
        df_filtrado = df_filtrado[df_filtrado['lance máx'] < valor_lance]
    elif operador_lance == "Igual a":
        df_filtrado = df_filtrado[df_filtrado['lance máx'] == valor_lance]


# --- Ordenação ---
st.sidebar.subheader("Ordenar Tabela")
colunas_ordenacao = st.sidebar.multiselect(
    "Ordenar por:",
    options=['prazo rest', 'lance máx'],
    default=[] # Opcional: defina uma coluna padrão para ordenação
)

ordem_ascendente = st.sidebar.radio(
    "Ordem:",
    ["Ascendente", "Descendente"],
    key="ordem"
) == "Ascendente"

if colunas_ordenacao:
    df_filtrado = df_filtrado.sort_values(
        by=colunas_ordenacao,
        ascending=ordem_ascendente
    )


# --- Exibição da Tabela ---
st.header("Dados Analisados")
st.dataframe(df_filtrado, use_container_width=True)


# --- Botão de Download ---
if not df_filtrado.empty:
    st.subheader("Download dos Dados")
    st.markdown("Baixe a tabela (com os filtros aplicados) em formato Excel.")

    # Converte o dataframe filtrado para o formato Excel
    dados_excel = to_excel(df_filtrado)

    st.download_button(
        label="📥 Baixar como Excel (.xlsx)",
        data=dados_excel,
        file_name="dados_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )