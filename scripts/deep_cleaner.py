import json
import os

def clean_sector_files():
    sectors_dir = '/home/jhulio/autoexp/data/sectors/'
    files = [f for f in os.listdir(sectors_dir) if f.endswith('.json') and f != 'general.json']
    
    for filename in files:
        filepath = os.path.join(sectors_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        raw_rows = content.get('documentos', [])
        structured_groups = []
        current_group = None
        
        # Encontrar el índice de inicio (donde están los encabezados)
        start_idx = 0
        for i, row in enumerate(raw_rows):
            if any("DOCUMENTOS" in str(cell).upper() for cell in row):
                start_idx = i + 1
                break
        
        for row in raw_rows[start_idx:]:
            if not any(row): continue
            
            # Identificar Grupo/Categoría (Ej: A, B, C...)
            # Usualmente es una fila con una letra en la col 0 y texto en col 1, y col 2 vacía
            col0 = str(row[0]).strip()
            col1 = str(row[1]).strip()
            col2 = str(row[2]).strip() if len(row) > 2 else ""
            
            # Si col0 es una letra (A, B, C...) y col2 está casi vacía, es un encabezado de grupo
            if col0.isalpha() and len(col0) == 1 and col1 and not col2:
                current_group = {
                    "letra": col0,
                    "nombre": col1,
                    "items": []
                }
                structured_groups.append(current_group)
                continue
            
            # Si tenemos un grupo activo y la fila tiene contenido, es un documento
            if current_group is not None:
                # El ID puede ser numérico o estar vacío si es continuación
                doc_id = col0
                doc_name = col1
                normativa = col2
                
                if doc_name and doc_name.upper() != "DOCUMENTOS":
                    current_group["items"].append({
                        "id": doc_id,
                        "nombre": doc_name,
                        "normativa": normativa
                    })
        
        # Guardar la versión limpia
        clean_content = {
            "sector": content["sector"],
            "grupos": structured_groups
        }
        
        with open(filepath, 'w', encoding='utf-8') as f_out:
            json.dump(clean_content, f_out, ensure_ascii=False, indent=2)
        print(f"Limpieza profunda completada: {filename}")

if __name__ == "__main__":
    clean_sector_files()
