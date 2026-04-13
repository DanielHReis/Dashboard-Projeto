import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da pagina
st.set_page_config(layout="wide", page_title="Dashboard de Salários em Data Science")
st.title("Dashboard de Salários em Data Science")
st.markdown("Análise interativa dos salários da área de dados entre 2020 e 2022.")

# Carregar e tratamento de dados
@st.cache_data
def load_data():
    df = pd.read_csv('ds_salaries.csv')
    
    df.drop(columns=['Unnamed: 0', 'salary', 'salary_currency'], inplace=True)
    df.rename(columns={
        'work_year': 'Ano de Referencia',
        'experience_level': 'Nivel de Experiencia',
        'salary_in_usd': 'Salario em Dolar(Anual)',
        'employment_type': 'Tipo de Contratacao',
        'job_title': 'Cargo',
        'employee_residence': 'Residencia Funcionario',
        'remote_ratio': 'Modalidade de Trabalho',
        'company_location': 'Residencia Empresa',
        'company_size': 'Tamanho da Empresa'
    }, inplace=True)
    
    experiencia = {'EN': 'Junior', 'MI': 'Pleno', 'SE': 'Senior', 'EX': 'Executivo'}
    df['Nivel de Experiencia'] = df['Nivel de Experiencia'].replace(experiencia)
    
    contratacao = {'FT': 'Tempo Integral', 'PT': 'Meio Periodo', 'FL': 'FreeLancer', 'CT': 'Contrato(PJ)'}
    df['Tipo de Contratacao'] = df['Tipo de Contratacao'].replace(contratacao)
    
    modalidade = {0: 'Presencial', 50: 'Hibrido', 100: 'Online'}
    df['Modalidade de Trabalho'] = df['Modalidade de Trabalho'].replace(modalidade)
    df['Modalidade de Trabalho'] = df['Modalidade de Trabalho'].astype(str)
    
    tamanho = {'L': 'Grande', 'S': 'Pequena', 'M': 'Media'}
    df['Tamanho da Empresa'] = df['Tamanho da Empresa'].replace(tamanho)
    
    cargos = {
        'Data Scientist': 'Cientista de Dados',
        'Data Analyst': 'Analista de Dados',
        'Data Engineer': 'Engenheiro de Dados',
        'Machine Learning Engineer': 'Engenheiro de Machine Learning'
    }
    df['Cargo'] = df['Cargo'].replace(cargos)

    df['Ano de Referencia'] = df['Ano de Referencia'].astype(int)
    
    return df

df = load_data()

# Filtros laterais
st.sidebar.header("Filtros Globais")

anos = st.sidebar.multiselect(
    "Selecione o(s) Ano(s)",
    options=sorted(df['Ano de Referencia'].unique()),
    default=sorted(df['Ano de Referencia'].unique())
)

niveis = st.sidebar.multiselect(
    "Nível de Experiência",
    options=df['Nivel de Experiencia'].unique(),
    default=df['Nivel de Experiencia'].unique()
)

modalidades = st.sidebar.multiselect(
    "Modalidade de Trabalho",
    options=df['Modalidade de Trabalho'].unique(),
    default=df['Modalidade de Trabalho'].unique()
)

paises = st.sidebar.multiselect(
    "País do Funcionário",
    options=sorted(df['Residencia Funcionario'].unique()),
    default=sorted(df['Residencia Funcionario'].unique())
)

df_sel = df[
    (df['Ano de Referencia'].isin(anos)) &
    (df['Nivel de Experiencia'].isin(niveis)) &
    (df['Modalidade de Trabalho'].isin(modalidades)) &
    (df['Residencia Funcionario'].isin(paises))
]

st.subheader("Visão Geral")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Salário Médio (USD)", f"${df_sel['Salario em Dolar(Anual)'].mean():,.0f}")
with col2:
    st.metric("Total de Profissionais", f"{df_sel.shape[0]:,}")
with col3:
    st.metric("Cargos Únicos", f"{df_sel['Cargo'].nunique()}")

# GRÁFICO 1: Top 10 Cargos
st.subheader("Top 10 Cargos com Maior Salário Médio")
top_cargos = df_sel.groupby('Cargo')['Salario em Dolar(Anual)'].mean().sort_values(ascending=False).head(10).reset_index()
fig_cargos = px.bar(top_cargos, x='Salario em Dolar(Anual)', y='Cargo', orientation='h', text_auto=True, title="Média Salarial por Cargo")
fig_cargos.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_cargos, use_container_width=True)

# GRÁFICO 2: Boxplot por Experiência
st.subheader("Distribuição Salarial por Nível de Experiência")
fig_experiencia = px.box(df_sel, x='Nivel de Experiencia', y='Salario em Dolar(Anual)', color='Nivel de Experiencia', title="Variação Salarial (Júnior a Executivo)")
st.plotly_chart(fig_experiencia, use_container_width=True)

# GRÁFICO 3: Evolução Anual
st.subheader("Evolução do Salário Médio por Ano")
evolucao = df_sel.groupby('Ano de Referencia')['Salario em Dolar(Anual)'].mean().reset_index()
fig_evolucao = px.line(evolucao, x='Ano de Referencia', y='Salario em Dolar(Anual)', markers=True, title="Salário Médio Anual (USD)")
fig_evolucao.update_xaxes(
    tickmode='array',
    tickvals=evolucao['Ano de Referencia'].unique(),
    ticktext=[str(a) for a in sorted(evolucao['Ano de Referencia'].unique())]
)
st.plotly_chart(fig_evolucao, use_container_width=True)

# GRÁFICO 4: Modalidade de Trabalho
st.subheader("Impacto da Modalidade de Trabalho no Salário")
fig_modalidade = px.box(df_sel, x='Modalidade de Trabalho', y='Salario em Dolar(Anual)', color='Modalidade de Trabalho', title="Comparativo: Presencial vs Híbrido vs Online")
st.plotly_chart(fig_modalidade, use_container_width=True)

# GRÁFICO 5: Análise Geográfica
st.markdown("---")
st.header("Análise Geográfica de Salários")
st.markdown("Explore como os salários variam ao redor do mundo — tanto pela localização dos **funcionários** quanto das **empresas**.")

# Seletor de perspectiva
perspectiva = st.radio(
    "Visualizar por:",
    options=["Residência do Funcionário", "Localização da Empresa"],
    horizontal=True
)

coluna_geo = 'Residencia Funcionario' if perspectiva == "Residência do Funcionário" else 'Residencia Empresa'
label_geo = "País do Funcionário" if perspectiva == "Residência do Funcionário" else "País da Empresa"

# Tabela de conversão ISO-2 → ISO-3
ISO2_TO_ISO3 = {
    'AF':'AFG','AL':'ALB','DZ':'DZA','AD':'AND','AO':'AGO','AR':'ARG','AM':'ARM','AU':'AUS',
    'AT':'AUT','AZ':'AZE','BS':'BHS','BH':'BHR','BD':'BGD','BY':'BLR','BE':'BEL','BZ':'BLZ',
    'BJ':'BEN','BT':'BTN','BO':'BOL','BA':'BIH','BW':'BWA','BR':'BRA','BN':'BRN','BG':'BGR',
    'BF':'BFA','BI':'BDI','CV':'CPV','KH':'KHM','CM':'CMR','CA':'CAN','CF':'CAF','TD':'TCD',
    'CL':'CHL','CN':'CHN','CO':'COL','KM':'COM','CG':'COG','CD':'COD','CR':'CRI','HR':'HRV',
    'CU':'CUB','CY':'CYP','CZ':'CZE','DK':'DNK','DJ':'DJI','DO':'DOM','EC':'ECU','EG':'EGY',
    'SV':'SLV','GQ':'GNQ','ER':'ERI','EE':'EST','SZ':'SWZ','ET':'ETH','FJ':'FJI','FI':'FIN',
    'FR':'FRA','GA':'GAB','GM':'GMB','GE':'GEO','DE':'DEU','GH':'GHA','GR':'GRC','GT':'GTM',
    'GN':'GIN','GW':'GNB','GY':'GUY','HT':'HTI','HN':'HND','HU':'HUN','IS':'ISL','IN':'IND',
    'ID':'IDN','IR':'IRN','IQ':'IRQ','IE':'IRL','IL':'ISR','IT':'ITA','JM':'JAM','JP':'JPN',
    'JO':'JOR','KZ':'KAZ','KE':'KEN','KI':'KIR','KW':'KWT','KG':'KGZ','LA':'LAO','LV':'LVA',
    'LB':'LBN','LS':'LSO','LR':'LBR','LY':'LBY','LI':'LIE','LT':'LTU','LU':'LUX','MG':'MDG',
    'MW':'MWI','MY':'MYS','MV':'MDV','ML':'MLI','MT':'MLT','MH':'MHL','MR':'MRT','MU':'MUS',
    'MX':'MEX','FM':'FSM','MD':'MDA','MC':'MCO','MN':'MNG','ME':'MNE','MA':'MAR','MZ':'MOZ',
    'MM':'MMR','NA':'NAM','NR':'NRU','NP':'NPL','NL':'NLD','NZ':'NZL','NI':'NIC','NE':'NER',
    'NG':'NGA','NO':'NOR','OM':'OMN','PK':'PAK','PW':'PLW','PA':'PAN','PG':'PNG','PY':'PRY',
    'PE':'PER','PH':'PHL','PL':'POL','PT':'PRT','QA':'QAT','RO':'ROU','RU':'RUS','RW':'RWA',
    'KN':'KNA','LC':'LCA','VC':'VCT','WS':'WSM','SM':'SMR','ST':'STP','SA':'SAU','SN':'SEN',
    'RS':'SRB','SC':'SYC','SL':'SLE','SG':'SGP','SK':'SVK','SI':'SVN','SB':'SLB','SO':'SOM',
    'ZA':'ZAF','SS':'SSD','ES':'ESP','LK':'LKA','SD':'SDN','SR':'SUR','SE':'SWE','CH':'CHE',
    'SY':'SYR','TW':'TWN','TJ':'TJK','TZ':'TZA','TH':'THA','TL':'TLS','TG':'TGO','TO':'TON',
    'TT':'TTO','TN':'TUN','TR':'TUR','TM':'TKM','TV':'TUV','UG':'UGA','UA':'UKR','AE':'ARE',
    'GB':'GBR','US':'USA','UY':'URY','UZ':'UZB','VU':'VUT','VE':'VEN','VN':'VNM','YE':'YEM',
    'ZM':'ZMB','ZW':'ZWE','HK':'HKG','MK':'MKD','TZ':'TZA','CW':'CUW','BQ':'BES',
}

def add_iso3(dataframe, col_iso2):
    dataframe = dataframe.copy()
    dataframe['iso3'] = dataframe[col_iso2].map(ISO2_TO_ISO3)
    return dataframe

# Agregar dados por país
df_geo = df_sel.groupby(coluna_geo).agg(
    Salario_Medio=('Salario em Dolar(Anual)', 'mean'),
    Total_Profissionais=('Salario em Dolar(Anual)', 'count'),
    Salario_Mediano=('Salario em Dolar(Anual)', 'median'),
    Salario_Max=('Salario em Dolar(Anual)', 'max'),
).reset_index()
df_geo.columns = [label_geo, 'Salário Médio (USD)', 'Nº de Profissionais', 'Salário Mediano (USD)', 'Salário Máximo (USD)']
df_geo['Salário Médio (USD)'] = df_geo['Salário Médio (USD)'].round(0)
df_geo['Salário Mediano (USD)'] = df_geo['Salário Mediano (USD)'].round(0)
df_geo = add_iso3(df_geo, label_geo)

# MAPA 1: Coroplético de salário médio
st.subheader(f"Mapa de Calor — Salário Médio por {label_geo}")

fig_map = px.choropleth(
    df_geo,
    locations='iso3',
    locationmode="ISO-3",
    color='Salário Médio (USD)',
    hover_name=label_geo,
    hover_data={
        'Nº de Profissionais': True,
        'Salário Médio (USD)': ':,.0f',
        'Salário Mediano (USD)': ':,.0f',
        label_geo: False
    },
    color_continuous_scale='Viridis',
    title=f"Salário Médio em USD por {label_geo}",
    labels={'Salário Médio (USD)': 'Salário Médio (USD)'}
)
fig_map.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
    coloraxis_colorbar=dict(title="USD"),
    height=500,
    margin=dict(l=0, r=0, t=40, b=0)
)
st.plotly_chart(fig_map, use_container_width=True)

# MAPA 2: Mapa de bolhas — volume de profissionais
st.subheader(f"Mapa de Bolhas — Volume de Profissionais por {label_geo}")

fig_bubble = px.scatter_geo(
    df_geo,
    locations='iso3',
    locationmode="ISO-3",
    size='Nº de Profissionais',
    color='Salário Médio (USD)',
    hover_name=label_geo,
    hover_data={
        'Nº de Profissionais': True,
        'Salário Médio (USD)': ':,.0f',
        label_geo: False
    },
    color_continuous_scale='RdYlGn',
    size_max=60,
    title=f"Volume de Profissionais e Salário Médio por {label_geo}",
)
fig_bubble.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
    coloraxis_colorbar=dict(title="USD"),
    height=500,
    margin=dict(l=0, r=0, t=40, b=0)
)
st.plotly_chart(fig_bubble, use_container_width=True)

# Comparativo: Salário por país (top 10)
st.subheader(f"Top 10 Países por Salário Médio")

col_esquerda, col_direita = st.columns(2)

with col_esquerda:
    top10 = df_geo.nlargest(10, 'Salário Médio (USD)')
    fig_top = px.bar(
        top10,
        x='Salário Médio (USD)',
        y=label_geo,
        orientation='h',
        color='Salário Médio (USD)',
        color_continuous_scale='Viridis',
        text_auto=True,
        title="Maiores Salários Médios"
    )
    fig_top.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    fig_top.update_coloraxes(showscale=False)
    st.plotly_chart(fig_top, use_container_width=True)

with col_direita:
    paises_volume = df_geo[df_geo['Nº de Profissionais'] >= 3].nlargest(10, 'Nº de Profissionais')
    fig_vol = px.bar(
        paises_volume,
        x='Nº de Profissionais',
        y=label_geo,
        orientation='h',
        color='Nº de Profissionais',
        color_continuous_scale='Blues',
        text_auto=True,
        title="Países com Mais Profissionais (mín. 3) — Top 10"
    )
    fig_vol.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    fig_vol.update_coloraxes(showscale=False)
    st.plotly_chart(fig_vol, use_container_width=True)


# Tabela resumo por país
with st.expander("Ver tabela completa de dados por país"):
    st.dataframe(
        df_geo.drop(columns=['iso3']).sort_values('Salário Médio (USD)', ascending=False).reset_index(drop=True),
        use_container_width=True
    )

# Rodapé
st.caption(f"Dados filtrados com {df_sel.shape[0]} registros de um total de {df.shape[0]}.")