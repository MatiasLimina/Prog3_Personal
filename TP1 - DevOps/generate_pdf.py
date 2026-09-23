import os
import re
import shutil
import subprocess
import base64
import pypdf
import mistune

def generate():
    target_md = 'TP1_Despliegue_VPS_Informe_Final.md'
    target_pdf = 'TP1_Despliegue_VPS_Informe_Final.pdf'
    submission_pdf = 'TP-Com2-Monjelardi-Aguero-Limina.pdf'
    temp_html = 'informe_temp.html'

    if not os.path.exists(target_md):
        raise FileNotFoundError(f'No se encontró el archivo markdown base: {target_md}')

    with open(target_md, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 1. Transformar referencias de imágenes a URIs base64 embebidas
    image_count = 0
    def replace_image_with_base64(match):
        nonlocal image_count
        alt_text = match.group(1)
        img_path = match.group(2)
        
        if img_path.startswith(('http://', 'https://', 'data:')):
            return f'![{alt_text}]({img_path})'
        
        clean_path = img_path.replace('file:///', '').replace('file://', '').replace('/', os.sep)
        if not os.path.isabs(clean_path):
            clean_path = os.path.abspath(clean_path)
            
        if os.path.exists(clean_path):
            image_count += 1
            ext = os.path.splitext(clean_path)[1].lower().replace('.', '')
            if ext == 'jpg':
                ext = 'jpeg'
            with open(clean_path, 'rb') as img_f:
                b64_data = base64.b64encode(img_f.read()).decode('utf-8')
            return f'![{alt_text}](data:image/{ext};base64,{b64_data})'
        else:
            print(f'[ADVERTENCIA] No se encontró la imagen en disco: {clean_path}')
            return f'![{alt_text}]({img_path})'

    processed_md = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image_with_base64, md_content)
    print(f'[INFO] {image_count} imágenes convertidas exitosamente a base64.')

    # 2. Parsear Markdown a HTML con Mistune
    try:
        markdown_parser = mistune.create_markdown(plugins=['table', 'task_lists', 'strikethrough'])
        html_body = markdown_parser(processed_md)
    except Exception as e:
        print(f'[INFO] Usando parser estándar de mistune ({e})')
        html_body = mistune.html(processed_md)

    # 3. Inyectar estilos CSS optimizados para A4 e impresión de alta fidelidad
    css = """
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

      @page {
        size: A4;
        margin: 16mm 14mm 16mm 14mm;
      }

      body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1e293b;
        line-height: 1.5;
        font-size: 12.5px;
        background: #fff;
        margin: 0;
        padding: 0;
      }

      h1 {
        font-size: 21px;
        font-weight: 800;
        color: #0f172a;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 5px;
        margin-top: 0;
        margin-bottom: 4px;
      }

      h2 {
        font-size: 15.5px;
        font-weight: 700;
        color: #1e3a8a;
        margin-top: 20px;
        margin-bottom: 8px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 3px;
        page-break-after: avoid;
      }

      h3 {
        font-size: 13.5px;
        font-weight: 600;
        color: #1e40af;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
      }

      h4 {
        font-size: 12.5px;
        font-weight: 600;
        color: #334155;
        margin-top: 10px;
        margin-bottom: 4px;
        page-break-after: avoid;
      }

      p, li {
        color: #334155;
      }

      ul, ol {
        padding-left: 20px;
        margin-top: 3px;
        margin-bottom: 6px;
      }

      li {
        margin-bottom: 2px;
      }

      table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 11.5px;
        page-break-inside: avoid;
      }

      th, td {
        border: 1px solid #cbd5e1;
        padding: 5px 8px;
        text-align: left;
      }

      th {
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: 600;
      }

      tr:nth-child(even) {
        background-color: #f8fafc;
      }

      pre {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 8px 10px;
        border-radius: 5px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        overflow-x: auto;
        margin: 6px 0;
        page-break-inside: avoid;
        border: 1px solid #334155;
      }

      code {
        font-family: 'JetBrains Mono', monospace;
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 1px 3px;
        border-radius: 3px;
        font-size: 11px;
        border: 1px solid #e2e8f0;
      }

      pre code {
        background: transparent;
        color: inherit;
        padding: 0;
        border: none;
      }

      blockquote {
        border-left: 4px solid #2563eb;
        background-color: #eff6ff;
        padding: 6px 10px;
        margin: 8px 0;
        border-radius: 0 5px 5px 0;
        color: #1e3a8a;
      }

      img {
        max-width: 92%;
        max-height: 250px;
        height: auto;
        display: block;
        margin: 8px auto 3px auto;
        border-radius: 5px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        page-break-inside: avoid;
      }

      em {
        display: block;
        text-align: center;
        font-size: 10.5px;
        color: #64748b;
        margin-bottom: 8px;
        page-break-before: avoid;
      }

      hr {
        border: 0;
        border-top: 1px solid #e2e8f0;
        margin: 14px 0;
      }

      .task-list-item {
        list-style-type: none;
      }
      .task-list-item input {
        margin-right: 5px;
      }
    """

    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Trabajo Práctico 1: Despliegue en un VPS</title>
<style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(full_html)

    # 4. Eliminar PDFs previos para evitar falsos positivos
    for p in [target_pdf, submission_pdf]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception as e:
                print(f'[ADVERTENCIA] No se pudo borrar archivo previo {p}: {e}')

    # 5. Localizar binario de Chrome / Edge
    chrome_candidates = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
    ]
    chrome_path = None
    for c in chrome_candidates:
        if os.path.exists(c):
            chrome_path = c
            break

    if not chrome_path:
        raise RuntimeError('No se encontró ejecutable de Google Chrome o Microsoft Edge.')

    # 6. Ejecutar Chrome Headless con RUTA ABSOLUTA en --print-to-pdf
    abs_temp_html = os.path.abspath(temp_html).replace('\\', '/')
    abs_target_pdf = os.path.abspath(target_pdf).replace('/', '\\')

    cmd = [
        chrome_path,
        '--headless=new',
        '--disable-gpu',
        '--allow-file-access-from-files',
        '--virtual-time-budget=5000',
        '--no-pdf-header-footer',
        f'--print-to-pdf={abs_target_pdf}',
        f'file:///{abs_temp_html}'
    ]

    print(f'[INFO] Renderizando con: {chrome_path}')
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.stderr:
        print(f'[STDERR RENDERER] {res.stderr.strip()}')

    # 7. Validar la existencia y contenido real del PDF generado
    if not os.path.exists(target_pdf):
        raise RuntimeError(f'Fallo crítico: El PDF {target_pdf} no fue generado por Chrome.')

    pdf_size = os.path.getsize(target_pdf)
    print(f'[ÉXITO] {target_pdf} generado correctamente ({pdf_size} bytes).')

    # 8. Auditoría interna con pypdf para verificar que las imágenes están incrustadas
    reader = pypdf.PdfReader(target_pdf)
    total_pages = len(reader.pages)
    total_imgs_in_pdf = sum(len(page.images) for page in reader.pages)
    print(f'[AUDITORÍA PDF] Total de páginas: {total_pages} | Total de imágenes incrustadas: {total_imgs_in_pdf}')

    for idx, page in enumerate(reader.pages):
        if len(page.images) > 0:
            print(f'   -> Página {idx+1}: {len(page.images)} imagen(es) detectada(s)')

    # 9. Copiar a la versión con nombre oficial de entrega
    shutil.copy2(target_pdf, submission_pdf)
    print(f'[ÉXITO] Archivo de entrega {submission_pdf} creado y validado.')

    # 10. Limpieza de archivo temporal
    if os.path.exists(temp_html):
        os.remove(temp_html)

if __name__ == '__main__':
    generate()
