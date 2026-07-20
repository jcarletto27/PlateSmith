# PlateSmith

PlateSmith is a browser-based generator for serial plates, equipment tags, and similar labels. It creates single-line vector text suitable for engraving, cutting, or marking workflows.

## Features

- Rectangular and circular plate layouts
- Live browser preview
- Adjustable dimensions and line thickness
- Optional plate outlines
- SVG, DXF, and PNG export
- Bulk SVG generation from CSV
- Built-in single-line font with no external font dependency

## Run with Docker

Requirements: Docker with Compose.

```sh
docker compose up --build
```

Open <http://localhost:5544>.

The project directory is mounted into the container, so source changes are available without rebuilding the image.

## Run locally

Requirements: Python 3.11 or later.

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>.

## Bulk generation

Upload a CSV file through the web interface. The first row is treated as a header. Each following row uses this format:

```csv
shape,dim1,dim2,line1,line2,line3,line4,line5
torus,35,23,SN-001,BATCH 4
rectangle,100,50,SN-002,BATCH 4,LINE 3
```

For a rectangle, `dim1` is width and `dim2` is height. For a torus, `dim1` is outer diameter and `dim2` is inner diameter. Dimensions are in millimetres.

Bulk generation returns a ZIP archive containing one SVG file per data row.

## Project structure

```text
app.py               Flask application and bulk SVG generator
templates/index.html Browser interface and client-side exporters
requirements.txt     Python dependencies
Dockerfile           Application image
compose.yml          Local container configuration
```

## License

No license has been specified.
