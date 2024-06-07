import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Desequilibris entre oferta i matrícules', layout='wide')
st.title('Desequilibris entre oferta i matrícules')

st.write('Seleccioneu per obtenir el mapa de saturació dels centres que imparteixen ensenyaments de la branca desitjada.')
# Començo preparant un dataset amb tots els curs FP oferts
oferta_actual = pd.read_csv('data/Oferta_formativa_FPCAT_20240523.csv') 

oferta_actual_fp = oferta_actual[
    (oferta_actual['Tipus de formació'] == 'Cicles formatius de grau mitjà') |
    (oferta_actual['Tipus de formació'] == 'Cicles formatius de grau superior')
]
columnes_oferta_actual_fp = [
    'Codi curs', 'Nom del curs', 'Tipus de formació', 
    'Familia professional'
]
oferta_actual_fp_seleccio = oferta_actual_fp[columnes_oferta_actual_fp]
oferta_actual_fp_seleccio = oferta_actual_fp_seleccio.groupby('Codi curs').first()

# Dades oferta inicial de places
oferta_inicial = pd.read_csv('data/Oferta_inicial_de_places_dels_estudis_post-obligatoris_20240520.csv')

columnes_oferta_inicial = [
    'Curs', 'Codi centre', 'Denominació completa', 'Codi ensenyament', 'Nom ensenyament', 'Nombre places', 
    'Places ofertades a la preinscripció'
]

oferta_inicial_seleccio = oferta_inicial[oferta_inicial['Curs'] == '2022/2023'][columnes_oferta_inicial]

oferta_inicial_seleccio = oferta_inicial_seleccio.groupby(['Codi centre', 'Codi ensenyament']).agg({
    'Nombre places': 'sum',
    'Places ofertades a la preinscripció': 'sum',
    'Denominació completa': 'first',
    'Nom ensenyament': 'first'
}).reset_index()

oferta_inicial_places = pd.merge(
    oferta_inicial_seleccio,
    oferta_actual_fp_seleccio,
    left_on='Codi ensenyament',
    right_on='Codi curs',
    how='inner'
)

# Dades matrícules
oferta_matricula = pd.read_csv('data/Alumnes_matriculats_per_ensenyament_i_unitats_dels_centres_docents_20240520.csv', low_memory=False)

oferta_matricula = oferta_matricula[
    (oferta_matricula['Nom estudis'] == 'FORMACIÓ PROFESSIONAL') & 
    (oferta_matricula['Codi ensenyament'].notna())]

columnes_dades_matricula = [
    'Curs', 'Codi ensenyament', 'Matrícules. Total', 'Codi centre', 'Modalitat', 'Denominació completa'
]

oferta_matricula = oferta_matricula[
    (oferta_matricula['Curs'] == '2022/2023') & 
    (oferta_matricula['Modalitat'] == 'PRESENCIAL')

][columnes_dades_matricula]


oferta_matricula = oferta_matricula[columnes_dades_matricula]

oferta_matricula = oferta_matricula.groupby(['Codi centre', 'Codi ensenyament']).agg({
    'Matrícules. Total': 'sum'
}).reset_index()


df_final = pd.merge(
    oferta_inicial_places,
    oferta_matricula,
    on=['Codi ensenyament', 'Codi centre'],
    how='inner'
)

# Hem combinat els tres datasets

columnes_df_final = [
    'Codi ensenyament', 
    'Nombre places', 
    'Denominació completa', 
    'Nom ensenyament', 
    'Nom del curs',  
    'Tipus de formació', 
    'Familia professional', 
    'Matrícules. Total'
]
df_final = df_final[columnes_df_final]

     

familia_professional = st.selectbox(
        'Seleccioneu familia professional',
        ['Seleccioneu familia professional'] + sorted(list(df_final['Familia professional'].unique()))
        )


def calcula_rati(row):
    matricules_total = row['Matrícules. Total']
    nombre_places = row['Nombre places']
    if matricules_total > nombre_places * 1.20:
        return '>20% de matrícules'
    elif nombre_places > matricules_total * 1.20:
        return '>20% places buides'
    else:
        return 'Oferta equilibrada'

if(familia_professional != 'Seleccioneu familia professional'):
        # filtrem dades
        df_final = df_final[df_final['Familia professional'] == familia_professional]
        
        df_final['Rati alumnat/places'] = df_final.apply(calcula_rati, axis=1)

        color_discrete_map = {
            '>20% més matrícules': 'red',  
            '>20% places buides': 'blue',  
            'Oferta equilibrada': 'green' 
            }
        
        fig = px.scatter(df_final, x='Matrícules. Total', y='Nombre places', color='Rati alumnat/places',
                 color_discrete_map=color_discrete_map,
                 size='Matrícules. Total',
                 hover_data={
                        'Denominació completa': True,  
                        'Nom ensenyament': True,  
                        'Nombre places': True,  
                        'Matrícules. Total': True  
                 },
                 title='Relació entre alumnat matrículat i places en cada centre educatiu',
                 )

        fig.update_layout(width=800, height=600)

        st.plotly_chart(fig)

        




