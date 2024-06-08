import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Evolució de matrícules per especialitat de Formació Professional', layout='wide')
st.title('Evolució de matrícules per especialitat de Formació Professional')
st.write('Seleccioneu l\'especialitat desitjada per a consultar la seva evolució d\'alumnat matrículat en els darrer anys en modalitat presencial.')

# Dades matrícules
oferta_matricula = pd.read_csv('data/Alumnes_matriculats_per_ensenyament_i_unitats_dels_centres_docents_20240520.csv', low_memory=False)

oferta_matricula = oferta_matricula[
    (oferta_matricula['Nom estudis'] == 'FORMACIÓ PROFESSIONAL') & 
    (oferta_matricula['Codi ensenyament'].notna()) &
    (oferta_matricula['Modalitat']== 'PRESENCIAL')
    ]

columnes_dades_matricula = [
    'Curs', 'Codi ensenyament', 'Matrícules. Total', 
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


# Primer selector
tipus_formacio = st.selectbox(
        'Seleccioneu nivell de formació professional',
         ['Seleccioneu nivell de formació professional'] + list(dades_finals['Tipus de formació'].unique()),
         disabled= False
         )

if(tipus_formacio != 'Seleccioneu nivell de formació professional'):
        familia_professional_disabled = False
        dades_finals = dades_finals[dades_finals['Tipus de formació'] == tipus_formacio]
else:
        familia_professional_disabled = True
        

familia_professional = st.selectbox(
        'Seleccioneu familia professional',
        ['Seleccioneu familia professional'] + sorted(list(dades_finals['Familia professional'].unique())),
        disabled = familia_professional_disabled,
        )

if(familia_professional != 'Seleccioneu familia professional'):
        nom_ensenyament_disabled = False
        # filtrem dades
        dades_finals = dades_finals[dades_finals['Familia professional'] == familia_professional]
else:
        nom_ensenyament_disabled = True
        

nom_ensenyament = st.selectbox(
        'Seleccioneu cicle', 
        ['Seleccioneu cicle'] + sorted(list(dades_finals['Nom del curs'].unique())),
            disabled= nom_ensenyament_disabled,
            
        )
if nom_ensenyament != 'Seleccioneu cicle':
        dades_finals = dades_finals[dades_finals['Nom del curs'] == nom_ensenyament]


def plot_interactive(dataframe):
    # Colors de les tres variables
    color_map = {
        'Matrícules. Total': 'blue',  
        'Matrícules. Homes': 'green',  
        'Matrícules. Dones': 'red'  
    }

    
    fig = px.line(dataframe, x='Curs', y=['Matrícules. Total', 'Matrícules. Homes', 'Matrícules. Dones'],
                  labels={
                      "value": "Total de matrícules",  
                      "variable": "Tipus"  
                  },
                  title='Evolució de matrícules por curs escolar',
                  color_discrete_map=color_map)
    
    fig.update_layout(
        xaxis_title='Curs',
        yaxis_title='Nombre d\'estudiants matrículats',
        legend_title='Segons gènere',
        hovermode='x',
        width=800,  
        height=600  
    )

    # Permetre seleccionar o no seleccionar tipus
    fig.update_traces(mode='lines+markers')

    return fig



if nom_ensenyament != 'Seleccioneu cicle':    

    # Agrupar dades per curs
    dades_finals_grp = dades_finals.groupby(['Curs', 'Codi ensenyament']).agg({
    'Matrícules. Total': 'sum',
    'Matrícules. Homes': 'sum',
    'Matrícules. Dones': 'sum'
    }).reset_index()

    fig = plot_interactive(dades_finals_grp)
         
    st.plotly_chart(fig)

    
