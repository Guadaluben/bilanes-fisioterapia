import streamlit as st
import pyrebase
import datetime
import tempfile
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes

# --- CONFIGURACIÓN FIREBASE ---
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

# --- CONFIGURACIÓN APP ---
st.set_page_config(page_title="BilanKineIA", layout="centered")
st.title("BilanKineIA")

# --- CARGA DE PRESCRIPCIÓN ---
uploaded_file = st.file_uploader("Sube la prescripción médica (imagen o PDF)", type=["jpg", "jpeg", "png", "pdf"])

# --- EXTRACCIÓN AUTOMÁTICA (OCR) ---
nombre_detectado = ""
fecha_detectada = None

def detectar_texto(img):
    return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

def extraer_datos(text_data):
    posibles_nombres = []
    posible_fecha = None

    for i, palabra in enumerate(text_data["text"]):
        if palabra.strip() == "":
            continue

        x = text_data["left"][i]
        y = text_data["top"][i]
        texto = palabra.strip()

        # Detección de nombres (evita "Dr.", "Dra.", etc.)
        if texto.istitle() and not any(prefix in texto for prefix in ["Dr", "Dra", "Docteur", "Dr."]):
            posibles_nombres.append((texto, x, y))

        # Detección de fecha con patrón DD/MM/AAAA o similar
        if "/" in texto and len(texto) >= 8:
            posible_fecha = texto

    # Selección del nombre más a la derecha y arriba (zona paciente)
    if posibles_nombres:
        ordenados = sorted(posibles_nombres, key=lambda t: (t[2], -t[1]))  # prioriza arriba derecha
        if len(ordenados) >= 2:
            nombre_detectado = f"{ordenados[0][0]} {ordenados[1][0]}"
        else:
            nombre_detectado = ordenados[0][0]
    else:
        nombre_detectado = ""

    return nombre_detectado, posible_fecha

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pages = convert_from_bytes(uploaded_file.read(), dpi=300)
        image = pages[0]  # Usamos solo la primera página
    else:
        image = Image.open(uploaded_file)

    texto_detectado = detectar_texto(image)
    nombre_detectado, fecha_detectada = extraer_datos(texto_detectado)

# --- CAMPOS EDITABLES ---
nombre_paciente = st.text_input("Nombre completo del paciente", value=nombre_detectado)
fecha_por_defecto = datetime.date.today()
if fecha_detectada:
    try:
        fecha_por_defecto = datetime.datetime.strptime(fecha_detectada, "%d/%m/%Y").date()
    except:
        pass
fecha_prescripcion = st.date_input("Fecha de la prescripción", value=fecha_por_defecto)

# --- INFORMACIÓN ADICIONAL (opcional) ---
info_adicional = st.text_area("Información adicional (opcional)", height=150)

# --- BOTÓN PARA GENERAR INFORME ---
if st.button("Generar Informe"):
    if uploaded_file and nombre_paciente:
        informe_generado = f"""
Informe Fisioterapéutico

Paciente: {nombre_paciente}  
Fecha de prescripción: {fecha_prescripcion.strftime('%d/%m/%Y')}  
Archivo original: {uploaded_file.name}  
Información adicional: {info_adicional}

---

Evaluación:
- Se observa indicación de fisioterapia con ejercicios y terapia manual.
- Recomendado fortalecer musculatura, estabilizar articulaciones y aliviar dolor.

---

Tratamiento Propuesto:

1. Ejercicios (20 minutos)
- Bandas elásticas, pesas, bici estática, balón suizo.

2. Terapia Manual (20 minutos)
- Estiramientos pasivos y postisométricos, masaje descontracturante.

3. Aparatología (20 minutos)
- TENS, ultrasonidos, infrarrojos si fuera necesario.

---

Informe generado automáticamente para revisión profesional.
"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(informe_generado.encode("utf-8"))
            temp_path = temp_file.name

        fecha_str = fecha_prescripcion.strftime("%Y-%m-%d")
        nombre_archivo = f"{nombre_paciente.replace(' ', '_')}_{fecha_str}.txt"
        ruta_en_storage = f"informes/{nombre_archivo}"
        storage.child(ruta_en_storage).put(temp_path)
        url = storage.child(ruta_en_storage).get_url(None)

        st.success("Informe generado y subido correctamente.")
        st.markdown(f"[Ver o descargar informe]({url})")
    else:
        st.warning("Por favor, sube una prescripción y asegúrate de completar el nombre del paciente.")
