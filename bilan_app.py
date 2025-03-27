import streamlit as st
import pyrebase  # 👈 AÑADE ESTA LÍNEA

# 🔐 Conexión a Firebase
firebaseConfig = {
    "apiKey": "TU_API_KEY",
    "authDomain": "tu-proyecto.firebaseapp.com",
    "projectId": "tu-proyecto",
    "storageBucket": "tu-proyecto.appspot.com",
    "messagingSenderId": "1234567890",
    "appId": "1:1234567890:web:abcdef123456",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

# Configuración de la aplicación
st.set_page_config(page_title="Bilan de Fisioterapia", layout="centered")

# Título de la aplicación
st.title("📄 Bilan de Fisioterapia")

# Subir la prescripción
uploaded_file = st.file_uploader("📤 Sube la prescripción en imagen o PDF", type=["jpg", "png", "pdf"])

# Campo de texto para información extra
info_adicional = st.text_area("📝 Información adicional sobre el paciente", height=150)

# Botón para generar el informe
if st.button("📑 Generar Informe"):
    import tempfile  # Asegúrate de importar esto al inicio del archivo si no está

# Guardar el informe en un archivo temporal
with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
    temp_file.write(informe_generado.encode("utf-8"))
    temp_path = temp_file.name

# Crear el nombre del archivo en Firebase Storage
from datetime import date
fecha_actual = date.today().strftime("%Y-%m-%d")
nombre_archivo = f"{uploaded_file.name.replace(' ', '_')}_{fecha_actual}.txt"
ruta_en_storage = f"informes/{nombre_archivo}"

# Subir a Firebase Storage
storage.child(ruta_en_storage).put(temp_path)

# Obtener la URL pública del archivo
url = storage.child(ruta_en_storage).get_url(None)

# Mostrar el enlace en la app
st.success("✅ Informe subido a Firebase Storage correctamente.")
st.markdown(f"[📄 Haz clic aquí para ver o descargar el informe]({url})")

    if uploaded_file is not None:
        # Simulación de un informe generado por la API de OpenAI
        informe_generado = f"""
        **📋 Informe Fisioterapéutico**  
        **📌 Prescripción:** {uploaded_file.name}  
        **🖊 Información adicional:** {info_adicional}  

        **🔍 Evaluación:**  
        - Se observa indicación de fisioterapia con ejercicios y terapia manual.  
        - Se recomienda fortalecimiento del manguito rotador y estabilización articular.  

        **💪 Tratamiento Propuesto:**  
        1️⃣ **Ejercicios:** Fortalecimiento con bandas elásticas y pesos progresivos.  
        2️⃣ **Terapia Manual:** Movilización articular y estiramientos postisométricos.  
        3️⃣ **Aparatología:** Aplicación de TENS y ultrasonidos.  
        """

        # Mostrar el informe generado
        st.success("✅ Informe generado con éxito:")
        st.text_area("📄 Resultado del informe:", informe_generado, height=300)

    else:
        st.error("❌ Por favor, sube una prescripción antes de generar el informe.")
