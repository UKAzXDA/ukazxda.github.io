import base64
import io
import json
import os
import threading
import webbrowser

from flask import Flask, render_template_string, request, send_file
import pymupdf as fitz

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Editor — iOS Minimalist</title>
    <style>
        :root {
            --bg-color: #f5f5f7;
            --card-bg: #ffffff;
            --text-main: #1d1d1f;
            --text-secondary: #86868b;
            --accent: #0071e3;
            --accent-hover: #0077ed;
            --border: #e5e5ea;
            --radius-lg: 18px;
            --radius-md: 12px;
            --shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
        }

        * {
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }

        .app-container {
            width: 100%;
            max-width: 960px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.5px;
            margin: 0 0 8px 0;
        }

        .header p {
            color: var(--text-secondary);
            font-size: 15px;
            margin: 0;
        }

        .card {
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            padding: 20px 24px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.8);
            margin-bottom: 24px;
        }

        .upload-form {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }

        .file-drop {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 12px;
            background: #fafafa;
            border: 1.5px dashed var(--border);
            padding: 12px 20px;
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .file-drop:hover {
            border-color: var(--accent);
            background: #f0f7ff;
        }

        .file-drop input[type="file"] {
            display: none;
        }

        .file-label {
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .btn-primary {
            background: var(--accent);
            color: #ffffff;
            border: none;
            padding: 12px 24px;
            border-radius: var(--radius-md);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 113, 227, 0.25);
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-primary:hover {
            background: var(--accent-hover);
            transform: translateY(-1px);
        }

        .instruction-pill {
            background: rgba(0, 113, 227, 0.08);
            color: var(--accent);
            padding: 12px 20px;
            border-radius: var(--radius-md);
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 24px;
        }

        .pdf-page-wrapper {
            position: relative;
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            margin-bottom: 35px;
            overflow: hidden;
        }

        .pdf-page-img {
            width: 100%;
            height: auto;
            display: block;
        }

        .text-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }

        .editable-line {
            position: absolute;
            pointer-events: auto;
            white-space: nowrap;
            line-height: 1.0;
            outline: none;
            border-radius: 2px;
            transition: background 0.12s ease, box-shadow 0.12s ease;
            cursor: text;
            background: transparent;
        }

        .editable-line:hover {
            box-shadow: 0 0 0 1px var(--accent);
            background: rgba(0, 113, 227, 0.05);
            z-index: 10;
        }

        .editable-line:focus {
            background: #ffffff !important;
            box-shadow: 0 0 0 2px var(--accent), 0 4px 12px rgba(0,0,0,0.15);
            z-index: 20;
            padding: 0 3px;
        }

        .action-bar {
            position: sticky;
            bottom: 20px;
            z-index: 100;
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }

        .action-bar .btn-primary {
            padding: 14px 36px;
            font-size: 15px;
            border-radius: 30px;
            box-shadow: 0 10px 25px rgba(0, 113, 227, 0.35);
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <h1>Editor de PDF</h1>
            <p>Edição nativa contínua com impressão direta.</p>
        </div>

        <div class="card">
            <form action="/upload" method="post" enctype="multipart/form-data" class="upload-form">
                <label class="file-drop" for="pdf_file">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--accent);"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                    <span class="file-label" id="file-name-text">Escolha um arquivo PDF...</span>
                    <input type="file" name="pdf_file" id="pdf_file" accept=".pdf" required onchange="updateFileName(this)">
                </label>
                <button type="submit" class="btn-primary">Carregar PDF</button>
            </form>
        </div>

        {% if pages_data %}
        <div class="instruction-pill">
            ✨ <strong>Edição ativada:</strong> Clique em qualquer texto para alterar. Ao concluir, clique no botão para abrir e imprimir diretamente.
        </div>

        <form action="/save" method="post" id="export-form" target="_blank">
            <input type="hidden" name="pdf_filename" value="{{ pdf_filename }}">
            <input type="hidden" name="edits_json" id="edits_json">

            {% for page in pages_data %}
            <div class="pdf-page-wrapper">
                <img src="data:image/png;base64,{{ page.img_b64 }}" class="pdf-page-img" alt="Página {{ page.page_num + 1 }}">
                
                <div class="text-overlay" data-w="{{ page.width }}" data-h="{{ page.height }}">
                    {% for line in page.lines %}
                    <div contenteditable="true"
                         class="editable-line"
                         data-page="{{ page.page_num }}"
                         data-bbox='{{ line.bbox | tojson }}'
                         data-origin='{{ line.origin | tojson }}'
                         data-orig='{{ line.text | tojson }}'
                         data-size="{{ line.size }}"
                         data-color="{{ line.color }}"
                         data-flags="{{ line.flags }}"
                         data-font="{{ line.font }}"
                         style="left: {{ line.left_pct }}%; top: {{ line.top_pct }}%; color: {{ line.color }}; font-weight: {{ line.font_weight }}; font-style: {{ line.font_style }};">
                        {{- line.text -}}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}

            <div class="action-bar">
                <button type="submit" class="btn-primary">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                    Abrir e Imprimir PDF Editado
                </button>
            </div>
        </form>

        <script>
            function updateFileName(input) {
                const label = document.getElementById('file-name-text');
                if (input.files && input.files[0]) {
                    label.textContent = input.files[0].name;
                    label.style.color = 'var(--text-main)';
                }
            }

            function adjustFontSizes() {
                document.querySelectorAll('.text-overlay').forEach(overlay => {
                    const pageW = parseFloat(overlay.getAttribute('data-w'));
                    const currentW = overlay.clientWidth;
                    if (!pageW || !currentW) return;
                    const scale = currentW / pageW;

                    overlay.querySelectorAll('.editable-line').forEach(line => {
                        const origSize = parseFloat(line.getAttribute('data-size'));
                        line.style.fontSize = (origSize * scale) + 'px';
                    });
                });
            }

            window.addEventListener('resize', adjustFontSizes);
            document.addEventListener('DOMContentLoaded', adjustFontSizes);
            setTimeout(adjustFontSizes, 200);

            document.querySelectorAll('.editable-line').forEach(el => {
                el.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.blur();
                    }
                });
            });

            document.getElementById('export-form').onsubmit = function() {
                const allLines = [];
                document.querySelectorAll('.editable-line').forEach(lineDiv => {
                    let origText = "";
                    try {
                        origText = JSON.parse(lineDiv.getAttribute('data-orig'));
                    } catch(e) {
                        origText = lineDiv.getAttribute('data-orig') || "";
                    }

                    const currentText = (lineDiv.innerText || lineDiv.textContent || "").replace(/\\r?\\n|\\r/g, " ").trim();

                    allLines.push({
                        page: parseInt(lineDiv.getAttribute('data-page')),
                        bbox: JSON.parse(lineDiv.getAttribute('data-bbox')),
                        origin: JSON.parse(lineDiv.getAttribute('data-origin')),
                        orig: origText,
                        new: currentText,
                        size: parseFloat(lineDiv.getAttribute('data-size')),
                        color: lineDiv.getAttribute('data-color'),
                        flags: parseInt(lineDiv.getAttribute('data-flags') || '0'),
                        font: lineDiv.getAttribute('data-font') || ''
                    });
                });
                
                document.getElementById('edits_json').value = JSON.stringify(allLines);
            };
        </script>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, pages_data=None)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    file = request.files.get('pdf_file')
    if not file:
        return "Nenhum arquivo enviado", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    doc = fitz.open(filepath)
    pages_data = []

    for page_idx, page in enumerate(doc):
        rect = page.rect
        w, h = rect.width, rect.height

        text_page = page.get_text("dict")
        lines_list = []

        clean_doc = fitz.open()
        clean_page = clean_doc.new_page(width=w, height=h)
        clean_page.show_pdf_page(clean_page.rect, doc, page_idx)

        for block in text_page.get("blocks", []):
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue

                    line_text = "".join(s.get("text", "") for s in spans)
                    if not line_text.strip():
                        continue

                    line_bbox = line.get("bbox")
                    first_span = spans[0]
                    origin = first_span.get("origin", (line_bbox[0], line_bbox[3] - 2))
                    size = first_span.get("size", 11)
                    color_int = first_span.get("color", 0)
                    flags = first_span.get("flags", 0)
                    font_name = first_span.get("font", "")

                    redact_rect = fitz.Rect(line_bbox[0] - 1, line_bbox[1] - 1, line_bbox[2] + 1, line_bbox[3] + 1)
                    clean_page.add_redact_annot(redact_rect, fill=(1, 1, 1))

                    r = (color_int >> 16) & 255
                    g = (color_int >> 8) & 255
                    b = color_int & 255
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"

                    fn_lower = font_name.lower()
                    is_bold = bool(flags & 16) or ("bold" in fn_lower) or ("black" in fn_lower) or ("heavy" in fn_lower)
                    is_italic = bool(flags & 2) or ("italic" in fn_lower) or ("oblique" in fn_lower)

                    left_pct = (line_bbox[0] / w) * 100
                    top_pct = (line_bbox[1] / h) * 100

                    lines_list.append({
                        "bbox": line_bbox,
                        "origin": origin,
                        "text": line_text,
                        "size": round(size, 2),
                        "color": hex_color,
                        "flags": flags,
                        "font": font_name,
                        "font_weight": "bold" if is_bold else "normal",
                        "font_style": "italic" if is_italic else "normal",
                        "left_pct": round(left_pct, 4),
                        "top_pct": round(top_pct, 4)
                    })

        clean_page.apply_redactions()
        pix = clean_page.get_pixmap(dpi=150)
        img_b64 = base64.b64encode(pix.tobytes("png")).decode('utf-8')
        clean_doc.close()

        pages_data.append({
            "page_num": page_idx,
            "width": w,
            "height": h,
            "img_b64": img_b64,
            "lines": lines_list
        })

    doc.close()
    return render_template_string(HTML_TEMPLATE, pages_data=pages_data, pdf_filename=file.filename)


def get_best_pdf_font(font_name, flags):
    fn = font_name.lower()
    is_bold = bool(flags & 16) or ("bold" in fn) or ("black" in fn) or ("heavy" in fn)
    is_italic = bool(flags & 2) or ("italic" in fn) or ("oblique" in fn)

    if "times" in fn or "serif" in fn or "georgia" in fn or "roman" in fn:
        if is_bold and is_italic:
            return "tibi"
        elif is_bold:
            return "tibo"
        elif is_italic:
            return "tiit"
        else:
            return "times"
    elif "courier" in fn or "mono" in fn or "code" in fn or "console" in fn:
        if is_bold or is_italic:
            return "cobo"
        else:
            return "cour"
    else:
        if is_bold and is_italic:
            return "hebi"
        elif is_bold:
            return "hebo"
        elif is_italic:
            return "heit"
        else:
            return "helv"


def sanitize_for_pdf(text):
    if not text:
        return ""
    text = text.replace('\u00a0', ' ')
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace('…', '...')
    return text.strip()


@app.route('/save', methods=['POST'])
def save_pdf():
    filename = request.form.get('pdf_filename')
    edits_json = request.form.get('edits_json')
    all_lines = json.loads(edits_json) if edits_json else []

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    doc = fitz.open(filepath)

    changed_edits = []
    for line in all_lines:
        orig_clean = sanitize_for_pdf(line['orig'])
        new_clean = sanitize_for_pdf(line['new'])

        if orig_clean != new_clean:
            line['new_clean'] = new_clean
            changed_edits.append(line)

    edits_by_page = {}
    for edit in changed_edits:
        p = edit['page']
        if p not in edits_by_page:
            edits_by_page[p] = []
        edits_by_page[p].append(edit)

    for page_idx, page_edits in edits_by_page.items():
        page = doc[page_idx]

        for edit in page_edits:
            bbox = edit['bbox']
            clean_rect = fitz.Rect(bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2)
            page.add_redact_annot(clean_rect, fill=(1, 1, 1))

        page.apply_redactions()

        for edit in page_edits:
            new_text = edit['new_clean']
            if not new_text:
                continue

            origin = edit['origin']
            size = edit['size']
            flags = edit.get('flags', 0)
            font_name = edit.get('font', '')
            hex_color = edit['color'].lstrip('#')

            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
            else:
                r, g, b = 0.0, 0.0, 0.0

            pdf_font = get_best_pdf_font(font_name, flags)
            point = fitz.Point(origin[0], origin[1])

            page.insert_text(
                point,
                new_text,
                fontsize=size,
                color=(r, g, b),
                fontname=pdf_font
            )

    # Exporta os bytes do PDF em memória sem salvar no disco
    pdf_bytes = doc.tobytes()
    doc.close()

    # Retorna o arquivo inline para o navegador abrir diretamente no leitor de PDF
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=False
    )


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.2, open_browser).start()
    app.run(debug=True, port=5000)