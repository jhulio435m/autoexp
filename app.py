import streamlit as st
import db_manager as db
import ui_manager as ui
import os
import base64
from core.pdf_generator import generar_codigo_latex, compilar_latex
from utils.ubigeo import UBIGEO_DATA

db.init_db()

st.set_page_config(page_title="Expedientes Técnicos", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    .main .block-container { max-width: 100% !important; padding: 0rem 3rem 1rem 3rem !important; margin-top: -5rem !important; }
    footer { visibility: hidden; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.6; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; margin-bottom: 1rem; }
    .stTabs [data-baseweb="tab"] { padding: 0 24px; height: 48px; font-size: 1.0rem; font-weight: 600; color: #64748B; }
    div[data-testid="stVerticalBlock"] > div[style*="border"] { padding: 2.0rem !important; border: 1px solid #E2E8F0 !important; background-color: #FFFFFF !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important; }
    label { font-size: 0.9rem !important; margin-bottom: 0.4rem !important; font-weight: 700 !important; color: #1E293B !important; text-transform: uppercase; letter-spacing: 0.025em; }
    .stTextInput input, .stSelectbox div[role="button"], .stNumberInput input { height: 44px !important; font-size: 1.05rem !important; }
    .stTextArea textarea { font-size: 1.05rem !important; }
    </style>
    """, unsafe_allow_html=True)

if 'proyecto_id' not in st.session_state: st.session_state.proyecto_id = None
if st.session_state.proyecto_id is None: ui.screen_seleccion_proyecto(); st.stop()

p_actual = db.obtener_proyecto_por_id(st.session_state.proyecto_id)
if not p_actual: st.session_state.proyecto_id = None; st.rerun()

ui.sidebar_manager(p_actual)

tabs = st.tabs(["INFORMACIÓN DEL PROYECTO", "ESTRUCTURA TÉCNICA", "EDITOR LATEX (OVERLEAF)"])

with tabs[0]:
    with st.container(border=True):
        st.markdown("**CLASIFICACIÓN Y DATOS GENERALES**")
        c_sec, c_are, c_ent, c_cui = st.columns([0.25, 0.25, 0.3, 0.2])
        sectores = db.obtener_sectores()
        ids_sectores = [s['id'] for s in sectores]
        idx_sec = ids_sectores.index(p_actual['sector_id']) if p_actual['sector_id'] in ids_sectores else 0
        sec_edit = c_sec.selectbox("Sector", range(len(sectores)), index=idx_sec, format_func=lambda i: sectores[i]['nombre'].upper(), key="edit_sec")
        areas = db.obtener_areas_por_sector(sectores[sec_edit]['id'])
        ids_areas = [a['id'] for a in areas]
        idx_are = ids_areas.index(p_actual['area_id']) if p_actual['area_id'] in ids_areas else 0
        are_edit = c_are.selectbox("Área", range(len(areas)), index=idx_are, format_func=lambda i: areas[i]['nombre'].upper(), key="edit_are")

        entidad_edit = c_ent.text_input("Entidad", p_actual['entidad'], key="edit_entidad")
        cui_edit = c_cui.text_input("CUI", p_actual['cui'], key="edit_cui")
        nombre_edit = st.text_area("Nombre del Proyecto", p_actual['nombre'], height=80, key="edit_nombre")

        st.markdown("**UBICACIÓN**")
        u1, u2, u3, u4 = st.columns([0.2, 0.2, 0.2, 0.4])
        deps = sorted(list(UBIGEO_DATA.keys()))
        idx_dep = deps.index(p_actual['departamento']) if p_actual['departamento'] in deps else 0
        dep_edit = u1.selectbox("Departamento", deps, index=idx_dep, key="edit_dep")
        provs = sorted(list(UBIGEO_DATA[dep_edit].keys()))
        idx_pro = provs.index(p_actual['provincia']) if p_actual['provincia'] in provs else 0
        pro_edit = u2.selectbox("Provincia", provs, index=idx_pro, key="edit_pro")
        dists = sorted(UBIGEO_DATA[dep_edit][pro_edit])
        idx_dis = dists.index(p_actual['distrito']) if p_actual['distrito'] in dists else 0
        dis_edit = u3.selectbox("Distrito", dists, index=idx_dis, key="edit_dis")
        loc_edit = u4.text_input("Localidad / Sector", p_actual['localidad'], key="edit_loc")

        st.markdown("**RESPONSABLE Y PARÁMETROS TÉCNICOS**")
        p1, p2, p3, p4, p5 = st.columns([0.25, 0.15, 0.2, 0.2, 0.2])
        jefe_edit = p1.text_input("Jefe de Proyecto", p_actual['jefe_proyecto'], key="edit_jefe")
        cip_edit = p2.text_input("CIP", p_actual['cip_jefe'], key="edit_cip")
        monto_edit = p3.number_input("Monto (S/.)", value=float(p_actual['monto'] or 0), format="%.2f", key="edit_monto")
        plazo_edit = p4.number_input("Plazo (Días)", value=int(p_actual['plazo'] or 0), key="edit_plazo")
        mods = ["CONTRATA", "ADMINISTRACIÓN DIRECTA", "OBRAS POR IMPUESTOS"]
        mod_edit = p5.selectbox("Modalidad", mods, index=mods.index(p_actual['modalidad']) if p_actual['modalidad'] in mods else 0, key="edit_mod")

        st.markdown("**SISTEMA Y GEOREFERENCIACIÓN**")
        z1, z2, z3, z4 = st.columns([0.2, 0.2, 0.3, 0.3])
        sists = ["SUMA ALZADA", "PRECIOS UNITARIOS", "MIXTO"]
        sis_edit = z1.selectbox("Sistema", sists, index=sists.index(p_actual['sistema_contratacion']) if p_actual['sistema_contratacion'] in sists else 0, key="edit_sis")
        zona_edit = z2.selectbox("Zona UTM", ["17S", "18S", "19S"], index=["17S", "18S", "19S"].index(p_actual['zona_utm']) if p_actual['zona_utm'] in ["17S", "18S", "19S"] else 0, key="edit_zona")
        este_edit = z3.number_input("Este (X)", value=float(p_actual['este_utm'] or 0), format="%.2f", key="edit_este")
        norte_edit = z4.number_input("Norte (Y)", value=float(p_actual['norte_utm'] or 0), format="%.2f", key="edit_norte")

        if st.button("Guardar cambios", use_container_width=True):
            db.actualizar_proyecto(p_actual['id'], entidad_edit, nombre_edit, cui_edit, dep_edit, pro_edit, dis_edit, loc_edit, p_actual['consultor'], jefe_edit, cip_edit, monto_edit, plazo_edit, mod_edit, sis_edit, p_actual['tipo_intervencion'], p_actual['beneficiarios'], zona_edit, este_edit, norte_edit, areas[are_edit]['id'])
            st.success("Cambios guardados.")
            st.rerun()

with tabs[1]:
    st.markdown("**REQUISITOS DEL EXPEDIENTE**")
    grupos = db.obtener_requisitos_por_area(p_actual['area_id'])
    ids_sel = db.obtener_selecciones(p_actual['id'])
    
    # Nueva distribución: 2/3 para Estudios (A) y 1/3 para Generales (B)
    c_izq, c_der = st.columns([2, 1])
    items_finales = []
    
    for g in grupos:
        if g['letra'] == 'A':
            with c_izq.expander(f"{g['letra']} - {g['nombre']}", expanded=True):
                # Dividir ítems de Estudios en dos sub-columnas internas
                sub1, sub2 = st.columns(2)
                items_g = g['items']
                mid = (len(items_g) + 1) // 2
                for idx, item in enumerate(items_g):
                    target_sub = sub1 if idx < mid else sub2
                    label = f"{item['codigo']} | {item['nombre']}"
                    if target_sub.checkbox(label, value=(item['id'] in ids_sel), key=f"chk_{item['id']}"):
                        items_finales.append(item)
        else:
            with c_der.expander(f"{g['letra']} - {g['nombre']}", expanded=True):
                for item in g['items']:
                    label = f"{item['codigo']} | {item['nombre']}"
                    if st.checkbox(label, value=(item['id'] in ids_sel), key=f"chk_{item['id']}"):
                        items_finales.append(item)

    if st.button("Guardar checklist", use_container_width=True):
        db.guardar_selecciones(p_actual['id'], [i['id'] for i in items_finales])
        st.success("Checklist actualizado.")

with tabs[2]:
    st.markdown("**EDITOR DE DOCUMENTO EN TIEMPO REAL (ESTILO OVERLEAF)**")
    
    # 1. Preparar datos para el PDF
    actuales = db.obtener_selecciones(p_actual['id'])
    todos = []
    for g in db.obtener_requisitos_por_area(p_actual['area_id']): 
        todos.extend(g['items'])
    objs = [r for r in todos if r['id'] in actuales]
    
    p_pdf = dict(p_actual)
    p_pdf['proyecto'] = p_actual['nombre']
    p_pdf['ubicacion'] = f"{p_actual['localidad']}, {p_actual['distrito']}, {p_actual['provincia']}, {p_actual['departamento']}"
    
    # 2. Obtener Slugs para cargar memorias específicas
    sectores_raw = db.obtener_sectores()
    sector_info = sectores_raw[idx_sec]
    areas_raw = db.obtener_areas_por_sector(sector_info['id'])
    area_info = areas_raw[idx_are]
    p_pdf['sector_slug'] = sector_info['slug']
    p_pdf['area_slug'] = area_info['slug']
    
    # 3. Inicializar Código LaTeX
    if 'tex_code' not in st.session_state or st.sidebar.button("Reiniciar Código"):
        st.session_state.tex_code = generar_codigo_latex(p_pdf, objs)
        
    c1, c2 = st.columns([0.4, 0.6])
    
    with c1:
        tex_edit = st.text_area("Código LaTeX", value=st.session_state.tex_code, height=600)
        if st.button("Compilar y Generar PDF", use_container_width=True):
            st.session_state.tex_code = tex_edit
            with st.spinner("Compilando LaTeX..."):
                pdf_path = compilar_latex(tex_edit)
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    st.session_state.pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                    st.success("PDF Generado.")
                else:
                    st.error("Error al compilar el documento.")

    with c2:
        if 'pdf_display' in st.session_state:
            st.markdown(st.session_state.pdf_display, unsafe_allow_html=True)
        else:
            st.info("Presiona 'Compilar' para visualizar el PDF.")
