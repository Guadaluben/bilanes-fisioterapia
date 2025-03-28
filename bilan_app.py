import streamlit as st
import requests
import tempfile
import pyrebase
import datetime
import re

# -------------------------
# CONFIGURACIÓN DE FIREBASE
# -------------------------
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

# -------------------------
# CONFIGURACIÓN DE LA APP
# -------------------------
st.set_page_config(page_title="BilanKineIA", layout="centered")
st.title("BilanKineIA")

OCR_SPACE_API_KEY = "helloworld"  # Reemplaza por tu clave real si la recibes

# -------------------------
# FUNCIONES OCR
# -------------------------
def extraer_texto_con_ocr_space(uploaded_file):
    url = "https://api.ocr.space/parse/image"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    with open(temp_file_path, 'rb') as f:
        response = requests.post(
            url,
            files={"file": f},
            data={"apikey": OCR_SPACE_API_KEY, "language": "spa", "isOverlayRequired": False}
        )

    result = response.json()
    texto = result['ParsedResults'][0]['ParsedText'] if 'ParsedResults' in result else ""
    return texto

def extraer_nombre_y_fecha(texto):
    # Buscar fecha tipo 12/03/2025
    fechas = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", texto)
    fecha = fechas[0] if fechas else ""

    # Buscar nombre
    nombre = ""
    for linea in texto.split("\n"):
        if any(palabra in linea.lower() for palabra in ["nombre", "nom", "paciente", "sr", "sra", "mme", "m."]):
            palabras = linea.strip().split()
            candidatos = [p for p in palabras if p.istitle()]
            if len(candidatos) >= 2:
                nombre = " ".join(candidatos[:3])
                break
    return nombre.strip(), fecha.strip()

# -------------------------
# SUBIR PRESCRIPCIÓN
# -------------------------
uploaded_file = st.file_uploader("📤 Sube la prescripción (PDF o imagen)", type=["pdf", "png", "jpg", "jpeg"])

nombre_detectado, fecha_detectada = "", ""

if uploaded_file:
    texto_extraido = extraer_texto_con_ocr_space(uploaded_file)
    nombre_detectado, fecha_detectada = extraer_nombre_y_fecha(texto_extraido)

# -------------------------
# CAMPOS DEL PACIENTE
# -------------------------
nombre = st.text_input("Nombre completo del paciente", value=nombre_detectado)
fecha_str = st.text_input("Fecha de la prescripción (DD/MM/AAAA)", value=fecha_detectada)
try:
    fecha_prescripcion = datetime.datetime.strptime(fecha_str, "%d/%m/%Y").date()
except:
    fecha_prescripcion = datetime.date.today()

mostrar_info = st.checkbox("Añadir información adicional")
info_adicional = st.text_area("Información adicional sobre el paciente", height=150) if mostrar_info else ""

# -------------------------
# GENERAR INFORME
# -------------------------
if st.button("Generar Informe"):
    if uploaded_file and nombre:
        informe = f"""
Informe Fisioterapéutico

Paciente: {nombre}
Fecha de la prescripción: {fecha_prescripcion.strftime('%d/%m/%Y')}
Nombre del archivo original: {uploaded_file.name}
Información adicional: {info_adicional if info_adicional else 'No especificada'}

---

Evaluación:
- Se observa indicación de fisioterapia con ejercicios y terapia manual.
- Se recomienda fortalecimiento del manguito rotador y estabilización articular.

---

Tratamiento Propuesto

1. Ejercicios (20 minutos)
- Bicicleta estática, elásticos progresivos, balones suizos, luces de reacción.

2. Terapia Manual (20 minutos)
- Masaje, estiramientos postisométricos, movilización neural.

3. Aparatología (20 minutos)
- TENS + infrarrojos o presoterapia (según el caso).

---

Informe generado automáticamente por BilanKineIA.
"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(informe.encode("utf-8"))
            temp_path = temp_file.name

        fecha_archivo = fecha_prescripcion.strftime("%Y-%m-%d")
        nombre_archivo = f"{nombre.replace(' ', '_')}_{fecha_archivo}.txt"
        ruta_storage = f"informes/{nombre_archivo}"
        storage.child(ruta_storage).put(temp_path)
        url = storage.child(ruta_storage).get_url(None)

        st.success("✅ Informe generado correctamente")
        st.markdown(f"📎 [Descargar informe]({url})")
    else:
        st.warning("⚠️ Por favor, completa el nombre del paciente y sube la prescripción.")
