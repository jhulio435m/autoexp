import zipfile
import xml.etree.ElementTree as ET
import json
import os

def extract():
    file_path = '/home/jhulio/autoexp/Herramienta_Expedientes_tecnico.xlsx'
    output_path = '/home/jhulio/autoexp/documentos_seace.json'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} no encontrado")
        return

    with zipfile.ZipFile(file_path, 'r') as z:
        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        # Shared Strings
        shared_strings = []
        try:
            strings_xml = z.read('xl/sharedStrings.xml')
            root_strings = ET.fromstring(strings_xml)
            for si in root_strings.findall('ns:si', ns):
                t_text = "".join([t.text for t in si.findall('.//ns:t', ns) if t.text])
                shared_strings.append(t_text)
        except Exception as e:
            print(f"Aviso: No se pudieron leer sharedStrings: {e}")

        # Workbook
        workbook_xml = z.read('xl/workbook.xml')
        root_workbook = ET.fromstring(workbook_xml)
        sheet_map = {}
        for s in root_workbook.findall('.//ns:sheet', ns):
            name = s.get('name')
            # El ID de la relación es más preciso, pero sheetId suele coincidir con el orden
            sheet_id = s.get('sheetId')
            sheet_map[sheet_id] = name

        data = {}
        for info in z.infolist():
            if info.filename.startswith('xl/worksheets/sheet'):
                # Extraer número de hoja del nombre del archivo (ej. sheet1.xml -> 1)
                import re
                match = re.search(r'sheet(\d+)\.xml', info.filename)
                if not match: continue
                internal_id = match.group(1)
                
                sheet_xml = z.read(info.filename)
                root_sheet = ET.fromstring(sheet_xml)
                
                rows = []
                for row in root_sheet.findall('.//ns:row', ns):
                    row_data = []
                    for c in row.findall('ns:c', ns):
                        v_node = c.find('ns:v', ns)
                        if v_node is not None:
                            if c.get('t') == 's':
                                idx = int(v_node.text)
                                row_data.append(shared_strings[idx] if idx < len(shared_strings) else "")
                            else:
                                row_data.append(v_node.text)
                        else:
                            row_data.append("")
                    if any(row_data):
                        rows.append(row_data)
                
                # Intentar mapear por orden o ID
                sheet_name = sheet_map.get(internal_id, f"Ficha_{internal_id}")
                data[sheet_name] = rows

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Exportado exitosamente a {output_path}")

if __name__ == '__main__':
    extract()
