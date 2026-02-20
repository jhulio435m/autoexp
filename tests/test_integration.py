import db_manager as db
import pytest
import os

# Heisenberg: Prueba de Pureza (Integración) - V3 (Estándar TDR)

def test_db_connection():
    """Verificar que el reactor responde."""
    conn = db.get_connection()
    assert conn is not None
    conn.close()

def test_sectors_seeded():
    """Verificar que los precursores están en la DB."""
    sectores = db.obtener_sectores()
    assert len(sectores) > 0

def test_project_creation_and_deletion():
    """Validar el ciclo de vida con el nuevo esquema TDR."""
    # 1. Obtener una área para probar
    sectores = db.obtener_sectores()
    s_id = sectores[0]['id']
    areas = db.obtener_areas_por_sector(s_id)
    assert len(areas) > 0
    a_id = areas[0]['id']

    # 2. Sintetizar proyecto con TODOS los campos del TDR
    cui_test = "TEST-QC-99"
    try:
        p_id = db.crear_proyecto(
            entidad="MUNI_TEST", 
            nombre="PROYECTO DE PRUEBA QC", 
            cui=cui_test, 
            dep="LIMA", 
            prov="LIMA", 
            dist="MIRAFLORES", 
            loc="ZONA SUR", 
            consultor="HEISENBERG", 
            jefe="W. WHITE", 
            cip="123456", 
            monto=1500000.00, 
            plazo=120, 
            mod="CONTRATA", 
            sistema="SUMA ALZADA", 
            tipo="MEJORAMIENTO", 
            benef=5000, 
            zona="18S", 
            este=280000.00, 
            norte=8600000.00, 
            area_id=a_id
        )
        assert p_id is not None
        
        # 3. Verificar persistencia
        p = db.obtener_proyecto_por_id(p_id)
        assert p['cui'] == cui_test
        assert p['jefe_proyecto'] == "W. WHITE"
        
        # 4. Purga
        db.eliminar_proyecto(p_id)
        assert db.obtener_proyecto_por_id(p_id) is None
        
    except Exception as e:
        # Limpieza de emergencia
        conn = db.get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM proyectos WHERE cui = %s;", (cui_test,))
        conn.commit()
        conn.close()
        raise e
