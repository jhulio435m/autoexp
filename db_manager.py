import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://autoexp_user:autoexp_password@db:5432/autoexp_db")

def get_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        except Exception:
            retries -= 1
            time.sleep(2)
    raise Exception("No se pudo conectar a PostgreSQL")

def init_db():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS sectores (id SERIAL PRIMARY KEY, nombre TEXT NOT NULL, slug TEXT UNIQUE NOT NULL, icono TEXT);")
        cur.execute("CREATE TABLE IF NOT EXISTS areas (id SERIAL PRIMARY KEY, sector_id INTEGER REFERENCES sectores(id) ON DELETE CASCADE, nombre TEXT NOT NULL, slug TEXT NOT NULL, UNIQUE(sector_id, slug));")
        cur.execute("CREATE TABLE IF NOT EXISTS grupos (id SERIAL PRIMARY KEY, area_id INTEGER REFERENCES areas(id) ON DELETE CASCADE, letra TEXT, nombre TEXT NOT NULL);")
        cur.execute("CREATE TABLE IF NOT EXISTS requisitos (id SERIAL PRIMARY KEY, grupo_id INTEGER REFERENCES grupos(id) ON DELETE CASCADE, codigo TEXT, nombre TEXT NOT NULL, normativa TEXT, es_predeterminado BOOLEAN DEFAULT TRUE);")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id SERIAL PRIMARY KEY,
                area_id INTEGER REFERENCES areas(id),
                entidad TEXT NOT NULL,
                nombre TEXT NOT NULL,
                cui TEXT UNIQUE NOT NULL,
                departamento TEXT,
                provincia TEXT,
                distrito TEXT,
                localidad TEXT,
                consultor TEXT,
                jefe_proyecto TEXT,
                cip_jefe TEXT,
                monto NUMERIC(15,2),
                plazo INTEGER,
                modalidad TEXT,
                sistema_contratacion TEXT,
                tipo_intervencion TEXT,
                beneficiarios INTEGER,
                zona_utm TEXT,
                este_utm NUMERIC(12,2),
                norte_utm NUMERIC(12,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("CREATE TABLE IF NOT EXISTS selecciones (proyecto_id INTEGER REFERENCES proyectos(id) ON DELETE CASCADE, requisito_id INTEGER REFERENCES requisitos(id) ON DELETE CASCADE, PRIMARY KEY (proyecto_id, requisito_id));")
    conn.commit()
    conn.close()

def crear_proyecto(entidad, nombre, cui, dep, prov, dist, loc, consultor, jefe, cip, monto, plazo, mod, sistema, tipo, benef, zona, este, norte, area_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO proyectos (entidad, nombre, cui, departamento, provincia, distrito, localidad, consultor, jefe_proyecto, cip_jefe, monto, plazo, modalidad, sistema_contratacion, tipo_intervencion, beneficiarios, zona_utm, este_utm, norte_utm, area_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (entidad, nombre, cui, dep, prov, dist, loc, consultor, jefe, cip, monto, plazo, mod, sistema, tipo, benef, zona, este, norte, area_id))
        p_id = cur.fetchone()['id']
        cur.execute("INSERT INTO selecciones (proyecto_id, requisito_id) SELECT %s, r.id FROM requisitos r JOIN grupos g ON r.grupo_id = g.id WHERE g.area_id = %s AND r.es_predeterminado = TRUE;", (p_id, area_id))
    conn.commit()
    conn.close()
    return p_id

def actualizar_proyecto(p_id, entidad, nombre, cui, dep, prov, dist, loc, consultor, jefe, cip, monto, plazo, mod, sistema, tipo, benef, zona, este, norte, area_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE proyectos SET entidad=%s, nombre=%s, cui=%s, departamento=%s, provincia=%s, distrito=%s, localidad=%s, consultor=%s, jefe_proyecto=%s, cip_jefe=%s, monto=%s, plazo=%s, modalidad=%s, sistema_contratacion=%s, tipo_intervencion=%s, beneficiarios=%s, zona_utm=%s, este_utm=%s, norte_utm=%s, area_id=%s
            WHERE id = %s;
        """, (entidad, nombre, cui, dep, prov, dist, loc, consultor, jefe, cip, monto, plazo, mod, sistema, tipo, benef, zona, este, norte, area_id, p_id))
    conn.commit()
    conn.close()

def obtener_proyectos():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.*, a.nombre as area_nombre, s.nombre as sector_nombre, s.id as sector_id 
            FROM proyectos p JOIN areas a ON p.area_id = a.id JOIN sectores s ON a.sector_id = s.id ORDER BY p.created_at DESC;
        """)
        res = cur.fetchall()
    conn.close()
    return res

def obtener_proyecto_por_id(p_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT p.*, a.sector_id FROM proyectos p JOIN areas a ON p.area_id = a.id WHERE p.id = %s;", (p_id,))
        res = cur.fetchone()
    conn.close()
    return res

def eliminar_proyecto(p_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM proyectos WHERE id = %s;", (p_id,))
    conn.commit()
    conn.close()

def obtener_requisitos_por_area(area_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM grupos WHERE area_id = %s ORDER BY letra;", (area_id,))
        grupos = cur.fetchall()
        for g in grupos:
            cur.execute("SELECT * FROM requisitos WHERE grupo_id = %s ORDER BY id;", (g['id'],))
            g['items'] = cur.fetchall()
    conn.close()
    return grupos

def guardar_selecciones(proyecto_id, requisito_ids):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM selecciones WHERE proyecto_id = %s;", (proyecto_id,))
        for r_id in requisito_ids:
            cur.execute("INSERT INTO selecciones (proyecto_id, requisito_id) VALUES (%s, %s);", (proyecto_id, r_id))
    conn.commit()
    conn.close()

def obtener_selecciones(proyecto_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT requisito_id FROM selecciones WHERE proyecto_id = %s;", (proyecto_id,))
        res = [row['requisito_id'] for row in cur.fetchall()]
    conn.close()
    return res

def insertar_o_actualizar_sector(nombre, slug, icono):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO sectores (nombre, slug, icono) VALUES (%s, %s, %s) ON CONFLICT (slug) DO UPDATE SET nombre=EXCLUDED.nombre, icono=EXCLUDED.icono RETURNING id;", (nombre, slug, icono))
        res = cur.fetchone()['id']
    conn.commit()
    conn.close()
    return res

def insertar_area(sector_id, nombre, slug):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO areas (sector_id, nombre, slug) VALUES (%s, %s, %s) ON CONFLICT (sector_id, slug) DO UPDATE SET nombre=EXCLUDED.nombre RETURNING id;", (sector_id, nombre, slug))
        res = cur.fetchone()['id']
    conn.commit()
    conn.close()
    return res

def insertar_grupo(area_id, letra, nombre):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO grupos (area_id, letra, nombre) VALUES (%s, %s, %s) RETURNING id;", (area_id, letra, nombre))
        res = cur.fetchone()['id']
    conn.commit()
    conn.close()
    return res

def insertar_requisito(grupo_id, codigo, nombre, normativa, es_predeterminado=True):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO requisitos (grupo_id, codigo, nombre, normativa, es_predeterminado) VALUES (%s, %s, %s, %s, %s);", (grupo_id, codigo, nombre, normativa, es_predeterminado))
    conn.commit()
    conn.close()

def obtener_sectores():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM sectores ORDER BY nombre;")
        res = cur.fetchall()
    conn.close()
    return res

def obtener_areas_por_sector(sector_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM areas WHERE sector_id = %s ORDER BY nombre;", (sector_id,))
        res = cur.fetchall()
    conn.close()
    return res
