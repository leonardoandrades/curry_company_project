#-------------------------------------------------
#Libraries
#-------------------------------------------------

import pandas as pd
import plotly.express as px
import folium
import streamlit as st

from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
from haversine import haversine


st.set_page_config(page_title="Visão Entregadores", layout='wide')

#-------------------------------------------------
#Functions
#-------------------------------------------------

def clean_code(df1):
    #Remover linhas c/ NaN
    linhas1 = df1['Delivery_person_Age'] != "NaN "
    df1 = df1.loc[linhas1,:]
    
    linhas2 = df1['Road_traffic_density'] != "NaN "
    df1 = df1.loc[linhas2,:]
    
    linhas3 = df1['City'] != "NaN "
    df1 = df1.loc[linhas3,:]
    
    linhas4 = df1['Festival'] != "NaN "
    df1 = df1.loc[linhas4,:]
    
    # 1- Converting Delivery_person_Age into 'int'
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # 2- Converting Ratings into 'float'
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 3- Coverting multiple_deliveries into 'int' and also delete NaN from this col
    linhas1 = df1['multiple_deliveries'] != "NaN "
    df1 = df1.loc[linhas1,:]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # 4-Converting Order_Date into Date format
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],format=('%d-%m-%Y'))
    
    # # 5- Removing space using FOR & strip
    # df1 = df1.reset_index(drop=True)
    
    # for i in range(42805):
    #   df1.loc[i,'ID'] = df1.loc[i,'ID'].strip()
    
    #6- Removing space using only strip
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    
    #7- Adjusting column Time_taken using Lambda
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    #8- Incluing the column wk_year
    df1['wk_year'] = df1['Order_Date'].dt.strftime('%U')
    
    df1 = df1.reset_index(drop=True)
    
    return df1

def df_avg_ratings(df1):
	(df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
	   .groupby(['Delivery_person_ID'])
	   .mean()
	   .round(1))
	return df


def df_avg_ratings_traffic(df1):
	df_aux = (df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']]
			   .groupby(['Road_traffic_density'])
			   .agg({'Delivery_person_Ratings':['mean','std']}))
	
	df_aux.columns = ['mean','std'] #processo feito mais para ajustar o formato df
	df_aux.reset_index()
	return df_aux

def df_avg_ratings_weather(df1):
	df_aux = (df1.loc[:,['Delivery_person_Age','Weatherconditions']]
			     .groupby(['Weatherconditions'])
			     .agg({'Delivery_person_Age':['mean','std']}))
	df_aux.columns = ['mean','std']
	df_aux.reset_index()
	return df_aux


def df_top_rapidos(df1):
	df_aux = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
			   .groupby(['Delivery_person_ID','City'])
			   .mean()
			   .sort_values(['Time_taken(min)','City'],ascending=True).reset_index())
	
	a = df_aux.loc[df_aux['City'] == "Urban"].head(10)
	b = df_aux.loc[df_aux['City'] == "Metropolitian"].head(10)
	c = df_aux.loc[df_aux['City'] == "Semi-Urban"].head(10)
	pd.concat([a,b,c]).reset_index(drop=True)
	return df_aux

def df_top_lentos(df1):
	df_aux = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
			     .groupby(['City','Delivery_person_ID'])
			     .mean().sort_values(['Time_taken(min)','City'],ascending=False).reset_index())
	
	d = df_aux.loc[df_aux['City'] == "Urban"].head(10)
	e = df_aux.loc[df_aux['City'] == "Metropolitian"].head(10)
	f = df_aux.loc[df_aux['City'] == "Semi-Urban"].head(10)
	pd.concat([d,e,f]).reset_index(drop=True)
	return df_aux


#Import Dataset
df = pd.read_csv('dataset/train.csv/train.csv')
df1 = clean_code(df)

#-------------------------------------------------
#Sidebar Streamlit
#-------------------------------------------------

image_path = 'logo1.png'
image = Image.open(image_path)
st.sidebar.image(image,width=250)

st.header('Marketplace - Visão Entregadores')

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider('Até qual valor?',
                                value=datetime(2022,4,13), #standart date
                                min_value=datetime(2022,2,11), #min_date
                                max_value=datetime(2022,4,6), #max_date
                                format='DD-MM-YYYY')# format
#st.header(date_slider)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Traffic Options: ',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])
#st.header(traffic_options)

st.sidebar.markdown("""___""")

#Filtro data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#filtro traffic
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

#--------------------------------------------------
#Layout Streamlit
#--------------------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    st.title('Metricas Gerais')
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
       
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade:',maior_idade)

        with col2:
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade:',menor_idade)

        with col3:
            melhor_cond = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condicao veiculo:',melhor_cond)

        with col4:
            pior_cond = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condicao veiculo:',pior_cond)

    st.markdown("""___""")

    st.title('Avaliacoes')
    
    with st.container():
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('###### Avaliacoes media por entregador:')
            df = df_avg_ratings(df1)
            st.dataframe(df)


        with col2:
            st.markdown('###### Avaliacoes media por transito:')
            df_aux = df_avg_ratings_traffic(df1)
            st.dataframe(df_aux)

            st.markdown('###### Avaliacoes media por clima:')
            df_aux = df_avg_ratings_weather(df1)
            st.dataframe(df_aux)

    st.markdown("""___""")

    with st.container():
        st.title('Velocidade de Entrega')
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('##### Top entregadores mais rapidos:')
            df_aux = df_top_rapidos(df1)
            st.dataframe(df_aux)

        with col2:
            st.markdown('##### Top entregadores mais lentos:')
            df_aux = df_top_lentos(df1)
            st.dataframe(df_aux)
    

