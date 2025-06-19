FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    ghostscript \
    qpdf \
    unpaper \
 && pip install "ocrmypdf[unpaper]" flask \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY webservice.py /webservice.py

CMD ["python", "/webservice.py"]
