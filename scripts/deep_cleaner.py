import json
import os

sectors_dir = 'data/sectors'

def clean_sector_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified = False
    
    # Caso 1: Estructura con "grupos" (como educacion.json)
    if 'grupos' in data:
        original_len = len(data['grupos'])
        data['grupos'] = [g for g in data['grupos'] if g.get('letra') not in ['C', 'D']]
        if len(data['grupos']) != original_len:
            modified = True
            
    # Caso 2: Estructura de lista plana (como general.json)
    elif 'documentos' in data:
        new_docs = []
        skip = False
        for item in data['documentos']:
            # Si el primer elemento es 'C' o 'D' (encabezado de sección)
            if isinstance(item, list) and len(item) > 0:
                if item[0] in ['C', 'D']:
                    skip = True
                    continue
                # Si encontramos otra letra que no sea C o D después de haber empezado a saltar, 
                # (aunque usualmente C y D son las últimas)
                elif item[0].isalpha() and len(item[0]) == 1 and item[0] not in ['C', 'D']:
                    skip = False
            
            if not skip:
                new_docs.append(item)
        
        if len(new_docs) != len(data['documentos']):
            data['documentos'] = new_docs
            modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Limpio: {file_path}")
    else:
        print(f"Sin cambios: {file_path}")

for filename in os.listdir(sectors_dir):
    if filename.endswith('.json'):
        clean_sector_file(os.path.join(sectors_dir, filename))
