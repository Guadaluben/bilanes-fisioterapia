import streamlit as st
import datetime
import tempfile
import requests
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import re
import pyrebase
from fpdf import FPDF

# ------------------------
# CONFIGURACIÓN DE FIREBASE
# ------------------------
firebaseConfig = {
  "apiKey": "AIzaSyB9iQ0voXbSlY2BXtUaERzIRE4uXLA1zJ0",
  "authDomain": "bilankineia-7a2a8.firebaseapp.com",
  "projectId": "bilankineia-7a2a8",
  "storageBucket": "bilankineia-7a2a8.appspot.com",
  "messagingSenderId": "980038899896",
  "appId": "1:980038899896:web:1d53c3fe1318afee243c4d",
  "measurementId": "G-T9ZPLYCXBN"
}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

# ------------------------
# CONFIGURACIÓN DE LA APP
# ------------------------
st.set_page_config(page_title="BilanKineIA", layout="centered")
st.title("BilanKineIA")

# ------------------------
# FUNCIONES ÚTILES
# ------------------------
def extraer_texto_con_ocr_space(file_bytes):
    OCR_SPACE_API_KEY = "helloworld"  # Gratuito sin clave
    url_api = "https://api.ocr.space/parse/image"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(file_bytes)
        temp_path = temp.name

    with open(temp_path, 'rb') as f:
        r = requests.post(
            url_api,
            files={"file": f},
            data={"apikey": OCR_SPACE_API_KEY, "language": "spa"}
        )
    resultado = r.json()
    return resultado["ParsedResults"][0]["ParsedText"] if "ParsedResults" in resultado else ""

def extraer_nombre_y_fecha(texto):
    # Soporta nombres con caracteres acentuados y eÑes
    patron_nombre = r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\b"
    posibles_nombres = re.findall(patron_nombre, texto, flags=re.UNICODE)
    posibles_fechas = re.findall(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", texto)
    
    nombre = posibles_nombres[0] if posibles_nombres else ""
    fecha_str = posibles_fechas[0] if posibles_fechas else ""
    return nombre, fecha_str

def generar_pdf(nombre, fecha, informe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Nombre: {nombre}\nFecha: {fecha}\n\n{informe}")
    
    ruta_pdf = f"{nombre.replace(' ', '_')}_{fecha.replace('/', '-')}.pdf"
    pdf.output(ruta_pdf)
    return ruta_pdf

# ------------------------
# SUBIDA DE PRESCRIPCIÓN
# ------------------------
archivo_subido = st.file_uploader("📤 Sube la prescripción (PDF o imagen)", type=["pdf", "png", "jpg", "jpeg"])

nombre = ""
fecha_prescripcion = ""

if archivo_subido:
    texto_extraido = extraer_texto_con_ocr_space(archivo_subido.read())
    nombre, fecha_prescripcion = extraer_nombre_y_fecha(texto_extraido)

    nombre = st.text_input("Nombre completo del paciente", value=nombre)
    fecha_prescripcion = st.text_input("Fecha de la prescripción (DD/MM/AAAA)", value=fecha_prescripcion)

# ------------------------
# INFORMACIÓN ADICIONAL
# ------------------------
mostrar_info = st.checkbox("➕ Añadir información adicional")
info_adicional = ""
if mostrar_info:
    info_adicional = st.text_area("Información adicional sobre el paciente", height=150)

# ------------------------
# GENERAR INFORME
# ------------------------
if st.button("Generar Informe") and archivo_subido and nombre and fecha_prescripcion:
    # Generar informe
    informe = f"""
    **Informe Fisioterapéutico**
    **Paciente:** {nombre}
    **Fecha:** {fecha_prescripcion}
    **Información adicional:** {info_adicional or 'Ninguna'}

    **Evaluación:**
    - El paciente presenta indicación de fisioterapia.
    - Se recomienda iniciar tratamiento con ejercicios terapéuticos, terapia manual y aparatología.

    **Tratamiento Propuesto:**
    1. Ejercicios: trabajo de movilidad, fuerza y coordinación (20 minutos).
    2. Terapia manual: masaje terapéutico, estiramientos y movilizaciones (20 minutos).
    3. Aparatología: TENS, ultrasonidos o presoterapia (20 minutos).
    """

    st.markdown(informe)

    # Generar PDF
    pdf_path = generar_pdf(nombre, fecha_prescripcion, informe)

    # Subir a Firebase
    ruta_storage = f"informes/{nombre.replace(' ', '_')}_{fecha_prescripcion.replace('/', '-')}.pdf"
    storage.child(ruta_storage).put(pdf_path)
    st.success("Informe generado y subido correctamente a Firebase.")
