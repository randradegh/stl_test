import streamlit as st
import pandas as pd
import pydeck as pdk
from pydeck.types import String

import geopandas as gpd

##
# Datos
##

##
# Todo
# 1. Poner un select en el panel lateral para elegir capas
# 2. Incluir la capa de hoteles de DENUE :-)


url = "http://data.insideairbnb.com/mexico/df/mexico-city/2021-12-25/visualisations/listings.csv"
@st.cache(allow_output_mutation=True)
def get_data():
    return pd.read_csv(url)

df_abb = get_data()

# Renombramos la columna name para ser congruente con nom_estab del DENUE
#df.rename(columns={'AvgBill' : 'Bill'})
df_abb = df_abb.rename(columns={'name':'nom_estab','neighbourhood':'nomgeo'})
st.write(df_abb.head(20))

hoteles = pd.read_csv('data/denue_hoteles_cdmx_2020.csv', sep='|')

hoteles = hoteles[['latitud', 'longitud','nom_estab','municipio']]
hoteles = hoteles.rename(columns={'municipio':'nomgeo'})
st.write(hoteles)
##
# Limpieza de datos (RAF).
##



df_abb['price'] = df_abb['price'].replace(regex=['^.'],value='')
# Quitamos las comas
df_abb['price'] = df_abb['price'].replace(regex=[','],value='')
# Lo hacemos flotante
df_abb["price"] = pd.to_numeric(df_abb["price"], downcast="float")

map_data = df_abb[["latitude", "longitude", "nom_estab", "nomgeo"]].dropna(how="any")

st.write(map_data.head(5))

st.error('Integrar para AirBnB')
##
# Límites de las alcaldías
##

# '''
#     ___
#     #### Carga de los datos del los límites de las alcaldías.

#     Este dataset incluye las coordenadas geográficas que forman un poligono para cada 
#     una de las alcadías, además de algunos _features_ más: varios identificadores, nombre de la alcaldía, clave 
#     del municipio, la clave geográfica de la alcaldía, las coordenadas geográficas del centro geométrico de 
#     la alcaldía y los polígonos en dos formatos.

#     Cargamos los datos del archivo correspondiente: *limites_alcaldias_cdmx.geojson*
# '''

# st.code("""
#     shape = gpd.read_file('data/limites_alcaldias_cdmx.geojson')
# """)

# shape = gpd.read_file('data/limites_alcaldias_cdmx.geojson')

# with st.expander("Visualizar/Ocultar límites de alcaldías", expanded=False):
#     st.write(shape.head(3))

# """
#     Más adelante aprederán la manera de visualizar estos polígonos o fronteras de las alcaldías.
# """


shape = gpd.read_file('data/limites_alcaldias_cdmx.geojson')
st.write(shape.head(3))
st.write(shape[shape['nomgeo'] == 'Coyoacán'].g_pnt_2)
shape2 = shape[shape['id'] >= 8]
shape3 = shape[shape['id'] < 8]

##
# Selección de las capas a visualizar
##
sel_capa = st.sidebar.selectbox(
      'Elija las capas a visualizar',
      ('Frontera de Alcaldías', 
      'AirBnB & Hoteles',
      'Hoteles CDMX','Hoteles CDMX y Fronteras','AirBnB Puntos','AirBnB Hexágono','Frontera de Alcaldías Parciales'))

#st.write('Usted seleccionó:', sel_capa)

##
# Configuración para diseñar el mapa de Mapbox
##

## Capas 
bordes = pdk.Layer(
    "GeoJsonLayer",
    data=shape,
    opacity=0.8,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    pickable=True,
    get_elevation=0,
    get_fill_color="[253, 254, 254, 40 ]",
    pointType= 'circle',
    lineWidthScale= 20,
    lineWidthMinPixels= 50,
    get_line_color=[164, 64, 0],
    getPointRadius= 100,
    getLineWidth= 20,    
)
bordes_parcial = pdk.Layer(
    "GeoJsonLayer",
    data=shape3,
    opacity=0.8,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    pickable=True,
    get_elevation=10,
    pointType= 'circle',
    lineWidthScale= 20,
    lineWidthMinPixels= 50,
    get_line_color=[164, 64, 0],
    getPointRadius= 100,
    getLineWidth= 20,    
    get_fill_color=[229, 152, 102, 10 ],
)
puntos_abb=pdk.Layer(
    'ScatterplotLayer',
    data=map_data, 
    get_position='[longitude, latitude]',
    get_radius=30,          # Radius is given in meters
    get_fill_color=[230, 126, 34, 90],
    elevation_scale=0,
    #elevation_range=[0, 1000],
    pickable=True
)

hoteles=pdk.Layer(
    'ScatterplotLayer',
    data=hoteles, 
    get_position='[longitud, latitud]',
    get_radius=30,          # Radius is given in meters
    get_fill_color='[5, 0, 160]',
    elevation_scale=0,
    #elevation_range=[0, 1000],
    pickable=True
)

hexagonos_abb=pdk.Layer(
    'HexagonLayer',
    data=map_data, 
    get_position='[longitude, latitude]',
    get_radius=30,          # Radius is given in meters
    get_fill_color=[230, 126, 34, 250],
    radius=40,
    elevation_scale=2,
    elevation_range=[0, 1000],
    extruded=True,
    pickable=True
)
# text = pdk.Layer(
#     "TextLayer",
#     data=shape,
#     pickable=True,
#     get_position='geometry',
#     get_text="nomgeo",
#     get_size=60,
#     get_color=[160,64,0,20],
#     get_angle=0,
#     # Note that string constants in pydeck are explicitly passed as strings
#     # This distinguishes them from columns in a data set
#     get_text_anchor=String("middle"),
#     get_alignment_baseline=String("center"),
# )
view_state = pdk.ViewState(
    latitude=19.3266,
    longitude=-99.1490,
    zoom=9.5,
    pitch=0
)

my_tooltip={
    "html": 
    "Ejercicio con <i>Maxbox</i>"
    "<br><b>Nombre:</b> {nom_estab}"
    "<br><b>Alcaldía:</b> {nomgeo}",
    "style": {"color": "#FAFAFA", 
            "background-color":"#9a7d0a",
            "z-index":2,}
}

##
# Definición de las capas a mostrar
##
if sel_capa == 'AirBnB Puntos':
    capas = [ bordes,puntos_abb]
elif sel_capa == 'AirBnB Hexágono':
    capas = [bordes,hexagonos_abb]
elif sel_capa == 'Frontera de Alcaldías':
    capas = [bordes]
elif sel_capa == 'Frontera de Alcaldías Parciales':
    capas = [bordes_parcial]
elif sel_capa == 'Hoteles CDMX y Fronteras':
    capas = [bordes,hoteles]
elif sel_capa == 'Hoteles CDMX':
    capas = [hoteles]
elif sel_capa == 'AirBnB & Hoteles' :
    capas = [bordes, puntos_abb, hoteles]


m1 = st.pydeck_chart(pdk.Deck(map_style='mapbox://styles/mapbox/light-v10',
    layers=[capas], 
    initial_view_state=view_state, 
    tooltip=my_tooltip))