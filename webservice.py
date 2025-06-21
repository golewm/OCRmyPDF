from flask import Flask, request, send_file, Response
import tempfile, os, ocrmypdf

app = Flask(__name__)

# ---------------------------------------------------------------------------
#  OCR-Endpunkt
# ---------------------------------------------------------------------------
@app.route('/', methods=['POST'])
def ocr_pdf():
    # Datei prüfen -----------------------------------------------------------
    f = request.files.get('file')
    if not f:
        return "Missing file", 400

    # Temporäre Pfade anlegen ------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        ext      = os.path.splitext(f.filename)[1] or ".pdf"
        inpath   = os.path.join(tmp, f"in{ext}")
        outpath  = os.path.join(tmp, "out.pdf")
        f.save(inpath)

        # ---------------- URL-Parameter auswerten ---------------------------
        force  = request.args.get('force')  == '1'          # OCR erzwingen
        pdfa   = request.args.get('pdfa')   == '1'          # PDF/A
        lang   = request.args.get('lang')   or "deu"        # Sprache(n)
        oem    = int(request.args.get('oem', 1))            # 0-3, Std 1
        mode   = request.args.get('mode')   or ""           # Alias für PSM
        psm_q  = request.args.get('psm')                    # numerischer PSM
        rotate = request.args.get('rotate') == '1'          # Auto-Rotate
        deskew = request.args.get('deskew') == '1'          # Begradigen
        bg     = request.args.get('bg')     == '1'          # BG-Entfernung
        clean  = request.args.get('clean')  == '1'          # Unpaper-Clean
        wl     = request.args.get('wl')                     # Whitelist

        # Alias-Mapping für PSM-Namen → Nummer
        psm_alias = {"chaotic": 11}
        psm = int(psm_q) if psm_q is not None else psm_alias.get(mode)

        # ---------------- OCR-Argumente zusammenstellen ---------------------
        kwargs = {
            "image_dpi": 300,              # generische DPI bei Bildern
            "language":  lang,
            "tesseract_oem": oem
        }
        if psm is not None:
            kwargs["tesseract_pagesegmode"] = psm
        if wl:
            # Zeichen-Whitelist an Tesseract übergeben
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

        # ---------------- OCR ausführen -------------------------------------
        ocrmypdf.ocr(inpath, outpath, **kwargs)

        # ---------------- Ergebnis zurückgeben ------------------------------
        return send_file(
            outpath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="output.pdf"
        )

# ---------------------------------------------------------------------------
#  HTML-Dokumentation
# ---------------------------------------------------------------------------
@app.route('/docs', methods=['GET'])
def docs():
    html = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<title>OCR Webservice – API-Dokumentation</title>
<style>
 body{font-family:Arial,Helvetica,sans-serif;margin:40px;max-width:1000px}
 table{border-collapse:collapse;width:100%;margin:20px 0}
 th,td{border:1px solid #ccc;padding:8px}th{background:#eee}
 code{background:#f4f4f4;padding:2px 4px;border-radius:4px}
 pre{background:#f4f4f4;padding:12px;border-radius:6px;overflow-x:auto}
</style></head><body>

<h1>OCR Webservice – API-Dokumentation</h1>
<p>
<strong>Endpoint:</strong> <code>POST /</code><br>
Upload-Feld <code>file</code> (PDF / Bild). Rückgabe: durchsuchbares PDF.<br>
<em>Standards:</em> Sprache = Deutsch (<code>deu</code>), OEM = 1 (LSTM-only).
</p>

<h2>Optionen</h2>
<table>
  <tr>
    <th>Parameter</th>
    <th>Standardwert</th>
    <th>Beschreibung</th>
    <th>Mögliche&nbsp;Werte</th>
  </tr>

  <tr>
    <td><code>force</code></td>
    <td>0</td>
    <td>OCR erzwingen, auch wenn das PDF bereits Textebenen enthält.</td>
    <td><code>1</code></td>
  </tr>

  <tr>
    <td><code>pdfa</code></td>
    <td>0</td>
    <td>Ergebnis als PDF/A (benötigt Ghostscript ≥ 10.03).</td>
    <td><code>1</code></td>
  </tr>

  <tr>
    <td><code>lang</code></td>
    <td><code>deu</code></td>
    <td>Tesseract-Sprachmodelle für die Erkennung.</td>
    <td><code>deu</code>, <code>eng</code>, <code>rus</code>, Kombination z.&nbsp;B. <code>deu+eng</code></td>
  </tr>

  <tr>
    <td><code>oem</code></td>
    <td>1</td>
    <td>Wählt die Tesseract-Engine. '1' Liefert meist beste Resultate <br>
    <code>0</code> Legacy+LSTM<br>
    <code>1</code> LSTM-only<br>
    <code>2</code> Auto<br>
    </td>
  </tr>

<tr>
  <td><code>psm</code></td>
  <td>–</td>
  <td>Page-Segmentation-Mode.</td>
  <td>
    <code>0</code> Nur Ausrichtung + Schrifterkennung (OSD)<br>
    <code>1</code> Automatische Segmentierung mit OSD<br>
    <code>2</code> Automatische Segmentierung, ohne OSD/OCR (nicht implementiert)<br>
    <code>3</code> Vollautomatische Segmentierung, ohne OSD&nbsp;(Voreinstellung)<br>
    <code>4</code> Eine Spalte Text variabler Größen<br>
    <code>5</code> Ein gleichförmiger Block vertikal ausgerichteten Textes<br>
    <code>6</code> Ein gleichförmiger Textblock<br>
    <code>7</code> Eine einzige Textzeile<br>
    <code>8</code> Ein einzelnes Wort<br>
    <code>9</code> Ein einzelnes Wort im Kreis<br>
    <code>10</code> Ein einzelnes Zeichen<br>
    <code>11</code> Spärlicher Text – so viel wie möglich, beliebige Reihenfolge<br>
    <code>12</code> Spärlicher Text mit OSD<br>
    <code>13</code> Rohzeile – eine Textzeile ohne Tesseract-spezifische Tricks
  </td>
</tr>

  <tr>
    <td><code>mode</code></td>
    <td>–</td>
    <td>Kurzname – setzt intern <code>psm=11</code> (Sparse-Text-Modus).</td>
    <td><code>chaotic</code></td>
  </tr>

  <tr>
    <td><code>rotate</code></td>
    <td>0</td>
    <td>Dreht Seiten automatisch, falls Kopf/Fuß vertauscht.</td>
    <td><code>1</code></td>
  </tr>

  <tr>
    <td><code>deskew</code></td>
    <td>0</td>
    <td>Begradigt schräg eingescannten Text.</td>
    <td><code>1</code></td>
  </tr>

  <tr>
    <td><code>bg</code></td>
    <td>0</td>
    <td>Entfernt graue Hintergrundschleier (typisch bei Kopien).</td>
    <td><code>1</code></td>
  </tr>

  <tr>
    <td><code>clean</code></td>
    <td>0</td>
    <td>Unpaper-Cleanup: entfernt Flecken/Ränder (nur für Bilder relevant).</td>
    <td><code>1</code></td>
  </tr>

  <tr>
    <td><code>wl</code></td>
    <td>–</td>
    <td>Whitelist – Tesseract erkennt ausschließlich diese Zeichen.</td>
    <td>Zeichenliste, z.&nbsp;B. <code>/0123456789</code></td>
  </tr>
</table>

<h2>Beispiele</h2>

<h3>1 · Standard (Deutsch)</h3>
<pre><code>curl -X POST -F "file=@dokument.pdf" http://host:5000/ --output out.pdf</code></pre>

<h3>2 · Englisch + Russisch, PSM 6 (ein Block Text)</h3>
<pre><code>curl -X POST \\
     -F "file=@scan.jpg" \\
     "http://host:5000/?lang=eng+rus&psm=6" \\
     --output result.pdf</code></pre>

<h3>3 · Chaotisches Layout, OCR erzwingen, Slash-Whitelist</h3>
<pre><code>curl -X POST -F "file=@foto.png" \\
     "http://host:5000/?force=1&mode=chaotic&wl=/0123456789" \\
     --output ocr.pdf</code></pre>

</body></html>
"""
    return Response(html, mimetype='text/html')

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
