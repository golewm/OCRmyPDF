FROM python:3.11-slim

# Install stable Ghostscript 9.56.1 (Jammy), nicht Bookworm-Fehlerversion!
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates \
    && echo "deb http://archive.ubuntu.com/ubuntu jammy main" > /etc/apt/sources.list.d/jammy.list \
    && apt-get update && apt-get install -y \
    ghostscript=9.56.1~dfsg-1ubuntu1 \
    tesseract-ocr \
    tesseract-ocr-deu \
    qpdf \
    unpaper \
    && pip install "ocrmypdf[unpaper]" flask \
    && rm -rf /var/lib/apt/lists/*

COPY webservice.py /webservice.py

CMD ["python", "/webservice.py"]
