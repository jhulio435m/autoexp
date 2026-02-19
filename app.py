import streamlit as st
import json
import os
import subprocess
import pandas as pd

# Detectar la ruta base de forma dinámica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECTORS_DIR = os.path.join(BASE_DIR, "data", "sectors")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CORE_DIR = os.path.join(BASE_DIR, "core")

if not os.path.exists(OUTPUT_DIR): 
    os.makedirs(OUTPUT_DIR)

st.set_page_config(page_title="Generador Expedientes", layout="wide")

st.title("🏗️ Generador de Expedientes Técnicos")

# Sidebar - Listar sectores
if not os.path.exists(SECTORS_DIR):
    st.error(f"Error: No se encuentra la carpeta de sectores en {SECTORS_DIR}")
    st.stop()

archivos = sorted([f for f in os.listdir(SECTORS_DIR) if f.endswith('.json')])
if not archivos:
    st.warning("No se encontraron archivos JSON en la carpeta de sectores.")
    st.stop()

sector_file = st.sidebar.selectbox("Seleccione el Sector", archivos)

# Carga de datos
with open(os.path.join(SECTORS_DIR, sector_file), 'r', encoding='utf-8') as f:
    data = json.load(f)

# Formulario Simple
tabs = st.tabs(["📋 Datos Generales", "📑 Checklist de Documentos", "🚀 Generar PDF"])

with tabs[0]:
    st.header("1. Información del Proyecto")
    entidad = st.text_input("Entidad Convocante", "PROVIAS NACIONAL")
    proyecto = st.text_area("Nombre del Proyecto", "MEJORAMIENTO DEL CAMINO VECINAL...")
    cui = st.text_input("CUI (Código Unificado)", "0000000")
    ubicacion = st.text_input("Ubicación (Distrito - Provincia - Región)", "DISTRITO - PROVINCIA - REGION")
    consultor = st.text_input("Consultor / Consorcio", "CONSULTOR S.A.C.")

with tabs[1]:
    st.header("2. Checklist de Documentos Requeridos")
    st.write("Marque los documentos que desea incluir en el expediente:")
    seleccionados = []
    
    # Manejar estructura de grupos del JSON limpio
    grupos = data.get('grupos', [])
    if grupos:
        for g_idx, g in enumerate(grupos):
            with st.expander(f"Grupo {g['letra']}: {g['nombre']}"):
                for i_idx, item in enumerate(g['items']):
                    # Crear una clave única usando índices de grupo e item
                    unique_key = f"chk_{g_idx}_{i_idx}_{sector_file}"
                    label = f"{item['id']}. {item['nombre']}" if item['id'] else item['nombre']
                    if st.checkbox(label, key=unique_key):
                        seleccionados.append(item)
    else:
        # Fallback si el JSON no está procesado por grupos
        documentos_raw = data.get('documentos', [])
        for idx, doc in enumerate(documentos_raw):
            if isinstance(doc, list) and len(doc) > 1:
                unique_key = f"chk_raw_{idx}_{sector_file}"
                if st.checkbox(doc[1], key=unique_key):
                    seleccionados.append({"nombre": doc[1], "normativa": doc[2] if len(doc) > 2 else ""})

with tabs[2]:
    st.header("3. Finalizar y Compilar")
    if st.button("🔥 GENERAR EXPEDIENTE EN PDF"):
        if not seleccionados:
            st.warning("Por favor, seleccione al menos un documento del checklist.")
        else:
            with st.spinner("Compilando LaTeX dentro del contenedor..."):
                # Generación de LaTeX
                cls_path = os.path.join(CORE_DIR, "expediente")
                
                tex_content = [
                    r"\documentclass{" + cls_path + "}",
                    r"\entidad{" + entidad + "}",
                    r"\nombreproyecto{" + proyecto + "}",
                    r"\ubicacion{" + ubicacion + "}",
                    r"\cui{" + cui + "}",
                    r"\volumen{VOLUMEN III: MEMORIA DESCRIPTIVA}",
                    r"\consultor{" + consultor + "}",
                    r"\begin{document}",
                    r"\hacerportada",
                    r"\tableofcontents\newpage",
                    r"\section{BASES LEGALES Y NORMATIVAS}",
                    r"Para el presente proyecto se ha considerado la siguiente normativa sectorial:",
                    r"\begin{enumerate}"
                ]
                
                for doc in seleccionados:
                    nombre = doc.get('nombre', 'Documento')
                    norma = doc.get('normativa', 'Norma Técnica')
                    if not norma: norma = "Según TDR del Proyecto"
                    
                    # Limpiar caracteres especiales para LaTeX
                    nombre_esc = nombre.replace('&', r'\&').replace('_', r'\_').replace('%', r'\%').replace('#', r'\#')
                    norma_esc = norma.replace('&', r'\&').replace('_', r'\_').replace('%', r'\%').replace('#', r'\#')
                    
                    tex_content.append(r"\item \textbf{" + nombre_esc + "}: " + norma_esc)
                
                tex_content.append(r"\end{enumerate}")
                tex_content.append(r"\section{DESCRIPCIÓN TÉCNICA}")
                tex_content.append(r"El desarrollo de la ingeniería se ajusta a los estándares establecidos.")
                tex_content.append(r"\end{document}")
                
                tex_path = os.path.join(OUTPUT_DIR, "expediente_final.tex")
                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(tex_content))
                
                # Compilar usando el pdflatex del contenedor
                try:
                    cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={OUTPUT_DIR}", tex_path]
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=OUTPUT_DIR)
                    # Correr dos veces para el índice
                    subprocess.run(cmd, capture_output=True, text=True, cwd=OUTPUT_DIR)
                    
                    pdf_path = os.path.join(OUTPUT_DIR, "expediente_final.pdf")
                    if os.path.exists(pdf_path):
                        st.success("✅ ¡Expediente generado con éxito!")
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Descargar PDF",
                                data=f,
                                file_name=f"Expediente_{cui}.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.error("Error en la compilación de LaTeX.")
                        st.text_area("Log de Error:", result.stdout)
                except Exception as e:
                    st.error(f"Error de sistema: {e}")
