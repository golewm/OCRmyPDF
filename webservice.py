from flask import Flask, request, send_file, Response
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

        # --- URL-Parameter auslesen -----------------------------------------
        force  = request.args.get('force') == '1'
        pdfa   = request.args.get('pdfa')  == '1'
        lang   = request.args.get('lang')  or "eng"
        oem    = int(request.args.get('oem', 1))           # 0–3 (Std. 1=LSTM)
        mode   = request.args.get('mode') or ""            # z. B. chaotic
        rotate = request.args.get('rotate') == '1'
        deskew = request.args.get('deskew') == '1'
        bg     = request.args.get('bg')     == '1'
        clean  = request.args.get('clean')  == '1'

        psm_map = {"chaotic": 11}
        psm = psm_map.get(mode)

        # --- OCR-Optionen zusammenstellen -----------------------------------
        kwargs = {
            "image_dpi": 300,
            "language":  lang,
            "tesseract_oem": oem
        }
        if psm is not None:
            kwargs["tesseract_pagesegmode"] = psm
        if rotate:
            kwargs["rotate_pages"] = True
        if deskew:
            kwargs["deskew"] = True
        if bg:
            kwargs["remove_background"] = True
        if clean:
            kwargs["clean"] = True

        kwargs["force_ocr" if force else "redo_ocr"] = True
        if not pdfa:
            kwargs["output_type"] = "pdf"

        # --- OCR ausführen ---------------------------------------------------
        ocrmypdf.ocr(inpath, outpath, **kwargs)

        return send_file(
            outpath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="output.pdf"
        )

# --------------------------------------------------------------------------- #
#                              Dokumentations-Seite                           #
# --------------------------------------------------------------------------- #
@app.route('/docs', methods=['GET'])
def show_docs():
    html = """
    <!DOCTYPE html>
    <html><head>
        <meta charset="utf-8">
        <title>OCR Webservice – API&nbsp;Docs</title>
        <style>
            body{font-family:Arial,Helvetica,sans-serif;margin:40px;max-width:900px}
            table{border-collapse:collapse;width:100%;margin:20px 0}
            th,td{border:1px solid #ccc;padding:8px}
            th{background:#eee}
            code{background:#f4f4f4;padding:2px 4px;border-radius:4px}
            h1,h2{color:#333;margin-top:30px}
            pre{background:#f4f4f4;padding:12px;border-radius:6px;overflow-x:auto}
        </style>
    </head><body>
        <h1>OCR Webservice – API Dokumentation</h1>

        <p>
            <strong>Endpoint:</strong> <code>POST /</code> (Multipart-Upload).<br>
            Datei im Formularfeld <code>file</code> (PDF, JPG, PNG, TIFF).<br>
            Rückgabe: durchsuchbares PDF (oder PDF/A).
        </p>

        <h2>URL-Parameter &nbsp;(alle optional)</h2>
        <table>
            <tr><th>Parameter</th><th>Typ /Werte</th><th>Standard</th><th>Beschreibung</th></tr>

            <tr><td><code>force</code></td>
                <td><code>1</code></td><td><em>0</em></td>
                <td>OCR erzwingen, auch wenn Text vorhanden ist</td></tr>

            <tr><td><code>pdfa</code></td>
                <td><code>1</code></td><td><em>0</em></td>
                <td>Ergebnis als PDF/A (benötigt Ghostscript &gt;=10.03)</td></tr>

            <tr><td><code>lang</code></td>
                <td>ISO-639-3 Codes (kommagetrennt)<br><small>z.&nbsp;B. <code>deu+eng</code></small></td>
                <td><code>eng</code></td>
                <td>OCR-Sprache(n)</td></tr>

            <tr><td><code>oem</code></td>
                <td>
                    0 = Legacy+LSTM<br>
                    1 = LSTM-only (empfohlen)<br>
                    2 = Legacy-only<br>
                    3 = Auto
                </td>
                <td><code>1</code></td>
                <td>Tesseract-Engine-Modus</td></tr>

            <tr><td><code>mode</code></td>
                <td><code>chaotic</code> (→ PSM 11)</td>
                <td>–</td>
                <td>Schnelle Layout-Voreinstellung<br>(<em>Sparse Text</em>)</td></tr>

            <tr><td><code>rotate</code></td>
                <td><code>1</code></td><td><em>0</em></td>
                <td>Seiten automatisch ausrichten (Drehen)</td></tr>

            <tr><td><code>deskew</code></td>
                <td><code>1</code></td><td><em>0</em></td>
                <td>Schiefe Seiten begradigen</td></tr>

            <tr><td><code>bg</code></td>
                <td><code>1</code></td><td><em>0</em></td>
                <td>Hintergrund/Schmutz entfernen</td></tr>

            <tr><td><code>clean</code></td>
                <td><code>1</code></td><td><em>0</em></td>
                <td>Scan-Artefakte reduzieren (Unpaper-Cleanup)</td></tr>
        </table>

        <h2>Beispiel – Standard</h2>
<pre><code>curl -X POST -F "file=@scan.pdf" http://host:5000/ --output result.pdf</code></pre>

        <h2>Beispiel – Chaotisches Layout &amp; Deutsch</h2>
<pre><code>curl -X POST \\
     "http://host:5000/?force=1&mode=chaotic&lang=deu" \\
     -F "file=@foto.jpg" --output ocr.pdf
</code></pre>
    </body></html>
    """
    return Response(html, mimetype='text/html')

# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
