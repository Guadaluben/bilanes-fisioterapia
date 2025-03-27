import streamlit as st
import pyrebase
import datetime
import tempfile

# Configuración de Firebase
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

# Subida de prescripción
uploaded_file = st.file_uploader("Sube la prescripción (imagen o PDF)", type=["jpg", "png", "pdf"])

# Información adicional
info_adicional = st.text_area("Información adicional sobre el paciente", height=150)

# Datos del paciente
nombre = st.text_input("Nombre completo del paciente")
fecha_prescripcion = st.date_input("Fecha de la prescripción", value=datetime.date.today())

# Generar informe
if st.button("Generar Informe"):
    if uploaded_file is not None and nombre:
        informe_generado = f"""
Informe Fisioterapéutico

Paciente: {nombre}  
Fecha de la prescripción: {fecha_prescripcion.strftime('%d/%m/%Y')}  
Nombre del archivo original: {uploaded_file.name}  
Información adicional: {info_adicional}  

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

        fecha_str = fecha_prescripcion.strftime("%Y-%m-%d")
        nombre_archivo = f"{nombre.replace(' ', '_')}_{fecha_str}.txt"
        ruta_en_storage = f"informes/{nombre_archivo}"
        storage.child(ruta_en_storage).put(temp_path)
        url = storage.child(ruta_en_storage).get_url(None)

        st.success("Informe generado y subido correctamente a Firebase Storage.")
        st.markdown(f"[Ver o descargar el informe]({url})")
    else:
        st.error("Por favor, completa todos los campos y sube una prescripción.")
