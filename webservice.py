from flask import Flask, request, send_file
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

        # Optionale Parameter
        force = request.args.get('force') == '1'
        pdfa = request.args.get('pdfa') == '1'

        kwargs = {}
        if force:
            kwargs["force_ocr"] = True
        else:
            kwargs["redo_ocr"] = True
        if not pdfa:
            kwargs["output_type"] = "pdf"

        ocrmypdf.ocr(inpath, outpath, image_dpi=300, **kwargs)
        return send_file(outpath, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
