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

        # === Parameter auslesen ===
        force = request.args.get('force') == '1'
        pdfa = request.args.get('pdfa') == '1'
        lang = request.args.get('lang') or "eng"
        oem = request.args.get('oem') or "1"  # Standard: LSTM only
        mode = request.args.get('mode') or ""

        # === PSM-Modi ===
        psm_map = {
            "chaotic": "11",  # sparse text
        }
        psm = psm_map.get(mode, None)

        kwargs = {
            "image_dpi": 300,
            "language": lang,
            "tesseract_config": ["--oem", str(oem)]
        }

        if psm:
            kwargs["tesseract_config"].extend(["--psm", psm])

        if force:
            kwargs["force_ocr"] = True
        else:
            kwargs["redo_ocr"] = True

        if not pdfa:
            kwargs["output_type"] = "pdf"

        ocrmypdf.ocr(inpath, outpath, **kwargs)

        return send_file(
            outpath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="output.pdf"
        )


@app.route('/docs', methods=['GET'])
def show_docs():
    html = """
    <html>
    <head><title>OCR API – Dokumentation</title></head>
    <body>
        <h1>OCR API – Dokumentation</h1>
        <p>Sende eine <strong>POST-Anfrage</strong> an <code>/</code> mit einem PDF- oder Bild-File als <code>file</code>.</p>
        <h2>Optionale URL-Parameter:</h2>
        <ul>
            <li><code>?force=1</code> → Erzwinge OCR, auch wenn Text vorhanden ist</li>
            <li><code>?pdfa=1</code> → PDF/A-Ausgabe (Standard ist normales PDF)</li>
            <li><code>?lang=deu</code> → Sprache für OCR (Standard: <code>eng</code>)</li>
            <li><code>?oem=1</code> → OCR-Modus (0=Legacy, 1=LSTM-only (Standard), 2=Legacy+LSTM, 3=Auto)</li>
            <li><code>?mode=chaotic</code> → Setzt <code>--psm 11</code> für unstrukturiertes Layout</li>
        </ul>
        <h2>Beispiel (curl):</h2>
        <pre>
curl -X POST -F 'file=@test.pdf' "http://localhost:5000?force=1&lang=deu&mode=chaotic" --output result.pdf
        </pre>
    </body>
    </html>
    """
    return Response(html, mimetype='text/html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
