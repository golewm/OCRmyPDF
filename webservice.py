from flask import Flask, request, send_file, render_template_string
import tempfile, os, ocrmypdf

app = Flask(__name__)

@app.route('/', methods=['POST'])
def ocr_pdf():
    f = request.files.get('file')
    if not f:
        return "Missing file", 400

    with tempfile.TemporaryDirectory() as tmp:
        ext = os.path.splitext(f.filename)[1] or ".pdf"
        inpath = os.path.join(tmp, f"in{ext}")
        outpath = os.path.join(tmp, "out.pdf")
        f.save(inpath)

        # Optionen aus Query-Parametern
        force = request.args.get('force') == '1'
        pdfa = request.args.get('pdfa') == '1'
        mode = request.args.get('mode')
        rotate = request.args.get('rotate') == '1'
        deskew = request.args.get('deskew') == '1'
        bg = request.args.get('bg') == '1'
        clean = request.args.get('clean') == '1'
        oem = int(request.args.get('oem', 2))

        kwargs = {}
        kwargs["image_dpi"] = 300
        kwargs["tesseract_oem"] = oem

        if force:
            kwargs["force_ocr"] = True
        else:
            kwargs["redo_ocr"] = True
        if not pdfa:
            kwargs["output_type"] = "pdf"
        if mode == "chaotic":
            kwargs["tesseract_pagesegmode"] = 11
        if rotate:
            kwargs["rotate_pages"] = True
        if deskew:
            kwargs["deskew"] = True
        if bg:
            kwargs["remove_background"] = True
        if clean:
            kwargs["clean"] = True

        ocrmypdf.ocr(inpath, outpath, **kwargs)

        return send_file(
            outpath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="output.pdf"
        )

@app.route('/docs', methods=['GET'])
def docs():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OCR API Dokumentation</title>
        <style>
            body { font-family: sans-serif; margin: 40px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; }
            th { background: #eee; }
            code { background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>📄 OCR API Dokumentation</h1>
        <p>POST-Anfrage an <code>/</code> mit einem PDF oder Bild als Datei-Upload.</p>

        <h2>🔧 Query-Parameter</h2>
        <table>
            <tr><th>Parameter</th><th>Beschreibung</th><th>Typ / Wert</th></tr>
            <tr><td><code>force</code></td><td>Immer OCR ausführen</td><td><code>1</code></td></tr>
            <tr><td><code>pdfa</code></td><td>PDF/A erzeugen</td><td><code>1</code></td></tr>
            <tr><td><code>mode</code></td><td>Seitenlayout-Modus (PSM 11)</td><td><code>chaotic</code></td></tr>
            <tr><td><code>rotate</code></td><td>Seiten automatisch drehen</td><td><code>1</code></td></tr>
            <tr><td><code>deskew</code></td><td>Begradigung schiefer Seiten</td><td><code>1</code></td></tr>
            <tr><td><code>bg</code></td><td>Hintergrund entfernen</td><td><code>1</code></td></tr>
            <tr><td><code>clean</code></td><td>Störungen und Kanten entfernen</td><td><code>1</code></td></tr>
            <tr><td><code>oem</code></td><td>Tesseract OCR Engine Mode</td><td><code>0</code> bis <code>3</code> (Standard = 2)</td></tr>
        </table>

        <h2>🧪 Beispielaufruf (cURL)</h2>
        <pre><code>
curl -X POST "http://host:5000/?force=1&mode=chaotic" \
     -F "file=@test.pdf" \
     --output output.pdf
        </code></pre>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
