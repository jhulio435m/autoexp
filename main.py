from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import db_manager as db
import os
import base64
from core.pdf_generator import generar_codigo_latex, compilar_latex
from utils.ubigeo import UBIGEO_DATA

app = FastAPI()

# Configurar CORS para que React pueda comunicarse con FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

class Proyecto(BaseModel):
    id: Optional[int] = None
    entidad: str
    nombre: str
    cui: str
    departamento: str
    provincia: str
    distrito: str
    localidad: str
    consultor: Optional[str] = ""
    jefe_proyecto: str
    cip_jefe: str
    monto: float
    plazo: int
    modalidad: str
    sistema_contratacion: str
    tipo_intervencion: Optional[str] = ""
    beneficiarios: Optional[int] = 0
    zona_utm: str
    este_utm: float
    norte_utm: float
    area_id: int

@app.get("/api/sectores")
def get_sectores():
    return db.obtener_sectores()

@app.get("/api/areas/{sector_id}")
def get_areas(sector_id: int):
    return db.obtener_areas_por_sector(sector_id)

@app.get("/api/proyectos")
def get_proyectos():
    return db.obtener_proyectos()

@app.get("/api/proyectos/{proyecto_id}")
def get_proyecto(proyecto_id: int):
    p = db.obtener_proyecto_por_id(proyecto_id)
    if not p:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return p

@app.post("/api/proyectos")
def create_proyecto(p: Proyecto):
    try:
        p_id = db.crear_proyecto(
            p.entidad, p.nombre, p.cui, p.departamento, p.provincia, p.distrito, 
            p.localidad, p.consultor, p.jefe_proyecto, p.cip_jefe, p.monto, 
            p.plazo, p.modalidad, p.sistema_contratacion, p.tipo_intervencion, 
            p.beneficiarios, p.zona_utm, p.este_utm, p.norte_utm, p.area_id
        )
        return {"id": p_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/proyectos/{proyecto_id}")
def update_proyecto(proyecto_id: int, p: Proyecto):
    try:
        db.actualizar_proyecto(
            proyecto_id, p.entidad, p.nombre, p.cui, p.departamento, p.provincia, 
            p.distrito, p.localidad, p.consultor, p.jefe_proyecto, p.cip_jefe, 
            p.monto, p.plazo, p.modalidad, p.sistema_contratacion, p.tipo_intervencion, 
            p.beneficiarios, p.zona_utm, p.este_utm, p.norte_utm, p.area_id
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/proyectos/{proyecto_id}")
def delete_proyecto(proyecto_id: int):
    db.eliminar_proyecto(proyecto_id)
    return {"status": "ok"}

import re

@app.get("/api/requisitos/{area_id}")
def get_requisitos(area_id: int):
    grupos = db.obtener_requisitos_por_area(area_id)
    # Limpiar nombres de ítems: quitar números iniciales como "1. ", "01. ", etc.
    for g in grupos:
        for item in g.get('items', []):
            item['nombre'] = re.sub(r'^[\d\.]+\s*', '', item['nombre'])
    return grupos

@app.get("/api/selecciones/{proyecto_id}")
def get_selecciones(proyecto_id: int):
    return db.obtener_selecciones(proyecto_id)

@app.post("/api/selecciones/{proyecto_id}")
def save_selecciones(proyecto_id: int, requisito_ids: List[int]):
    db.guardar_selecciones(proyecto_id, requisito_ids)
    return {"status": "ok"}

@app.get("/api/ubigeo")
def get_ubigeo():
    return UBIGEO_DATA

@app.get("/api/estructuras")
def get_document_structures():
    path = os.path.join(BASE_DIR, "data", "document_structures.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.get("/api/selecciones/{proyecto_id}/{requisito_id}/metadata")
def get_document_metadata(proyecto_id: int, requisito_id: int):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT metadata FROM selecciones WHERE proyecto_id = %s AND requisito_id = %s;", (proyecto_id, requisito_id))
        res = cur.fetchone()
    conn.close()
    return res['metadata'] if res else {}

@app.post("/api/selecciones/{proyecto_id}/{requisito_id}/metadata")
def save_document_metadata(proyecto_id: int, requisito_id: int, metadata: dict = Body(...)):
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE selecciones SET metadata = %s WHERE proyecto_id = %s AND requisito_id = %s;", (json.dumps(metadata), proyecto_id, requisito_id))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/selecciones/{proyecto_id}/{requisito_id}/tex")
def get_document_tex(proyecto_id: int, requisito_id: int):
    p_actual = db.obtener_proyecto_por_id(proyecto_id)
    if not p_actual:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Obtener el ítem específico
    conn = db.get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM requisitos WHERE id = %s;", (requisito_id,))
        item = cur.fetchone()
        cur.execute("SELECT metadata FROM selecciones WHERE proyecto_id = %s AND requisito_id = %s;", (proyecto_id, requisito_id))
        sel = cur.fetchone()
    conn.close()
    
    if not item:
        raise HTTPException(status_code=404, detail="Requisito no encontrado")

    metadata = sel['metadata'] if sel else {}
    
    # Preparar datos para la plantilla
    p_pdf = dict(p_actual)
    p_pdf['proyecto'] = p_actual['nombre']
    p_pdf['ubicacion'] = f"{p_actual['localidad']}, {p_actual['distrito']}, {p_actual['provincia']}, {p_actual['departamento']}"
    
    # Metadatos del documento específico se inyectan en el contexto
    p_pdf.update(metadata)
    
    # Generar LaTeX solo para este documento
    tex_code = generar_codigo_latex(p_pdf, [item])
    return {"tex_code": tex_code, "metadata": metadata}

@app.post("/api/pdf/preview")
def preview_pdf(data: dict):
    # data: { proyecto_id: int, tex_code: str (opcional) }
    p_id = data.get('proyecto_id')
    tex_code = data.get('tex_code')
    
    p_actual = db.obtener_proyecto_por_id(p_id)
    if not p_actual:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
    if not tex_code:
        # Generar código base si no se envía uno personalizado
        actuales = db.obtener_selecciones(p_id)
        todos = []
        for g in db.obtener_requisitos_por_area(p_actual['area_id']): 
            todos.extend(g['items'])
        objs = [r for r in todos if r['id'] in actuales]
        
        p_pdf = dict(p_actual)
        p_pdf['proyecto'] = p_actual['nombre']
        p_pdf['ubicacion'] = f"{p_actual['localidad']}, {p_actual['distrito']}, {p_actual['provincia']}, {p_actual['departamento']}"
        
        # Necesitamos slugs
        sectores = db.obtener_sectores()
        sector_info = next((s for s in sectores if s['id'] == p_actual['sector_id']), None)
        areas = db.obtener_areas_por_sector(p_actual['sector_id'])
        area_info = next((a for a in areas if a['id'] == p_actual['area_id']), None)
        
        p_pdf['sector_slug'] = sector_info['slug'] if sector_info else 'general'
        p_pdf['area_slug'] = area_info['slug'] if area_info else 'general'
        
        tex_code = generar_codigo_latex(p_pdf, objs)
    
    pdf_path, error = compilar_latex(tex_code)
    if error:
        raise HTTPException(status_code=500, detail=error)
        
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    return {"pdf_base64": base64_pdf, "tex_code": tex_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
