import streamlit as st
import datetime
st.title("⚠️ Acerca de")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("La información de este reporte **_Bumeran Tracker: Nómina_** ha sido recopilada del portal de empleos Bumeran.")

fecha_actual = datetime.date.today()
st.subheader(f"Última actualización: {fecha_actual}.")

st.subheader("🛠️ Herramientas Utilizadas")
st.markdown(" - Python\n - Librerias: Pandas, Altoir, Streamlit, Spacy.\n - Github")

st.subheader("📌 TO DO: ")
st.markdown("- Automatizar la actualización la base de datos con un entorno virtual.\n - Ampliar las áreas de Recursos Humanos a analizar.")

st.subheader("📩 Contacto: ")
st.markdown("- Correo: josemelgarejo88@gmail.com\n - Linkedin: [José Melgarejo](https://www.linkedin.com/in/jose-melgarejo/)")