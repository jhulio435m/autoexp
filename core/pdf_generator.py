import os
import subprocess
import shutil
from jinja2 import Environment, FileSystemLoader
from config import CORE_DIR, OUTPUT_DIR, BASE_DIR

def generar_codigo_latex(datos_proyecto, seleccionados):
    """Renderiza las plantillas LaTeX usando Jinja2 con datos reales."""
    
    # Configurar el entorno de Jinja2 para LaTeX
    env = Environment(
        loader=FileSystemLoader(BASE_DIR),
        block_start_string='[%',
        block_end_string='%]',
        variable_start_string='[[',
        variable_end_string=']]',
        comment_start_string='[#',
        comment_end_string='#]',
    )

    # Preparar el contexto de datos para la plantilla
    context = {
        **datos_proyecto,
        "seleccionados": seleccionados,
        "sector_slug": datos_proyecto.get('sector_slug', 'general'),
        "area_slug": datos_proyecto.get('area_slug', 'general'),
        "incluir_especificaciones": False,
        "incluir_panel_fotografico": False
    }

    try:
        # Cargamos la plantilla maestra
        template = env.get_template("templates/master_template.tex")
        return template.render(context)
    except Exception as e:
        return f"% Error al renderizar plantilla: {str(e)}"

def compilar_latex(codigo_tex):
    """Compila el PDF asegurando que la clase y recursos estén disponibles."""
    src_cls = os.path.join(CORE_DIR, "expediente.cls")
    dest_cls = os.path.join(OUTPUT_DIR, "expediente.cls")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    shutil.copy2(src_cls, dest_cls)
    
    tex_path = os.path.join(OUTPUT_DIR, "preview.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(codigo_tex)
    
    try:
        cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={OUTPUT_DIR}", "preview.tex"]
        subprocess.run(cmd, capture_output=True, text=True, cwd=OUTPUT_DIR)
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=OUTPUT_DIR)
        
        pdf_path = os.path.join(OUTPUT_DIR, "preview.pdf")
        if os.path.exists(pdf_path):
            return pdf_path, None
        return None, f"Error en la compilación. Verifique los logs en output/preview.log"
    except Exception as e:
        return None, str(e)
