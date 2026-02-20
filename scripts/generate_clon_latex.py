import json
import os

def generate_clon_latex():
    json_path = "data/FULL_STRUCTURE_TRANSPORTE.json"
    if not os.path.exists(json_path): return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    latex = [
        r"\documentclass{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[spanish]{babel}",
        r"\title{MEMORIA DESCRIPTIVA - CLON PDF}",
        r"\begin{document}",
        r"\maketitle",
        r"\tableofcontents",
        r"\newpage"
    ]

    def process_node(node, level):
        cmd = "section" if level == 1 else "subsection" if level == 2 else "subsubsection" if level == 3 else "paragraph"
        title = node['label'].replace('&', r'\&').replace('_', r'\_').replace('%', r'\%')
        latex.append(f"\\{cmd}{{{title}}}")
        
        if node['content'].strip():
            txt = node['content'].replace('&', r'\&').replace('_', r'\_').replace('%', r'\%').replace('$', r'\$')
            latex.append(txt + "\n")
        
        for sub in node.get('subitems', []):
            process_node(sub, level + 1)

    for item in data:
        process_node(item, 1)

    latex.append(r"\end{document}")

    with open("output/clon_memoria.tex", 'w', encoding='utf-8') as f:
        f.write("\n".join(latex))
    print("✅ Archivo LaTeX clonado generado en output/clon_memoria.tex")

if __name__ == "__main__":
    generate_clon_latex()
