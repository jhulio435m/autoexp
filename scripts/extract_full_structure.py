import json
import re
import os

def parse_full_text():
    txt_path = "data/memoria_real.txt"
    if not os.path.exists(txt_path):
        return

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    structure = []
    current_section = None
    current_subsection = None
    current_level3 = None
    
    header_re = re.compile(r'^(\d+(\.\d+)*)\s+([A-ZÁÉÍÓÚÑ].*)')

    for line in lines:
        line = line.strip()
        if not line: continue
        
        match = header_re.match(line)
        if match:
            level_num = match.group(1)
            title = match.group(3).split('...')[0].strip()
            title = re.sub(r'[\.\-\s]+$', '', title) # Limpiar final
            
            depth = level_num.count('.') + 1
            node = {"id": level_num, "label": title, "content": "", "subitems": []}
            
            if depth == 1:
                structure.append(node); current_section = node; current_subsection = None; current_level3 = None
            elif depth == 2 and current_section:
                current_section["subitems"].append(node); current_subsection = node; current_level3 = None
            elif depth == 3 and current_subsection:
                current_subsection["subitems"].append(node); current_level3 = node
            elif depth >= 4 and current_level3:
                current_level3["subitems"].append(node)
        else:
            target = current_level3 or current_subsection or current_section
            if target:
                target["content"] += line + " "

    with open("data/FULL_STRUCTURE_TRANSPORTE.json", 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    print("✅ Extracción completa.")

if __name__ == "__main__":
    parse_full_text()
