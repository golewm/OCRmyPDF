from flask import Flask, request, send_file, Response
import tempfile, os, ocrmypdf

app = Flask(__name__)

@app.route('/', methods=['POST'])
def ocr_pdf():
    # ---------- Datei holen ----------
    f = request.files.get('file')
    if not f:
        return "Missing file", 400

    with tempfile.TemporaryDirectory() as tmp:
        ext = os.path.splitext(f.filename)[1] or ".pdf"
        inpath = os.path.join(tmp, f"in{ext}")
        outpath = os.path.join(tmp, "out.pdf")
        f.save(inpath)

        # ---------- URL-Parameter ----------
        force  = request.args.get('force') == '1'
        pdfa   = request.args.get('pdfa')  == '1'
        lang   = request.args.get('lang')  or "deu"       # Standard jetzt DE
        oem    = int(request.args.get('oem', 1))          # 0–3, default 1
        mode   = request.args.get('mode') or ""
        psm_q  = request.args.get('psm')                  # numerischer PSM
        rotate = request.args.get('rotate') == '1'
        deskew = request.args.get('deskew') == '1'
        bg     = request.args.get('bg')     == '1'
        clean  = request.args.get('clean')  == '1'
        wl     = request.args.get('wl')                    # Whitelist

        psm_map = {"chaotic": 11}
        psm = int(psm_q) if psm_q is not None else psm_map.get(mode)

        # ---------- OCR-Optionen ----------
        kwargs = {
            "image_dpi": 300,
            "language":  lang,
            "tesseract_oem": oem
        }
        if psm is not None:
            kwargs["tesseract_pagesegmode"] = psm
        if wl:
            kwargs.setdefault("tesseract_config", []).extend(
                ["-c", f"tessedit_char_whitelist={wl}"]
            )
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

        # ---------- OCR ausführen ----------
        ocrmypdf.ocr(inpath, outpath, **kwargs)

        # ---------- Ergebnis senden ----------
        return send_file(
            outpath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="output.pdf"
        )

# ---------------------------------------------------------------------------
#                                 Dokumentation
# ---------------------------------------------------------------------------
@app.route('/docs', methods=['GET'])
def show_docs():
    html = """
<!DOCTYPE html><html><head><meta charset="utf-8"><title>OCR Webservice – API Docs</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:40px;max-width:900px}
table{border-collapse:collapse;width:100%;margin:20px 0}
th,td{border:1px solid #ccc;padding:8px}th{background:#eee}
code{background:#f4f4f4;padding:2px 4px;border-radius:4px}
pre{background:#f4f4f4;padding:12px;border-radius:6px;overflow-x:auto}
</style></head><body>
<h1>OCR Webservice – API Dokumentation</h1>

<p><strong>Endpoint:</strong> <code>POST /</code><br>
Datei-Feld <code>file</code> (PDF, JPG, PNG, TIFF).<br>
Standard­sprache: <strong>Deutsch (deu)</strong>.</p>

<h2>Unterstützte Sprachen</h2>
<ul>
  <li><code>deu</code> – Deutsch (Standard)</li>
  <li><code>eng</code> – Englisch</li>
  <li><code>rus</code> – Russisch</li>
  <li>Kombiniert: z.&nbsp;B. <code>deu+eng</code></li>
</ul>

<h2>URL-Parameter</h2>
<table>
<tr><th>Param.</th><th>Werte</th><th>Default</th><th>Erklärung</th></tr>
<tr><td><code>force</code></td><td>1</td><td>0</td><td>OCR erzwingen</td></tr>
<tr><td><code>pdfa</code></td><td>1</td><td>0</td><td>PDF/A-Ausgabe</td></tr>
<tr><td><code>lang</code></td><td><em>s.o.</em></td><td><code>deu</code></td><td>OCR-Sprache(n)</td></tr>
<tr><td><code>oem</code></td><td>0–3</td><td>1</td><td>Tesseract-Engine-Modus</td></tr>
<tr><td><code>psm</code></td><td>0–13</td><td>–</td><td>Numerischer Page-Segmentation-Mode</td></tr>
<tr><td><code>mode</code></td><td><code>chaotic</code></td><td>–</td><td>Alias für PSM 11 (Sparse)</td></tr>
<tr><td><code>rotate</code></td><td>1</td><td>0</td><td>Seiten drehen</td></tr>
<tr><td><code>deskew</code></td><td>1</td><td>0</td><td>Schiefen Text begradigen</td></tr>
<tr><td><code>bg</code></td><td>1</td><td>0</td><td>Hintergrund entfernen</td></tr>
<tr><td><code>clean</code></td><td>1</td><td>0</td><td>Unpaper-Cleanup</td></tr>
<tr><td><code>wl</code></td><td>Zeichenliste</td><td>–</td><td>Whitelist, z.&nbsp;B. <code>/0123</code></td></tr>
</table>

<h2>Beispiele</h2>

<h3>1. Deutsches PDF (Standard)</h3>
<pre><code>curl -X POST -F "file=@rechnung.pdf" \\
     http://host:5000/ --output out.pdf
</code></pre>

<h3>2. Englisch + Russisch, PSM 6</h3>
<pre><code>curl -X POST -F "file=@scan.jpg" \\
     "http://host:5000/?lang=eng+rus&psm=6" \\
     --output ocr.pdf
</code></pre>

<h3>3. Chaotisches Layout, Whitelist für Slash &amp; Zahlen</h3>
<pre><code>curl -X POST -F "file=@foto.png" \\
     "http://host:5000/?mode=chaotic&force=1&wl=/0123456789" \\
     --output result.pdf
</code></pre>
</body></html>
"""
    return Response(html, mimetype='text/html')

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
