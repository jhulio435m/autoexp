import streamlit as st
import db_manager as db
from utils.ubigeo import UBIGEO_DATA

def screen_seleccion_proyecto():
    proyectos = db.obtener_proyectos()
    
    if proyectos:
        st.markdown("### Mis Proyectos")
        for p in proyectos:
            with st.container(border=True):
                # Distribución: CUI, Nombre, Sector/Area, Monto, Abrir
                c_cui, c_nom, c_sector, c_monto, c_sel = st.columns([0.1, 0.4, 0.25, 0.15, 0.1])
                c_cui.markdown(f"**{p['cui']}**")
                c_nom.markdown(f"**{p['nombre'].upper()}**")
                # Mostrar Sector y Área
                c_sector.caption(f"{p['sector_nombre'].upper()}")
                c_sector.markdown(f"{p['area_nombre']}")
                c_monto.markdown(f"S/. {p['monto']:,.2f}" if p['monto'] else "-")
                if c_sel.button("Abrir", key=f"btn_sel_{p['id']}", use_container_width=True):
                    st.session_state.proyecto_id = p['id']
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if not st.checkbox("➕ REGISTRAR NUEVO PROYECTO", key="show_form"):
            st.stop()
            
    st.markdown("---")
    with st.container(border=True):
        st.subheader("Nuevo Registro")
        
        sectores = db.obtener_sectores()
        if not sectores: return st.error("No hay sectores configurados.")

        c1, c2, c3, c4 = st.columns([0.25, 0.25, 0.25, 0.25])
        with c1:
            idx_s = st.selectbox("Sector", range(len(sectores)), format_func=lambda i: sectores[i]['nombre'].upper())
            sector_id = sectores[idx_s]['id']
        with c2:
            areas = db.obtener_areas_por_sector(sector_id)
            idx_a = st.selectbox("Área", range(len(areas)), format_func=lambda i: areas[i]['nombre'].upper())
            area_id = areas[idx_a]['id']
        with c3:
            entidad = st.text_input("Entidad", key="new_entidad")
        with c4:
            cui = st.text_input("CUI", key="new_cui")

        nombre = st.text_area("Nombre del Proyecto", height=80, key="new_nombre")

        st.markdown("**Ubicación Geográfica**")
        u1, u2, u3, u4 = st.columns([0.2, 0.2, 0.2, 0.4])
        deps = sorted(list(UBIGEO_DATA.keys()))
        dep = u1.selectbox("Departamento", deps, key="new_dep")
        pro = u2.selectbox("Provincia", sorted(list(UBIGEO_DATA[dep].keys())), key="new_pro")
        dis = u3.selectbox("Distrito", sorted(UBIGEO_DATA[dep][pro]), key="new_dis")
        loc = u4.text_input("Localidad / Sector", key="new_loc")

        st.markdown("**Responsable y Parámetros Técnicos**")
        p1, p2, p3, p4, p5 = st.columns([0.2, 0.15, 0.2, 0.25, 0.2])
        jefe = p1.text_input("Jefe de Proyecto", key="new_jefe")
        cip = p2.text_input("CIP", key="new_cip")
        monto = p3.number_input("Monto (S/.)", min_value=0.0, format="%.2f", key="new_monto")
        plazo = p4.number_input("Plazo (Días)", min_value=0, key="new_plazo")
        mod = p5.selectbox("Modalidad", ["CONTRATA", "ADMINISTRACIÓN DIRECTA", "OBRAS POR IMPUESTOS"], key="new_mod")

        st.markdown("**Sistema y Georeferenciación**")
        z1, z2, z3, z4 = st.columns([0.2, 0.2, 0.2, 0.4])
        sis = z1.selectbox("Sistema", ["SUMA ALZADA", "PRECIOS UNITARIOS", "MIXTO"], key="new_sis")
        zona = z2.selectbox("Zona UTM", ["17S", "18S", "19S"], key="new_zona")
        este = z3.number_input("Este (X)", format="%.2f", key="new_este")
        norte = z4.number_input("Norte (Y)", format="%.2f", key="new_norte")
        
        if st.button("REGISTRAR PROYECTO", use_container_width=True):
            if entidad and nombre and cui:
                try:
                    p_id = db.crear_proyecto(entidad, nombre, cui, dep, pro, dis, loc, "CONSULTOR", jefe, cip, monto, plazo, mod, sis, "MEJORAMIENTO", 0, zona, este, norte, area_id)
                    st.session_state.proyecto_id = p_id
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else: st.error("Complete los datos obligatorios.")

def sidebar_manager(p_actual):
    st.sidebar.markdown("### GESTIÓN")
    st.sidebar.markdown(f"**PROYECTO:**  \n{p_actual['nombre'].upper()}")
    st.sidebar.caption(f"CUI: {p_actual['cui']}")
    
    # Mostrar Sector y Área en el Sidebar
    sectores = db.obtener_sectores()
    sector_nombre = next((s['nombre'] for s in sectores if s['id'] == p_actual['sector_id']), "N/A")
    areas = db.obtener_areas_por_sector(p_actual['sector_id'])
    area_nombre = next((a['nombre'] for a in areas if a['id'] == p_actual['area_id']), "N/A")
    
    st.sidebar.divider()
    st.sidebar.caption("SECTOR")
    st.sidebar.markdown(f"**{sector_nombre.upper()}**")
    st.sidebar.caption("ÁREA / ESPECIALIDAD")
    st.sidebar.markdown(f"{area_nombre}")
    
    st.sidebar.divider()
    if st.sidebar.button("VOLVER A PROYECTOS", use_container_width=True):
        st.session_state.proyecto_id = None
        st.rerun()

    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    with st.sidebar.expander("OPERACIONES"):
        pwd = st.text_input("Password", type="password", key="del_pwd")
        if st.sidebar.button("ELIMINAR", use_container_width=True):
            if pwd == "176132":
                db.eliminar_proyecto(p_actual['id'])
                st.session_state.proyecto_id = None
                st.rerun()
            else: st.error("Incorrecto.")
