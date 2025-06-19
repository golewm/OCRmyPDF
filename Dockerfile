FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    ghostscript=9.55.0* \
    qpdf \
    unpaper \
  && pip install ocrmypdf flask

COPY webservice.py /webservice.py

CMD ["python", "/webservice.py"]
