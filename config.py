import os

# Rutas Base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECTORS_DIR = os.path.join(BASE_DIR, "data", "sectors")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CORE_DIR = os.path.join(BASE_DIR, "core")

# Crear directorios si no existen
for d in [OUTPUT_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

# Configuración de Sectores (Sin emojis, nombres corporativos)
CONFIG_SECTORES = {
    "agricultura": {"nombre": "AGRICULTURA"},
    "agua_y_saneamiento": {"nombre": "AGUA Y SANEAMIENTO"},
    "educacion": {"nombre": "EDUCACIÓN"},
    "electrificacion": {"nombre": "ELECTRIFICACIÓN"},
    "general": {"nombre": "GENERAL"},
    "salud": {"nombre": "SALUD"},
    "transporte": {"nombre": "TRANSPORTE"}
}

def get_sector_label(filename):
    name_clean = filename.replace('.json', '')
    config = CONFIG_SECTORES.get(name_clean, {})
    name = config.get("nombre") or name_clean.replace('_', ' ').upper()
    return name
