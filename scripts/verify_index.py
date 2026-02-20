import json
import re
import os

def verify_consistency():
    json_path = "data/document_structures.json"
    txt_path = "data/memoria_real.txt"
    
    if not os.path.exists(json_path) or not os.path.exists(txt_path):
        print("❌ Archivos faltantes para la verificación.")
        return

    # 1. Cargar Estructura JSON
    with open(json_path, 'r') as f:
        doc_json = json.load(f)
    
    # Secciones esperadas en Memoria Descriptiva según el JSON
    expected_sections = []
    for sector in doc_json.values():
        if "memoria_descriptiva" in sector:
            for sec in sector["memoria_descriptiva"]["secciones"]:
                expected_sections.append(sec["label"].upper())
                for field in sec["campos"]:
                    expected_sections.append(field["label"].upper())

    # 2. Analizar el Texto Real
    with open(txt_path, 'r') as f:
        content = f.read()

    pages = content.split('\f')
    real_index = {}
    
    for i, page_text in enumerate(pages):
        page_num = i + 1
        lines = page_text.split('\n')
        for line in lines:
            line = line.strip()
            # Patrón para títulos en mayúsculas o numerados
            if len(line) > 5 and (re.match(r'^[\d\.]+\s+[A-ZÁÉÍÓÚÑ]', line) or (line.isupper() and len(line.split()) < 10)):
                clean_title = re.sub(r'^[\d\.]+\s+', '', line).strip().upper()
                # Limpiar caracteres especiales de TOC
                clean_title = clean_title.replace('.', '').strip()
                if clean_title not in real_index:
                    real_index[clean_title] = page_num

    # 3. Comparación
    matches = 0
    discrepancies = []
    
    print("\n--- REPORTE DE CONSISTENCIA: JSON VS PDF (TEXTO) ---")
    print(f"{'SECCIÓN EN JSON':<40} | {'ESTADO':<10} | {'PÁGINA PDF'}")
    print("-" * 70)

    for section in expected_sections:
        clean_section = section.replace('.', '').strip().upper()
        found = False
        found_page = None
        
        for real_title, p_num in real_index.items():
            if clean_section in real_title or real_title in clean_section:
                found = True
                found_page = p_num
                break
        
        if found:
            matches += 1
            print(f"{section[:40]:<40} | ✅ OK       | Pag. {found_page}")
        else:
            discrepancies.append(section)
            print(f"{section[:40]:<40} | ❌ MISS     | ---")

    accuracy = (matches / total_expected) * 100 if (total_expected := len(expected_sections)) > 0 else 0
    
    print("-" * 70)
    print(f"RESUMEN FINAL:")
    print(f"Coincidencias: {matches} / {total_expected}")
    print(f"Porcentaje de Coincidencia: {accuracy:.2f}%")
    
    if discrepancies:
        print("\nLISTA DE DISCREPANCIAS (No encontradas o con nombre diferente):")
        for d in discrepancies:
            print(f" - {d}")

if __name__ == "__main__":
    verify_consistency()
