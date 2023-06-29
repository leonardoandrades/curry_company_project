import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", layout='wide')


#==================================================
#Sidebar
#==================================================

image_path = 'logo1.png'
image = Image.open(image_path)
st.sidebar.image(image,width=250)


st.header('Marketplace - Visão Empresa')

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
	"""
Growth dashboard for construido para acompanhar as metricas de crescimento dos Entregadores e Restaurantes.

	""")
