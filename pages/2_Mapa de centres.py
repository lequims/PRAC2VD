import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static


def extreure_coordenades(georeferencia):
    try:
        georeferencia = georeferencia.strip('POINT ()')
        lon, lat = map(float, georeferencia.split())
        return lat, lon
    except:
        return None, None

st.set_page_config(page_title='Mapa de centres per especialitat de Formació Professional', layout='wide')
st.title('Mapa de centres per especialitat de Formació Professional')
oferta_actual = pd.read_csv('data/Oferta_formativa_FPCAT_20240523.csv') 

oferta_actual_fp = oferta_actual[
    (oferta_actual['Tipus de formació'] == 'Cicles formatius de grau mitjà') |
    (oferta_actual['Tipus de formació'] == 'Cicles formatius de grau superior')
]
columnes_oferta_actual_fp = [
    'Codi curs', 'Nom del curs', 'Tipus de formació', 
    'Familia professional', 'Codi centre', 'Nom centre', 
    'Municipi centre', 'Georeferència', 'pàgina web centre'
]
oferta_actual_fp_seleccio = oferta_actual_fp[columnes_oferta_actual_fp]

oferta_inicial = pd.read_csv('data/Oferta_inicial_de_places_dels_estudis_post-obligatoris_20240520.csv') 

columnes_oferta_inicial = [
    'Places ofertades a la preinscripció', 'Curs', 'Codi centre', 'Denominació completa',
    'Nom titularitat', 'Codi ensenyament', 'Nom ensenyament', 
    'Torn', 'Nivell', 'Nombre places'
]

oferta_inicial_seleccio = oferta_inicial[columnes_oferta_inicial]
oferta_inicial_seleccio = oferta_inicial_seleccio[oferta_inicial_seleccio['Curs'] == '2023/2024']

oferta_final = pd.merge(oferta_inicial_seleccio, oferta_actual_fp_seleccio, how='inner', left_on=['Codi centre', 'Codi ensenyament'], right_on=['Codi centre', 'Codi curs'])

# Primer selector
tipus_formacio = st.selectbox(
        'Seleccioneu nivell de formació professional',
         ['Seleccioneu nivell de formació professional'] + sorted(list(oferta_final['Tipus de formació'].unique())),
         disabled= False
         )

if(tipus_formacio != 'Seleccioneu nivell de formació professional'):
        familia_professional_disabled = False
        oferta_final = oferta_final[oferta_final['Tipus de formació'] == tipus_formacio]
else:
        familia_professional_disabled = True
        

familia_professional = st.selectbox(
        'Seleccioneu familia professional',
        ['Seleccioneu familia professional'] + sorted(list(oferta_final['Familia professional'].unique())),
        disabled = familia_professional_disabled,
        )

if(familia_professional != 'Seleccioneu familia professional'):
        nom_ensenyament_disabled = False
        # filtrem dades
        oferta_final = oferta_final[oferta_final['Familia professional'] == familia_professional]
else:
        nom_ensenyament_disabled = True
        

nom_ensenyament = st.selectbox(
        'Seleccioneu cicle', 
        ['Seleccioneu cicle'] + sorted(list(oferta_final['Nom ensenyament'].unique())),
            disabled= nom_ensenyament_disabled,
            
        )
if nom_ensenyament != 'Seleccioneu cicle':
        oferta_final = oferta_final[oferta_final['Nom ensenyament'] == nom_ensenyament]


oferta_final['Latitud'], oferta_final['Longitud'] = zip(*oferta_final['Georeferència'].map(extreure_coordenades))
oferta_final = oferta_final.dropna(subset=['Latitud', 'Longitud'])


if nom_ensenyament != 'Seleccioneu cicle':               
    m = folium.Map(location=[41.3851, 2.1734], zoom_start=8)

    for idx, row in oferta_final.iterrows():
                    
                    popup_content = """
                        <b>{}</b><br>
                        <a href="{}" target="_blank">Página web</a>
                        """.format(row['Denominació completa'], row['pàgina web centre'])
                    
                    folium.Marker(
                        location=[row['Latitud'], row['Longitud']],
                        popup=folium.Popup(popup_content, max_width=450),
                        icon=folium.Icon(color='red')
                    ).add_to(m)

    folium_static(m)
   

            