from flask import Flask, request, send_file, Response
import tempfile, os, ocrmypdf

app = Flask(__name__)

@app.route('/', methods=['POST'])
def ocr_pdf():
    # ---------- Datei einlesen ----------
    f = request.files.get('file')
    if not f:
        return "Missing file", 400

    with tempfile.TemporaryDirectory() as tmp:
        ext = os.path.splitext(f.filename)[1] or ".pdf"
        inpath = os.path.join(tmp, f"in{ext}")
        outpath = os.path.join(tmp, "out.pdf")
        f.save(inpath)

        # ---------- Query-Parameter auswerten ----------
        force  = request.args.get('force') == '1'
        pdfa   = request.args.get('pdfa')  == '1'
        lang   = request.args.get('lang')  or "eng"
        oem    = int(request.args.get('oem', 1))         # Standard LSTM-only
        mode   = request.args.get('mode') or ""

        psm_map = {"chaotic": 11}                         # Sparse-Text-Modus
        psm = psm_map.get(mode)

        # ---------- OCR-Optionen zusammenstellen ----------
        kwargs = {
            "image_dpi": 300,
            "language":  lang,
            "tesseract_oem": oem
        }
        if psm is not None:
            kwargs["tesseract_pagesegmode"] = psm

        kwargs["force_ocr" if force else "redo_ocr"] = True
        if not pdfa:
            kwargs["output_type"] = "pdf"

        # ---------- OCR ausführen ----------
        ocrmypdf.ocr(inpath, outpath, **kwargs)

        # ---------- Ergebnis senden ----------
        return send_file(
            outpath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="output.pdf"
        )

# ---------- HTML-Dokumentation ----------
@app.route('/docs', methods=['GET'])
def show_docs():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OCR API – Dokumentation</title>
        <style>
            body{font-family:Arial,Helvetica,sans-serif;margin:40px}table{border-collapse:collapse}th,td{border:1px solid #ccc;padding:8px}
            th{background:#eee}code{background:#f4f4f4;padding:2px 4px;border-radius:4px}
        </style>
    </head>
    <body>
        <h1>OCR API – Dokumentation</h1>
        <p><strong>POST</strong> an <code>/</code> mit Datei-Feld <code>file</code> (PDF/Bild). Rückgabe: durchsuchbares PDF.</p>
        <h2>Parameter</h2>
        <table>
            <tr><th>Parameter</th><th>Beschreibung</th><th>Beispiel</th></tr>
            <tr><td><code>force</code></td><td>OCR immer erzwingen</td><td><code>?force=1</code></td></tr>
            <tr><td><code>pdfa</code></td><td>PDF/A erzeugen</td><td><code>?pdfa=1</code></td></tr>
            <tr><td><code>lang</code></td><td>OCR-Sprache (ISO-639-3)</td><td><code>?lang=deu</code></td></tr>
            <tr><td><code>oem</code></td><td>Tesseract-OEM (0–3, Standard 1=LSTM)</td><td><code>?oem=2</code></td></tr>
            <tr><td><code>mode</code></td><td><code>chaotic</code> → PSM 11 (Sparse)</td><td><code>?mode=chaotic</code></td></tr>
        </table>
        <h2>Beispiel (cURL)</h2>
<pre><code>curl -X POST -F "file=@scan.jpg" \\
     "http://host:5000/?force=1&mode=chaotic&lang=deu" \\
     --output result.pdf</code></pre>
    </body>
    </html>
    """
    return Response(html, mimetype='text/html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
