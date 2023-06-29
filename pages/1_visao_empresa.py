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

st.set_page_config(page_title="Visão Empresa", layout='wide')

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

def orders_per_day(df1):
	exe1 = df1.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()
	fig = px.bar(exe1, x='Order_Date',y='ID')
	return fig
	
def graph_type_traffic(df1):
	exe3 = (df1.loc[:,['ID','Road_traffic_density']]
			   .groupby('Road_traffic_density')
			   .count().reset_index())
	exe3['Perc Entregas'] = exe3['ID'] / exe3['ID'].sum()
	
	fig = px.pie(exe3, names= 'Road_traffic_density', values='Perc Entregas')
	return fig

def graph_order_city_traffic(df1):
	exe4 = (df1.loc[:,['ID','Road_traffic_density','City']]
			   .groupby(['City','Road_traffic_density'])
			   .count().reset_index())
	fig = px.scatter(exe4, x='City', y='Road_traffic_density', size='ID')
	return fig

def graph_orders_week(df1):
	df1['wk_year'] = df1['Order_Date'].dt.strftime('%U')
	exe2 = df1.loc[:,['wk_year','ID']].groupby('wk_year').count().reset_index()
	
	fig = px.line(exe2,x='wk_year',y='ID')
	return fig

def graph_orders_deliver(df1):
	df_aux = df1.loc[:,['ID','wk_year']].groupby(['wk_year']).count().reset_index()
	df_aux2 = df1.loc[:,['Delivery_person_ID','wk_year']].groupby(['wk_year']).nunique().reset_index()
	df_final = df_aux.merge(df_aux2, how='inner', on='wk_year')
	df_final['ratio'] = df_final['ID'] / df_final['Delivery_person_ID']
	
	fig = px.line(df_final,x='wk_year', y='ratio')
	return fig

def graph_geo(df1):
	df_aux = (df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
				 .groupby(['City','Road_traffic_density'])
				 .median().reset_index())
	
	map = folium.Map()
	
	for index, location_info in df_aux.iterrows():
		folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']]).add_to(map)
	
	folium_static(map,width=1024,height=600)
	return

#Import Dataset
df = pd.read_csv('dataset/train.csv/train.csv')
df1 = clean_code(df)

#-------------------------------------------------
#Sidebar Streamlit
#-------------------------------------------------

image_path = 'logo1.png'
image = Image.open(image_path)
st.sidebar.image(image,width=250)


st.header('Marketplace - Visão Empresa')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geo'])

with tab1:
    with st.container():
        st.markdown('# Orders per day')
        fig = orders_per_day(df1)    
        st.plotly_chart(fig,use_container_width=True)


    with st.container():
        col1,col2 = st.columns(2)

        with col1:
            fig = graph_type_traffic(df1)
            st.header('% Type of traffic')
            st.plotly_chart(fig,use_container_width=True)

        with col2:
            st.header('Orders per City / Traffic')
            fig = graph_order_city_traffic(df1)
            st.plotly_chart(fig,use_container_width=True)

    with st.container():
        st.header('Database:')
        st.dataframe(df1)
        
        
with tab2:
    with st.container():
        st.header('Orders per Week')
        fig = graph_orders_week(df1)
        st.plotly_chart(fig,use_container_width=True)

    with st.container():
        st.header('Orders per Deliver per Week')
        fig = graph_orders_deliver(df1)
        st.plotly_chart(fig,use_container_width=True)


with tab3:
    st.header('Geo View')
    graph_geo(df1)


        











