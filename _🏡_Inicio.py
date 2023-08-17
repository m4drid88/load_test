import pandas as pd
import streamlit as st
import altair as alt
import datetime
# from google.oauth2 import service_account
# import pandas_gbq

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


#Preparar Data
@st.cache_data
def load_data():
    # data = pd.read_csv("https://raw.githubusercontent.com/m4drid88/bumeran-tracker/main/dataBumeran.csv?token=GHSAT0AAAAAACGCRESHHHGLDVT74GANFZNYZGT4VJQ").query("subareaTrabajo == 'Planillas' | subareaTrabajo == 'Administración de Personal'")
    data = pd.read_csv("data_bumeran.csv").query("subareaTrabajo == 'Planillas' | subareaTrabajo == 'Administración de Personal'")
    data["fechaPublicacion"] = pd.to_datetime(data["fechaPublicacion"],dayfirst=True).dt.date
    return data

data = load_data()
# print(data["fechaPublicacion"].max())

# data.to_csv("data.csv",index=False)

#Texto Presentación
st.title("📲Bumeran Tracker - Nómina📈")
st.markdown(f"El siguiente reporte realiza el seguimiento de los avisos de trabajo en el portal Bumeran. Los avisos corresponden a posiciones del área de PLANILLAS y ADP. Se han procesado **_{len(data)}_** avisos de empleo.")
#Botones para elegir los días

tiempo_opciones = {"hace 1 semana":7,"hace 15 días":15,"hace 1 mes":30,"desde siempre":9999}
tiempo_selected = st.radio(options=tiempo_opciones.keys(),label="Selecciona el tiempo",horizontal=True)
dias = tiempo_opciones[tiempo_selected]

fecha_actual = datetime.date.today()
fecha_minima = fecha_actual - datetime.timedelta(days=dias)

#Filtrado de data por fecha
@st.cache_data
def filtrar_fecha(data,fecha_minima):
    data_fecha_filtrada = data[data["fechaPublicacion"] >= fecha_minima]
    return data_fecha_filtrada

data_fecha_filtrada = filtrar_fecha(data,fecha_minima)

# Grafico de distribución de posiciones

st.subheader("Distribución por cargos")
# domain = [str(fecha_minima),str(fecha_actual + datetime.timedelta(days=1))]
data_cargo = pd.DataFrame(data_fecha_filtrada["cargoTrabajo"].value_counts()).reset_index(drop=False).rename(columns={"count":"conteo"})
data_cargo["porcentaje"] = round(data_cargo["conteo"] / data_cargo["conteo"].sum() *100,2)
cargos_chart = alt.Chart(data_cargo).mark_bar(color="firebrick").encode(
    y = alt.Y("cargoTrabajo",title="Cargos"),
    x = alt.X("conteo",title="Avisos",axis=alt.Axis(tickRound=True,tickCount=5)),
    tooltip=["cargoTrabajo","conteo","porcentaje"]
).properties(height=alt.Step(50))
st.altair_chart(cargos_chart,use_container_width=True)

# st.divider()

# Gráfico de distribución por fechas
st.subheader("Histórico de avisos de trabajo")
cargos = set(data.cargoTrabajo.unique())

container = st.container()

all_checkbox = container.checkbox("Elegir todos los cargos")

if all_checkbox:
    selected_options = container.multiselect("Selecciona los cargos que quieres ver: ",
         cargos,cargos)
else:
    selected_options =  container.multiselect("Selecciona los cargos que quieres ver: ",
        cargos)


@st.cache_data
def filtrar_fecha_cargo(data,cargos):
    data_fecha_cargo_filtrado = data[data["cargoTrabajo"].isin(cargos)]
    return data_fecha_cargo_filtrado

if selected_options:
    data_fecha_cargo_filtrado = filtrar_fecha_cargo(data_fecha_filtrada,selected_options)
    # data_fecha_cargo_filtrado

    fechas_chart = alt.Chart(data_fecha_cargo_filtrado).mark_bar(color="firebrick").encode(
        x=alt.X("monthdate(fechaPublicacion):O",axis=alt.Axis(title="días")),
        y=alt.Y("count(tituloTrabajo):N",title="Avisos",axis=alt.Axis(tickCount=5)),
        tooltip=[alt.Tooltip("fechaPublicacion",title="Fecha"),
                alt.Tooltip("count(tituloTrabajo):N",title="Avisos"),
                alt.Tooltip("day(fechaPublicacion):O",title="Día de Semana")]
    )
    st.altair_chart(fechas_chart,use_container_width=True)

else:
    st.subheader("Debes elegir al menos un cargo.")


###




# cargos = data.cargoTrabajo.unique()
# selected_cargos = st.multiselect(options=data.cargoTrabajo.unique(),label="Elige los puestos: ",default=cargos)
# selected_data = data[data["cargoTrabajo"].isin(selected_cargos)]

# def generate_altairchart(selected_data,variable,name_variable):
#     dd = pd.DataFrame(selected_data[variable].value_counts()).reset_index(drop=False).rename(columns={"count":"conteo"})
#     dd["porcentaje"] = round(dd["conteo"] / dd["conteo"].sum() *100,2)    
#     chart = alt.Chart(dd).mark_bar(color="firebrick").encode(
#         alt.X(variable).title(name_variable),
#         alt.Y("conteo").title("Avisos"),
#         tooltip=[variable,"conteo","porcentaje"]
#     )
#     return chart

# col1,col2 = st.columns(2)

# with col1:

#     st.subheader("Por Tipo de Trabajo")
#     st.altair_chart(generate_altairchart(selected_data,"tipoTrabajo","Tipo de Trabajo"),use_container_width=True)

#     st.subheader("Confidencialidad")
#     st.altair_chart(generate_altairchart(selected_data,"confidencial","Confidencialidad"),use_container_width=True)

# with col2:

#     st.subheader("Por Modalidad de Trabajo")
#     st.altair_chart(generate_altairchart(selected_data,"modalidadTrabajo","Modalidad de Trabajo"),use_container_width=True)

#     st.subheader("Apto para discapacitado")
#     st.altair_chart(generate_altairchart(selected_data,"aptoDiscapacitado","Apto para discapacitado"),use_container_width=True)