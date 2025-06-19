FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    ghostscript \
    tesseract-ocr \
    tesseract-ocr-deu \
    qpdf \
    unpaper \
    python3-pip \
 && pip3 install "ocrmypdf[unpaper]" flask \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY webservice.py /webservice.py

CMD ["python3", "/webservice.py"]
