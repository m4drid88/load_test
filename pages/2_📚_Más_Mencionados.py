import pandas as pd
import streamlit as st
import altair as alt
import datetime
# from google.oauth2 import service_account
# import pandas_gbq
import ast

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#Preparar Data
@st.cache_data
def load_data():
    # data = pd.read_csv("https://raw.githubusercontent.com/m4drid88/bumeran-tracker/main/dataBumeran.csv?token=GHSAT0AAAAAACGCRESHHHGLDVT74GANFZNYZGT4VJQ").query("subareaTrabajo == 'Planillas' | subareaTrabajo == 'Administración de Personal'")
    # data = pandas_gbq.read_gbq(query,project_id="mypython-389022",credentials=credentials).query("subareaTrabajo == 'Planillas' | subareaTrabajo == 'Administración de Personal'")
    data = pd.read_csv("data_bumeran.csv").query("subareaTrabajo == 'Planillas' | subareaTrabajo == 'Administración de Personal'")
    data["fechaPublicacion"] = pd.to_datetime(data["fechaPublicacion"],dayfirst=True).dt.date
    return data

data = load_data()

st.title("📚 Más Mencionados")
st.markdown(f"El siguiente reporte realiza el seguimiento de los avisos de trabajo en el portal Bumeran. Los avisos corresponden a posiciones del área de PLANILLAS y ADP. Se han procesado **_{len(data)}_** avisos de empleo.")
st.markdown("En esta página podras visualizar que conocimientos en idiomas, ERP, programas son los más mencionados en los avisos.")

# Gráfico de distribución por fechas

cargos = set(data.cargoTrabajo.unique())

container = st.container()

all_checkbox = container.checkbox("Elegir todos los cargos")

if all_checkbox:
    selected_cargos = container.multiselect("Selecciona los cargos que quieres ver: ",
         cargos,cargos)
else:
    selected_cargos =  container.multiselect("Selecciona los cargos que quieres ver: ",
        cargos)


keywords = {"keywords_idiomas" : ["inglés","portugués","francés","italiano"],
"keywords_programas" : ["excel","word","turecibo","plame","afp","adobe","power bi","power point","sql","python","r"],
"keywords_conocimientos" : ["essalud","indicadores","onp","eps","subsidios","cuentas","kpi","power bi","power point","cts","gratificaciones","utilidades","vacaciones","tareo","asistencia","tiempos","contratos","auditoría","sunafil","sindicato"],
"keywords_erp" : ["sap","ofisis","ofiplan","spring","buk","ssff","starsoft","erp"],
"keywords_carreras" : ["psicología","derecho","administración","contabilidad","economía","ingeniería",]}

options = {"Idiomas":"keywords_idiomas","Programas":"keywords_programas","Conocimientos":"keywords_conocimientos","ERP":"keywords_erp","Carreras":"keywords_carreras"}
keywords_options = st.radio(label="Seleccionar: ",options=options.keys(),horizontal=True)
selected_keywords = options[keywords_options]


if selected_cargos:


    @st.cache_data
    def filtrar_fecha_cargo(data,cargos,sel_keywords):

        data_fecha_cargo_filtrado = data[data["cargoTrabajo"].isin(cargos)]
        data_fecha_cargo_filtrado["skill_keywords"] = data_fecha_cargo_filtrado["skill_keywords"].apply(ast.literal_eval)
        # data_fecha_cargo_filtrado["skill_keywords"] = data_fecha_cargo_filtrado["skill_keywords"].str.replace("[","").str.replace("]","").str.split(",")
        all_keywords = data_fecha_cargo_filtrado["skill_keywords"].explode()
        count_keywords = all_keywords.value_counts().reset_index()
        count_keywords.columns = ['keywords', 'counts']
        length = len(data_fecha_cargo_filtrado) # number of job postings
        count_keywords['percentage'] = count_keywords.counts / length
        keywords_list = keywords[sel_keywords]
        count_keywords = count_keywords[count_keywords.keywords.isin(keywords_list)]
        count_keywords = count_keywords.sort_values(by="percentage",ascending=False)
        # # count_keywords = count_keywords.head(10)
        return count_keywords

    count_keywords = filtrar_fecha_cargo(data,selected_cargos,sel_keywords=selected_keywords)
    # count_keywords

    color_scheme = ['#f6765b', '#da5d46', '#be4531', '#a32c1d',"#880d09"]

    keyword_chart = alt.Chart(count_keywords).mark_bar().encode(
        x = alt.X("percentage",title="% Menciones",axis=alt.Axis(labels=False)),
        y = alt.Y("keywords",title="",axis=alt.Axis(labelFontSize=18),sort="-x"),
        tooltip=[alt.Tooltip("counts:N",title="Menciones"),
                alt.Tooltip("percentage:N", format=".2%",title="% Menciones")],
        color=alt.Color('percentage:N', scale=alt.Scale(range=color_scheme),legend=None)
    ).properties(height=alt.Step(50))

    text = keyword_chart.mark_text(
        align='left', baseline='middle',
        dx=1.5,  # Ajusta la posición horizontal del texto
        fontSize=20

    ).encode(
        text=alt.Text('percentage:N', format=".1%"),
        color=alt.value('white')
    )

    final_chart = keyword_chart + text

    st.altair_chart(final_chart,use_container_width=True)

else:
    st.subheader("Debes elegir al menos un cargo.")