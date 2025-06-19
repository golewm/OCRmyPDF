from flask import Flask, request, send_file
import tempfile, os, ocrmypdf

app = Flask(__name__)

@app.route('/', methods=['POST'])
def ocr_pdf():
    f = request.files.get('file')
    if not f:
        return "Missing file", 400

    with tempfile.TemporaryDirectory() as tmp:
        inpath = os.path.join(tmp, "in.pdf")
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

        ocrmypdf.ocr(inpath, outpath, **kwargs)
        return send_file(outpath, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
