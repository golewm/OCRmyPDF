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
        ocrmypdf.ocr(inpath, outpath, redo_ocr=True, output_type="pdf")
        return send_file(outpath, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
