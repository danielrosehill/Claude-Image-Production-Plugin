---
name: pdf-extract-embedded-images
description: Extract embedded JPEG and PNG images from a PDF at their native resolution, without rasterizing. Use when a PDF is primarily a wrapper around photos or images and you want to recover them at full quality without the page rendering overhead.
disable-model-invocation: false
allowed-tools: Bash(pdfimages *), Bash(ls *), Bash(mkdir *), Read, Write
---

# Extract Embedded Images from PDF

Pull out JPEG and PNG objects embedded in a PDF using `pdfimages`. Extracts at native resolution without rasterizing the page. Different from `pdf-to-images` — this recovers the original embedded image files, not a rasterized page render.

## When to use

- A PDF is a container for photos (e.g., a photo book or brochure) — you want the original images, not a rasterized version.
- Bulk-extracting image assets from a multi-page document without re-encoding.
- Recovering embedded images at their full embedded resolution and quality.

## Inputs to gather

- **Input PDF file** — path to the PDF. Required.
- **Output directory** — optional. Default: current directory.

## Procedure

### 1. Check tooling

```bash
command -v pdfimages || echo "pdfimages not installed — install with: sudo apt install poppler-utils"
```

Abort if missing.

### 2. Validate PDF and inspect contents

```bash
file "<input.pdf>"
pdfimages -list "<input.pdf>"
```

The `-list` flag shows a summary of embedded images: page number, index, width, height, bits per component, color space, encoding. This helps set expectations (e.g., "3 JPEG images at 2400×3000px").

### 3. Extract

```bash
pdfimages -all "<input.pdf>" "<output-prefix>"
```

The `-all` flag extracts both the raw image stream (if JPEG, as `.jpg`; if PNG, as `.png`, etc.) plus any alternate-format versions.

**Alternatives:**

- `-j` — extract JPEG objects only (faster if there are many PNG/PNG variants).
- `-png` — convert all images to PNG (may re-encode non-JPEG content; slower but lossy compression converted to lossless).

Recommend `-all` unless the user specifies otherwise.

### 4. Report

After extraction:

- Count of images extracted, by type (JPEG, PNG, etc.).
- Output filenames and their dimensions.
- File sizes and whether any extraction failed.
- Remind the user that embedded images may have compression applied by the PDF creator — they are not necessarily at absolute maximum quality, but they are at their native resolution.

## Output / side effects

- Image files created with names like `prefix-000.jpg`, `prefix-001.png`, etc. (depends on PDF content).
- Original PDF unchanged.

## Notes

- **Native resolution, not PDF rendering resolution:** `pdfimages` extracts the raw embedded objects at the resolution they were embedded, not the page rendering resolution. For a photo book PDF with 2400×3000px JPEGs embedded, you get those 2400×3000px files directly — much faster and lossless compared to rasterizing the 8.5"×11" page at 300 DPI.
- **Lossy source warning:** Even though `pdfimages` does not re-encode, the original embedded images may already be JPEG-compressed by the PDF creator. You cannot recover quality that was lost before embedding. Check output sizes and quality to verify.
- **PNG and other formats:** `pdfimages` preserves PNG, TIFF, and other formats within the PDF. The `-all` flag ensures you get them all. The `-png` flag is useful if you want everything as PNG but will re-encode and potentially change file size.
- **Naming collision:** If multiple images have the same name, `pdfimages` appends sequential suffixes (e.g., `prefix-000.jpg`, `prefix-001.jpg`). No files are overwritten.
- Depends: `apt install poppler-utils`.
