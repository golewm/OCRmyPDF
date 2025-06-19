# OCR Flask Webservice

Ein schlanker OCR-Service mit OCRmyPDF und Flask.

## Starten mit Docker Compose

```bash
docker-compose up -d --build
```

## Testen

```bash
curl -X POST -F 'file=@test.pdf' http://localhost:5000/ --output result.pdf
```

## Integration in n8n

- HTTP POST Request an den OCR-Service
- Form-Data mit Schlüssel `file`
