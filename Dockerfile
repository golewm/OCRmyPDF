FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    tesseract-ocr \
    tesseract-ocr-deu \
    qpdf \
    unpaper \
  && curl -LO https://ftp.debian.org/debian/pool/main/g/ghostscript/ghostscript_10.05.1~dfsg-1_i386.deb \
  && apt-get install -y ./ghostscript_10.05.1~dfsg-1_amd64.deb \
  && rm ghostscript_10.05.1~dfsg-1_amd64.deb \
  && pip install ocrmypdf flask \
  && rm -rf /var/lib/apt/lists/*

COPY webservice.py /webservice.py

CMD ["python", "/webservice.py"]
