---
name: pdf-to-images
description: Rasterize PDF pages to numbered image files (JPEG, PNG, or TIFF) at a specified resolution (DPI). Use when you need to convert PDF content to standalone images — one image per page — with optional page range selection.
disable-model-invocation: false
allowed-tools: Bash(pdftoppm *), Bash(ls *), Bash(mkdir *), Read, Write
---

# Rasterize PDF to Images

Convert PDF pages to raster images (JPEG, PNG, or TIFF) using `pdftoppm`. Each page becomes a numbered image file. Different from `pdf-extract-embedded-images` — this rasterizes the entire page content.

## When to use

- Converting a scanned PDF or document PDF to standalone images for archival, editing, or distribution.
- Extracting pages as thumbnails or preview images at lower DPI.
- Creating image sequences from a multi-page PDF without needing OCR or text extraction.

## Inputs to gather

- **Input PDF file** — path to the PDF. Required.
- **DPI (resolution)** — dots per inch. Default: 300 (suitable for archival and print). Ask if the user needs lower DPI for faster processing or smaller file size (e.g., 150 for thumbnails, 600 for high-quality scans).
- **Output format** — `jpeg`, `png`, or `tiff`. Default: `jpeg` (good balance of size and quality). PNG for lossless, TIFF for archival.
- **Page range** (optional) — ask if they want all pages or a subset. If a subset, capture start page and end page (e.g., pages 5–10).
- **Output directory** — optional. Default: current directory.

## Procedure

### 1. Check tooling

```bash
command -v pdftoppm || echo "pdftoppm not installed — install with: sudo apt install poppler-utils"
```

Abort if missing.

### 2. Validate PDF

```bash
file "<input.pdf>"
pdfinfo "<input.pdf>"  # shows page count, dimensions, etc.
```

If invalid, abort. Print page count for user awareness.

### 3. Build command

Base command:

```bash
pdftoppm -r <DPI> -<format> "<input.pdf>" "<output-prefix>"
```

**Examples:**

- All pages, JPEG at 300 DPI: `pdftoppm -r 300 -jpeg input.pdf output_`
- Pages 5–10, PNG at 150 DPI: `pdftoppm -r 150 -png -f 5 -l 10 input.pdf output_`
- All pages, TIFF at 600 DPI: `pdftoppm -r 600 -tiff input.pdf output_`

Flags:
- `-r <DPI>` — resolution in DPI.
- `-<format>` — output format: `jpeg`, `png`, `tiff`.
- `-f <N>` — first page (optional).
- `-l <N>` — last page (optional).

### 4. Execute

```bash
pdftoppm -r <DPI> -<format> <page-flags> "<input.pdf>" "<output-prefix>"
```

Show progress and warn if the PDF is large (many pages or high DPI — processing may take a minute or more).

### 5. Report

After conversion:

- Count of images created.
- Output directory and filename pattern (e.g., `output_001.jpg`, `output_002.jpg`, ...).
- File sizes and total space used.
- If a page range was used, note which pages were extracted.

## Output / side effects

- Numbered image files created (e.g., `prefix-000001.png`). Naming convention depends on pdftoppm version; typically zero-padded 6-digit page numbers.
- Original PDF unchanged.

## Notes

- **Rasterization vs. embedding:** `pdftoppm` rasterizes the entire page at the specified DPI. This is lossy compared to the original PDF vector content, but suitable for archival, sharing, or thumbnail workflows. See `pdf-extract-embedded-images` for extracting embedded photos without rasterization.
- **DPI guidance:** 300 DPI is standard for documents and photos. 150 DPI is adequate for thumbnails or web preview. 600 DPI or higher for fine scanning or print-quality archival.
- **Format choice:** JPEG for smaller files (good for photos within PDFs). PNG for lossless (documents with text). TIFF for professional archival (larger files, lossless, can embed metadata).
- **Large PDFs:** Page rasterization is I/O and CPU intensive. A 100-page PDF at 300 DPI can take 1–2 minutes. Warn the user before starting large jobs.
- Depends: `apt install poppler-utils`.
