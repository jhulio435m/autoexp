import json
import os

def clean_seace_data():
    input_path = '/home/jhulio/autoexp/data/documentos_seace.json'
    output_path = '/home/jhulio/autoexp/data/seace_clean.json'
    
    if not os.path.exists(input_path):
        print("Error: No se encontró el archivo de entrada.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    sheet_data = raw_data.get("0. BD", [])
    if not sheet_data:
        print("Error: No se encontró la hoja '0. BD'.")
        return
        
    structured_data = {}
    current_category = "General"
    
    # La fila 2 contiene los encabezados: [ID, Nombre, Edif, Elec, Sane, Transp]
    headers = sheet_data[2]
    sectors = [str(h).replace('\n', ' ').strip() for h in headers[2:]]
    
    for row in sheet_data[3:]:
        if not row or len(row) < 2: continue
        
        doc_id = str(row[0]).strip()
        doc_name = str(row[1]).strip()
        
        # Detectar categorías (Ej: A, B, C...)
        if doc_id and not doc_id.isdigit() and len(doc_id) <= 2:
            current_category = f"{doc_id} - {doc_name}"
            structured_data[current_category] = []
            continue
        
        # Procesar documentos
        normativas = {}
        for i, sector in enumerate(sectors):
            idx = i + 2
            val = ""
            if idx < len(row):
                val = str(row[idx]).strip().replace('\n', ' ')
            normativas[sector] = val
        
        doc_entry = {
            "id": doc_id,
            "nombre": doc_name,
            "normativas": normativas
        }
        
        if current_category not in structured_data:
            structured_data[current_category] = []
        structured_data[current_category].append(doc_entry)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    
    print(f"Limpieza completada. Archivo guardado en: {output_path}")

if __name__ == "__main__":
    clean_seace_data()
