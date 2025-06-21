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

        kwargs = {
            "image_dpi": 300,
            "tesseract_oem": oem,
        }

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
    <html>
    <head>
        <title>OCR-API Dokumentation</title>
        <style>
            body { font-family: sans-serif; padding: 2em; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 0.5em; }
            th { background-color: #f2f2f2; }
            code { background: #eee; padding: 0.2em; }
        </style>
    </head>
    <body>
        <h1>OCR Webservice API</h1>
        <p>Diese API verarbeitet PDF- oder Bilddateien und fügt erkannten Text hinzu.</p>

        <h2>Endpunkt</h2>
        <p><code>POST /</code> – Datei per <code>multipart/form-data</code> senden</p>

        <h2>Query-Parameter</h2>
        <table>
            <tr><th>Name</th><th>Beschreibung</th></tr>
            <tr><td><code>force=1</code></td><td>Immer OCR ausführen (auch wenn bereits Text vorhanden ist)</td></tr>
            <tr><td><code>pdfa=1</code></td><td>Erzeuge PDF/A statt normalem PDF</td></tr>
            <tr><td><code>mode=chaotic</code></td><td>Tesseract PSM 11 (Sparse Text Mode)</td></tr>
            <tr><td><code>rotate=1</code></td><td>Seiten automatisch drehen</td></tr>
            <tr><td><code>deskew=1</code></td><td>Schiefe Seiten begradigen</td></tr>
            <tr><td><code>bg=1</code></td><td>Hintergrund entfernen</td></tr>
            <tr><td><code>clean=1</code></td><td>Störende Ränder/Artefakte entfernen</td></tr>
            <tr><td><code>oem=2</code></td><td>Tesseract OCR Engine Mode (z. B. 1 = Legacy, 2 = LSTM)</td></tr>
        </table>

        <h2>Beispielaufruf (cURL)</h2>
        <pre>
curl -X POST "http://localhost:5000/?force=1&mode=chaotic" \\
     -F "file=@dokument.pdf" \\
     --output output.pdf
        </pre>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
