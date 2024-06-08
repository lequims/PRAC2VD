import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Dades globals de Formació Professional', layout='wide')
st.title('Dades globals de  matrícules de Formació Professional')

st.write('Dades globals de matrícules en estudis de formació professional en modalitat presencial corresponent al curs 2022-2023.')

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


# Dades matrícules
oferta_matricula = pd.read_csv('data/Alumnes_matriculats_per_ensenyament_i_unitats_dels_centres_docents_20240520.csv', low_memory=False)

oferta_matricula = oferta_matricula[
    (oferta_matricula['Nom estudis'] == 'FORMACIÓ PROFESSIONAL') & 
    (oferta_matricula['Codi ensenyament'].notna()) &
    (oferta_matricula['Modalitat']== 'PRESENCIAL') &
    (oferta_matricula['Curs']== '2022/2023')
    
    ]

columnes_dades_matricula = [
    'Codi centre', 'Denominació completa', 'Nom naturalesa', 'Curs', 'Codi ensenyament', 'Matrícules. Total', 
    'Matrícules. Homes', 'Matrícules. Dones'
]

oferta_matricula = oferta_matricula[columnes_dades_matricula]

oferta_matricula = oferta_matricula.groupby(['Codi centre', 'Codi ensenyament']).agg({
    'Matrícules. Total': 'sum',
    'Matrícules. Dones': 'sum',
    'Matrícules. Homes': 'sum',
    'Denominació completa': 'first',
    'Nom naturalesa': 'first'
    
}).reset_index()

dades_fp_globals = pd.merge(
    oferta_matricula,
    oferta_actual_fp_seleccio,
    left_on='Codi ensenyament',
    right_on='Codi curs',
    how='inner'
)

# Branques amb més matricula

df_families = dades_fp_globals.groupby(['Familia professional']).agg({
    'Familia professional': 'first',
    'Matrícules. Total': 'sum',  
    'Matrícules. Dones': 'sum',  
    'Matrícules. Homes': 'sum'   
}).rename(columns={'Codi centre': 'Total'})

df_families = df_families.sort_values(by='Matrícules. Total', ascending=False)

fig = px.bar(df_families, x='Familia professional', y=['Matrícules. Homes', 'Matrícules. Dones'],
             title="Estudiants matrículats en cada branca de FP",
             labels={'value': 'Nombre de matrícules', 'variable': 'Gènere:'},
             barmode='stack')

fig.update_layout(width=800, height=600)
st.plotly_chart(fig)


# Dades sobre centres públics o privats

df_centres = dades_fp_globals.groupby(['Codi centre']).agg({
    'Codi centre': 'first', 
    'Denominació completa': 'first', 
    'Nom naturalesa': 'first', 
    'Matrícules. Total': 'sum',  
    'Matrícules. Dones': 'sum',  
    'Matrícules. Homes': 'sum'   
}).rename(columns={'Codi centre': 'Total'})


df_public_privat = dades_fp_globals.groupby(['Nom naturalesa']).agg({
    'Nom naturalesa': 'first',
    'Matrícules. Total': 'sum',  
    'Matrícules. Dones': 'sum',  
    'Matrícules. Homes': 'sum'   
}).rename(columns={'Codi centre': 'Total'})


fig = px.bar(df_public_privat, x='Nom naturalesa', y='Matrícules. Total',
             title='Matrícules  (Públic vs Privades)',
             labels={'Nom naturalesa': 'Tipus', 'Matrícules. Total': 'Matrícules'})

st.plotly_chart(fig)









