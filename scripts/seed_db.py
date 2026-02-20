import json
import os
import sys
import re

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_manager as db
from config import BASE_DIR

MASTER_JSON = os.path.join(BASE_DIR, "data", "documentos_seace.json")

# Mapeo de sectores a índices de columnas en el JSON maestro
# 0: ID/Letra, 1: Nombre, 2: Edificación, 3: Electrificación, 4: Saneamiento, 5: Transportes
SECTOR_MAP = {
    "SALUD": {"col": 2, "slug": "salud"},
    "EDUCACIÓN": {"col": 2, "slug": "educacion"},
    "TRANSPORTE": {"col": 5, "slug": "transporte"},
    "AGUA Y SANEAMIENTO": {"col": 4, "slug": "agua_y_saneamiento"},
    "ELECTRIFICACIÓN": {"col": 3, "slug": "electrificacion"},
    "AGRICULTURA": {"col": 4, "slug": "agricultura"}, # Usamos saneamiento/riego como base
    "GENERAL": {"col": 2, "slug": "general"}
}

def clean_name(text):
    if not text: return ""
    # Quitar números iniciales y espacios extra
    return re.sub(r'^[\d\.]+\s*', '', text).strip()

def seed_from_master():
    print("🧪 Heisenberg: Iniciando sincronización con el Maestro SEACE...")
    
    if not os.path.exists(MASTER_JSON):
        print(f"❌ Error: No se encuentra {MASTER_JSON}")
        return

    with open(MASTER_JSON, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    # La hoja principal suele ser "0. BD"
    rows = master_data.get("0. BD", [])
    if not rows:
        print("❌ Error: La hoja '0. BD' está vacía.")
        return

    conn = db.get_connection()
    with conn.cursor() as cur:
        print("🧹 Limpiando el laboratorio (tablas maestras)...")
        cur.execute("TRUNCATE sectores, areas, grupos, requisitos CASCADE;")
    conn.commit()
    conn.close()

    for sector_name, config in SECTOR_MAP.items():
        s_id = db.insertar_o_actualizar_sector(sector_name, config['slug'], "")
        print(f"💎 Sincronizando Sector: {sector_name}")
        
        # Definir áreas por defecto para cada sector
        areas = [{"nombre": "ÁREA GENERAL", "slug": "general"}]
        if config['slug'] == "transporte":
            areas = [{"nombre": "PISTAS Y VEREDAS", "slug": "pistas"}, {"nombre": "PUENTES Y OBRAS DE ARTE", "slug": "puentes"}]
        elif config['slug'] == "agua_y_saneamiento":
            areas = [{"nombre": "REDES DE AGUA Y ALCANTARILLADO", "slug": "redes"}, {"nombre": "PLANTAS DE TRATAMIENTO", "slug": "plantas"}]

        for area_info in areas:
            a_id = db.insertar_area(s_id, area_info['nombre'], area_info['slug'])
            
            current_group_id = None
            for row in rows:
                if not row or len(row) < 2: continue
                
                col0 = str(row[0]).strip()
                col1 = str(row[1]).strip()
                
                # Detectar cabecera de grupo (Letras A, B, C...)
                if len(col0) == 1 and col0.isalpha() and not col1.startswith("Nº"):
                    if col0 in ['C', 'D']:
                        current_group_id = None # Saltamos estos grupos
                        continue
                    current_group_id = db.insertar_grupo(a_id, col0, col1)
                
                # Detectar requisito (Números 1, 2, 3...)
                elif col0.isdigit() and current_group_id:
                    normativa = ""
                    if len(row) > config['col']:
                        normativa = str(row[config['col']]).strip()
                    
                    db.insertar_requisito(
                        current_group_id,
                        col0,
                        clean_name(col1),
                        normativa,
                        es_predeterminado=True
                    )

    print("🏁 Heisenberg: Sincronización completa. Datos actualizados.")

if __name__ == '__main__':
    seed_from_master()
