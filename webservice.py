from flask import Flask, request, send_file, jsonify
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
    return jsonify({
        "description": "OCR API mit Tesseract/LSTM über OCRmyPDF",
        "method": "POST",
        "content_type": "multipart/form-data",
        "file_field": "file (binär)",
        "query_parameters": {
            "force": "1 = immer OCR ausführen (auch wenn Text erkennbar ist)",
            "pdfa": "1 = PDF/A erzeugen, sonst Standard-PDF",
            "mode": "chaotic = Tesseract PSM 11 (Sparse Text Mode)",
            "rotate": "1 = Seiten automatisch drehen (wenn nötig)",
            "deskew": "1 = schiefe Seiten automatisch begradigen",
            "bg": "1 = Hintergrund entfernen",
            "clean": "1 = Artefakte/Kanten entfernen",
            "oem": "Tesseract-OCR Engine Mode (Standard = 2 = LSTM-only)"
        },
        "example_curl": "curl -X POST 'http://host:5000/?force=1&mode=chaotic' -F 'file=@scan.pdf' --output output.pdf"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
