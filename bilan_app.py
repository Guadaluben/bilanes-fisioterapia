import streamlit as st
import pyrebase
import datetime
import tempfile
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import re

# Configuración Firebase
firebaseConfig = {
    "apiKey": "TU_API_KEY",
    "authDomain": "TU_PROYECTO.firebaseapp.com",
    "projectId": "TU_PROYECTO",
    "storageBucket": "TU_PROYECTO.appspot.com",
    "messagingSenderId": "1234567890",
    "appId": "1:1234567890:web:abcdef123456",
    "databaseURL": ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

# Configuración de la app
st.set_page_config(page_title="BilanKineIA", layout="centered")
st.title("BilanKineIA")

# --- OCR desde imagen o PDF ---
def obtener_texto_desde_archivo(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=200)
        imagen = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    else:
        imagen = Image.open(uploaded_file)

    texto = pytesseract.image_to_string(imagen)
    return texto

def extraer_nombre_y_fecha(texto):
    # Buscar fecha en formato DD/MM/YYYY o similar
    fechas = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", texto)
    fecha_detectada = fechas[0] if fechas else ""

    # Buscar líneas con posibles nombres
    nombre_detectado = ""
    for linea in texto.split("\n"):
        if any(kw in linea.lower() for kw in ["paciente", "nom", "nombre", "sr", "sra", "mme", "m."]):
            palabras = linea.strip().split()
            candidatos = [p for p in palabras if p.istitle()]
            if len(candidatos) >= 2:
                nombre_detectado = " ".join(candidatos[:3])
                break

    return nombre_detectado.strip(), fecha_detectada.strip()

# Subida del archivo
uploaded_file = st.file_uploader("Sube la prescripción (imagen o PDF)", type=["jpg", "png", "pdf"])

nombre_detectado, fecha_detectada = "", ""

if uploaded_file:
    texto_extraido = obtener_texto_desde_archivo(uploaded_file)
    nombre_detectado, fecha_detectada = extraer_nombre_y_fecha(texto_extraido)

# Formulario del paciente
nombre = st.text_input("Nombre completo del paciente", value=nombre_detectado)
fecha_str = st.text_input("Fecha de la prescripción (DD/MM/AAAA)", value=fecha_detectada)
try:
    fecha_prescripcion = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
except:
    fecha_prescripcion = datetime.date.today()

# Información adicional opcional
mostrar_info = st.checkbox("Añadir información adicional")
info_adicional = st.text_area("Información adicional sobre el paciente", height=150) if mostrar_info else ""

# Generar informe
if st.button("Generar Informe"):
    if uploaded_file and nombre:
        informe_generado = f"""
Informe Fisioterapéutico

Paciente: {nombre}
Fecha de la prescripción: {fecha_prescripcion.strftime('%d/%m/%Y')}
Nombre del archivo original: {uploaded_file.name}
Información adicional: {info_adicional if info_adicional else 'No especificada'}

---

Evaluación:
- Se observa indicación de fisioterapia con ejercicios y terapia manual.
- Se recomienda fortalecimiento, control motor y tratamiento complementario.

---

Tratamiento Propuesto

1. Ejercicios (20 minutos)
- Bandas elásticas, pesas progresivas.
- Bicicleta estática y balón suizo.

2. Terapia Manual (20 minutos)
- Masaje descontracturante.
- Estiramientos postisométricos.

3. Aparatología (20 minutos)
- TENS y ultrasonidos.

---

Informe generado automáticamente para revisión profesional.
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(informe_generado.encode("utf-8"))
            temp_path = temp_file.name

        fecha_archivo = fecha_prescripcion.strftime("%Y-%m-%d")
        nombre_archivo = f"{nombre.replace(' ', '_')}_{fecha_archivo}.txt"
        ruta_en_storage = f"informes/{nombre_archivo}"
        storage.child(ruta_en_storage).put(temp_path)
        url = storage.child(ruta_en_storage).get_url(None)

        st.success("Informe generado y subido correctamente.")
        st.markdown(f"[Ver o descargar el informe]({url})")
    else:
        st.error("Por favor, completa el nombre y sube una prescripción.")
