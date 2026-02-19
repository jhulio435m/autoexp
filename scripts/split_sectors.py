import json
import os

def split_sectors():
    input_file = '/home/jhulio/autoexp/data/documentos_seace.json'
    output_dir = '/home/jhulio/autoexp/data/sectors'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    mapping = {
        '0. BD': 'general',
        '0.Formato Contenido Minim. EETT': 'educacion',
        'Ficha_3': 'electrificacion',
        'Ficha_8': 'salud',
        'Ficha_7': 'transporte',
        '0. TD': 'agricultura',
        'Ficha_5': 'agua_y_saneamiento'
    }

    for sheet_key, filename in mapping.items():
        if sheet_key in data:
            sheet_content = data[sheet_key]
            
            clean_rows = []
            for row in sheet_content:
                # Filtrar filas vacías y limpiar celdas
                new_row = [str(c).strip().replace('\n', ' ') for c in row if c is not None]
                if any(new_row):
                    clean_rows.append(new_row)
            
            result = {
                "sector": filename.replace('_', ' ').title(),
                "hoja_original": sheet_key,
                "documentos": clean_rows
            }
            
            out_path = os.path.join(output_dir, filename + '.json')
            with open(out_path, 'w', encoding='utf-8') as f_out:
                json.dump(result, f_out, ensure_ascii=False, indent=2)
            print(f"Generado: {out_path}")

if __name__ == '__main__':
    split_sectors()
