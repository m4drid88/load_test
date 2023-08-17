import pandas as pd
from dotenv import load_dotenv
import os
import requests
from random import randint
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import logging
import string
from unidecode import unidecode
import re
import spacy
from spacy.symbols import ORTH

# load_dotenv(".env")
SCRAPE_OPS_KEY = os.getenv("SCRAPEOP_KEY")
logging.basicConfig(filename="log.txt", level=logging.INFO,
                    format="%(asctime)s %(message)s", filemode="a")

def get_headers_list():
  response = requests.get('http://headers.scrapeops.io/v1/browser-headers?api_key=' + SCRAPE_OPS_KEY)
  json_response = response.json()
  return json_response.get('result', [])

def get_random_header(header_list):
  random_index = randint(0, len(header_list) - 1)
  randomHeader = header_list[random_index]
  randomHeader["referer"] = "https://www.bumeran.com.pe/empleos-area-recursos-humanos-y-capacitacion-publicacion-menor-a-7-dias.html"
  randomHeader["x-site-id"] = "BMPE"
  return randomHeader

header_list = get_headers_list()

def get_max_pages():
    proxy_params = {
        'api_key': SCRAPE_OPS_KEY,
        'url': 'https://www.bumeran.com.pe/empleos-area-recursos-humanos-y-capacitacion-publicacion-menor-a-7-dias.html',
        'render_js': True,
    }

    header = get_random_header(header_list)
    header.pop("referer")
    header.pop("x-site-id")

    response = requests.get(
    url='https://proxy.scrapeops.io/v1/',
    params=urlencode(proxy_params),
    timeout=120,
    headers=header)

    page_classes = ["sc-imDdex","sc-ewMkZo"]
    soup = BeautifulSoup(response.content,"html.parser")

    for cl in page_classes:
        res = soup.find_all("a",class_=cl)
        if res:
            num_pages = int(res[-1].text)
            break
    return num_pages

number_pages = get_max_pages()
logging.info(f"Se han procesado {number_pages} páginas.")

avisos = []

for i in range(number_pages):
  url = "https://www.bumeran.com.pe/api/avisos/searchNormalizado"
  querystring = {"pageSize":"20","page":i}
  payload = {
      "filtros": [
          {
              "id": "area",
              "value": "recursos-humanos-y-capacitacion"
          },
          {
            "id": "dias_fecha_publicacion",
            "value": "menor-a-7-dias"
        }
      ],
      "busquedaExtendida": True,
      "tipoDetalle": "full",
      "withHome": False,
      "internacional": False
  }

  response = requests.request("POST", url, json=payload, headers=get_random_header(header_list), params=querystring)

  if response.status_code == 201:  
    data = response.json()["content"]
    avisos += data

logging.info(f"Se han procesado {len(avisos)} avisos.")

df = pd.DataFrame(avisos)
df.to_csv("bumeran_data_pure.csv",index=False,mode="a",header=False)

df = df.drop(columns={"logoURL","salarioMinimo","salarioMaximo","planPublicacion","portal","oportunidad","fechaHoraPublicacion","gptwUrl","latitud","longitud","links"})
df = df.drop_duplicates(subset="id")

def clean_titulo(texto):
    txt = texto.lower()
    translator = str.maketrans(string.punctuation," "*len(string.punctuation))
    txt  =  txt.translate(translator)
    txt = unidecode(txt)
    return txt

def get_cargo(texto):
    cargos = {
        "asistente": ["asistente","asiten","assist"],
        "analista": ["analista","analita","senior"],
        "jefe": ["jefe", "jefa"],
        "supervisor": ["supervisor"],
        "coordinador": ["coordinador"],
        "gerente": ["gerente"],
        "auxiliar": ["auxiliar", "apoyo","colaborador"],
        "practicante":["practicante","pasant"],
        "trabajador social":["social","trabajador"],
        "consultor":["consultor"],
        "especialista":["especialista"],
        "generalista":["generalist"],
        "encargado":["encargad"],
        "reclutador":["reclutad","Recruiter"],
        "business partner":["partner"],
        "trainee" : ["traine"],
        "capacitador":["capacita"]
    }
    cargo = "Otros"
    for k, v in cargos.items():
        for w in v:
            if w in texto:  # Utilizar 'in' para verificar si 'w' está contenido en 'texto'
                cargo = k
                break
    return cargo.capitalize()

df["cargoTrabajo"] = df["titulo"].apply(clean_titulo).apply(get_cargo)

def buscar_area(text):
    areaTrabajoList = {"Planillas":["NOMIN","PLANILL","LIQUID","REMUN","PAYR"],
                    "Talento":["TALENT"],
                    "Administración de Personal":["ADMINISTRAC","ASISTENCIA","TIEMPOS","TAREO"],
                    "Bienestar Social":["BIENEST","SOCIAL"],
                    "Seguridad y Salud":["SEGURIDAD","MEDICO"],
                    "Capacitación":["CAPACITAC","ENTRENAMI","APRENDIZ","CAPACITAD"],
                    "Cultura Organizacional":["CLIMA","CULTUR","EXPERIENCIA"],
                    "Compensaciones":["COMPENSACI"],
                    "Desarrollo":["DESARROLLO"],
                    "Reclutamiento":["RECLU","SELECC","ATRACC","RECRUIT"],
                    "Gestión Humana":["HUMAN","HR","RRHH","R.H","RH","PARTNER"],
                    "Comunicación":["COMUN"],
                    "Relaciones Laborales":["RELACION"]      
    }
    area = "Otros"

    for k,v in areaTrabajoList.items():
        for z in v:
            if z in text.upper():
                area = k
                break
    return area

df["subareaTrabajo"] = df["titulo"].apply(clean_titulo).apply(buscar_area)

def buscar_departamanto(texto):
    lugar = texto.split(",")[-1].strip()
    return lugar

departamentos = {
    "Municipalidad Metropolitana de Lima":"Lima",
    "Perú":"Lima",
    "":"Lima"
}

df["localizacionTrabajo"] = df["localizacion"].apply(buscar_departamanto).replace(departamentos)

def limpiar_detalle(texto):

    #eliminar HTML
    patron_entidades_html = r'&[#a-zA-Z0-9]+;'
    texto = re.sub(patron_entidades_html, '', texto)

    #reemplazar signos de puntuacion
    puntuacion_a_reemplazar = string.punctuation + '¡¿•·–'
    tabla = str.maketrans(puntuacion_a_reemplazar, ' ' * len(puntuacion_a_reemplazar))
    texto = texto.translate(tabla)
        
    return texto.strip()

nlp = spacy.load("es_core_news_sm")
# Add special case rule
powerbi_case = [{ORTH: "power bi"}]
nlp.tokenizer.add_special_case("power bi", powerbi_case)
powerpoint_case = [{ORTH: "power point"}]
nlp.tokenizer.add_special_case("power point",powerpoint_case)

keywords_idiomas = ["inglés","portugués","francés","italiano"]
keywords_programas = ["excel","word","turecibo","plame","afp","adobe","power bi","power point","sql","python","r"]
keywords_conocimientos = ["essalud","indicadores","onp","eps","subsidios","cuentas","kpi","power bi","power point","cts","gratificaciones","utilidades","vacaciones","tareo","asistencia","tiempos","contratos","auditoría","sunafil","sindicato"]
keywords_erp = ["sap","ofisis","ofiplan","spring","buk","ssff","starsoft","erp"]
keywords_carreras = ["psicología","derecho","administración","contabilidad","economía","ingeniería",]

df["detalle_2"] = df["detalle"].apply(limpiar_detalle)

keywords = keywords_idiomas + keywords_erp + keywords_carreras + keywords_programas + keywords_conocimientos

def procesar_fila(row):
    detalle = row.detalle_2.lower().strip()
    doc = nlp(detalle)
    tokens = [token.text for token in doc]
    tokens = list(set(tokens))

    keywords_replace = {
        "powerbi": "power bi",
        "powerpoint": "power point",
        "sindical": "sindicato"
    }

    for k, v in keywords_replace.items():
        tokens = [d.replace(k, v) for d in tokens]

    tokens = [word for word in tokens if word in keywords]
    return tokens

df["skill_keywords"] = df.apply(procesar_fila, axis=1)

rename_columns = {
    "titulo":"tituloTrabajo",
}

df = df.rename(columns=rename_columns)
df = df.drop("detalle_2",axis=1)
df["aptoDiscapacitado"] = df["aptoDiscapacitado"].replace({False:"No",True:"Si"})
df["confidencial"] = df["aptoDiscapacitado"].replace({False:"No",True:"Si"})
df['skill_keywords'] = df['skill_keywords'].apply(lambda lista: bytes(str(lista), 'utf-8'))

initial_df = pd.read_csv("data_bumeran.csv")
ids = list(initial_df["id"])

final_df = df[~df["id"].isin(ids)]

if len(final_df) > 0:
    final_df.to_csv("data_bumeran.csv",index=False,mode="a",header=False)

logging.info(f"Se han agregado {len(final_df)} a la base de datos.")