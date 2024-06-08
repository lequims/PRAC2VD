import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Evolució de la oferta formativa a centres públics i privats', layout='wide')
st.title('Evolució de la oferta formativa a centres públics i privats')


# Dades matrícules
oferta_matricula = pd.read_csv('data/Alumnes_matriculats_per_ensenyament_i_unitats_dels_centres_docents_20240520.csv', low_memory=False)

oferta_matricula = oferta_matricula[
    (oferta_matricula['Nom estudis'] == 'FORMACIÓ PROFESSIONAL') & 
    (oferta_matricula['Codi ensenyament'].notna()) &
    (oferta_matricula['Modalitat']== 'PRESENCIAL')
    ]

columnes_dades_matricula = [
    'Codi centre', 'Denominació completa', 'Nom naturalesa', 'Curs', 'Codi ensenyament', 'Matrícules. Total', 
    'Matrícules. Homes', 'Matrícules. Dones'
]

oferta_matricula = oferta_matricula[columnes_dades_matricula]

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


dades_finals = pd.merge(oferta_matricula, oferta_actual_fp_seleccio, left_on='Codi ensenyament', right_on='Codi curs', how='left')

dades_finals = dades_finals[dades_finals['Tipus de formació'].notna()]

dades_finals_grp = dades_finals.groupby(['Curs', 'Nom naturalesa'])['Matrícules. Total'].sum().reset_index()


fig = px.bar(dades_finals_grp, x='Curs', y='Matrícules. Total', color='Nom naturalesa', title="Nombre de matrícules per curs i tipus de centre",
             labels={"Matrícules. Total": "Nombre matrícules", "Nom naturalesa": "Tipus de centre"}, barmode='group')


st.plotly_chart(fig)
