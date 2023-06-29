#-------------------------------------------------
#Libraries
#-------------------------------------------------

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
import streamlit as st

from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
from haversine import haversine

st.set_page_config(page_title="Visão Restaurante", layout='wide')

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

#Import Dataset
df = pd.read_csv('dataset/train.csv/train.csv')
df1 = clean_code(df)

#==================================================
#Sidebar
#==================================================

image_path = 'logo1.png'
image = Image.open(image_path)
st.sidebar.image(image,width=250)


st.header('Marketplace - Visão Restaurantes')

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


#==================================================
#Layout graficos
#================================================== 

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    
    with st.container():
        st.title('Metricas Gerais')
        col1,col2,col3,col4,col5,col6 = st.columns(6)

        with col1:
            delivers = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos: ', delivers)

        with col2:
            
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['distance'] = df1.loc[:,cols].apply(lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
            
            km = df1['distance'].mean().round(2)
            col2.metric('A distância média das entregas:',km)

        with col3:    
            lin = df1['Festival'] == 'Yes'
            tmp_avg = df1.loc[lin,['Time_taken(min)']].mean().round(2)

            col3.metric('Tmp de Entrega Médio c/ Festival', tmp_avg)

        with col4:
            df_aux = df1.loc[:,['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']}).round(2)

            df_aux.columns = ['mean','std']
            
            df_aux = df_aux.reset_index()
            
            lin = df_aux['Festival'] == 'Yes'
            
            std1 = df_aux.loc[lin,'std']
            col4.metric('Desvio Padrão de Entrega médio c/ Festival', std1)

        with col5:
            lin = df1['Festival'] == 'No'
            tmp_avg1 = df1.loc[lin,['Time_taken(min)']].mean().round(2)

            col5.metric('Tmp de Entrega Médio s/ Festival', tmp_avg1)


        with col6:
            df_aux = df1.loc[:,['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']}).round(2)

            df_aux.columns = ['mean','std']
            
            df_aux = df_aux.reset_index()
            
            lin = df_aux['Festival'] == 'No'
            
            std2 = df_aux.loc[lin,'std']
            col6.metric('Desvio Padrão de Entrega médio c/ Festival', std2)
    
    st.markdown("""___""")

    with st.container():
        st.title('Distribuição da distância média por City')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('###### Tmp Médio e STD de entrega por City')
			
            exe3 = df1.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})

            exe3.columns = ['mean','std']
            
            exe3 = exe3.reset_index().round(2)
            
            fig = go.Figure()
            fig1 = fig.add_trace(go.Bar(name='Control',x=exe3['City'],y=exe3['mean'],error_y=dict(type='data',array=exe3['std'])))
            st.plotly_chart(fig1, use_container_width=True)


        with col2:
            st.markdown('###### Tmp Médio e STD de entrega por City e Tráfego')
            exe5 = (df1.loc[:,['City','Road_traffic_density','Time_taken(min)']]
                       .groupby(['City','Road_traffic_density'])
                       .agg({'Time_taken(min)':['mean','std']}))

            exe5.columns = ['mean','std']           
            exe5.reset_index().round(2)
            st.dataframe(exe5)
        

    st.markdown("""___""")

    with st.container():
        #st.title('#3')
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('###### Distruibuição do tempo por City')
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            
            df1['distance'] = df1.loc[:,cols].apply(lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
            
            avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
            
            fig1 = go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['distance'],pull=[0,0.1,0])])
            st.plotly_chart(fig1,use_container_width=True)



        with col2:
            st.markdown('###### Tmp médio por tipo Entrega')
            exe5 = (df1.loc[:,['City','Road_traffic_density','Time_taken(min)']]
                       .groupby(['City','Road_traffic_density'])
                       .agg({'Time_taken(min)':['mean','std']}))

            exe5.columns = ['mean','std']
            exe5 = exe5.reset_index().round(2)
            
            fig = px.sunburst(exe5,path=['City','Road_traffic_density'], values='mean',color='std',color_continuous_scale='RdBu',color_continuous_midpoint=exe5['std'].mean())
            st.plotly_chart(fig,use_container_width=True)

    st.markdown("""___""")








