FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl tesseract-ocr tesseract-ocr-deu qpdf unpaper \
    && curl -LO http://security.ubuntu.com/ubuntu/pool/main/g/ghostscript/ghostscript_9.56.1~dfsg-1ubuntu1_amd64.deb \
    && apt-get install -y ./ghostscript_9.56.1~dfsg-1ubuntu1_amd64.deb \
    && pip install "ocrmypdf[unpaper]" flask \
    && rm -rf /var/lib/apt/lists/* *.deb

COPY webservice.py /webservice.py

CMD ["python", "/webservice.py"]
