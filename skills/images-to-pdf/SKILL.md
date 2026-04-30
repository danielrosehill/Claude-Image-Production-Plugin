---
name: images-to-pdf
description: Use when the user wants to combine a folder or list of images into a single PDF — typically on a standard paper size (A4 default) for digital printers, document-style sharing, or proof sheets. Modes - one-per-page (default; auto-orient portrait/landscape per image), multi-up (2/4/6/9 per page), as-is (native pixel size). Prefers `img2pdf` for lossless JPEG embedding; falls back to ImageMagick `convert` for non-JPEG sources or when img2pdf is missing.
---

# Images → PDF

Bundle images into a PDF with predictable paper-size and layout behaviour. Built for the recurring "I need to send this batch to a printer" workflow.

## When to use

- Preparing a photo set for a digital print shop (one-per-page on A4 / Letter).
- Building a proof sheet (multi-up).
- Sharing a document-style PDF (e.g. scanned receipts) without re-encoding.
- Bundling AI-generated images for client review.

Do **not** use this skill when:
- The user wants the PDF to also include text/markdown — that's a different workflow (typst / pandoc).
- The PDF needs OCR text layer — out of scope (run tesseract separately, then merge).
- A single image → PDF without paper-size constraints — `img2pdf <input> -o <output>.pdf` is enough; no skill needed.

## Inputs

1. **Inputs** — directory, glob, or explicit file list. Required.
2. **Output PDF path** — required.
3. **Paper size** — `A4` (default), `A3`, `A5`, `Letter`, `Legal`, `Tabloid`, or explicit `<W>x<H><unit>` (e.g. `210x297mm`, `8.5x11in`).
4. **Mode** — one of:
   - `one-per-page` (default) — one image per page, fitted to the paper with margins. Auto-rotates the page (portrait vs landscape) to match the image's aspect ratio.
   - `multi-up` — `2`, `4`, `6`, or `9` images per page (`--per-page N`). Grid layout, each cell sized equally, image fitted within cell.
   - `as-is` — native pixel dimensions become the page size (use for digital archives or when DPI metadata is authoritative).
5. **Margin** — millimetres. Default `10mm` (`one-per-page`), `5mm` per cell (`multi-up`), `0` (`as-is`).
6. **Sort order** — `filename` (default, natural sort), `exif-date` (capture time from EXIF), `mtime` (filesystem mtime).
7. **DPI** — assumed DPI for fit calculations when source has no DPI metadata. Default `300` (print-quality).
8. **Auto-orient** — default `on` for `one-per-page`. Rotates page (not image) to match aspect — landscape image gets a landscape page. Disable with `--no-auto-orient`.

## Procedure

1. Detect tool availability:
   - `which img2pdf` — preferred path.
   - `which magick || which convert` — fallback for cases img2pdf can't handle.
   - If neither exists, point at `install-deps`.

2. Enumerate inputs in the requested sort order (image extensions only: jpg, jpeg, png, webp, tiff, gif). Skip non-image files with a one-line note.

3. **Mode: `one-per-page` with img2pdf** — preferred path because img2pdf embeds JPEG bytes losslessly (no re-encode):

   ```bash
   img2pdf \
     --pagesize <paper-spec> \
     --imgsize <paper-minus-margins> \
     --fit into \
     --auto-orient \
     -o "<output>" \
     "<file1>" "<file2>" ...
   ```

   `--fit into` keeps aspect ratio, fits within page minus margins. `--auto-orient` rotates pages to match image aspect.

   img2pdf accepts JPEG, PNG, TIFF natively. For other formats (WebP, HEIC, AVIF), pre-convert to PNG via vipsthumbnail and stage in a temp directory; img2pdf will re-embed losslessly.

4. **Mode: `multi-up`** — img2pdf doesn't natively grid; build an intermediate composite per page using ImageMagick `montage`:

   ```bash
   # for each chunk of N files:
   montage <files> -tile <cols>x<rows> \
     -geometry <cell-w>x<cell-h>+<margin>+<margin> \
     -background white \
     "<staged>/page-<idx>.png"
   ```

   Then feed the staged page PNGs to img2pdf as `one-per-page` against the chosen paper size. Cell dimensions = `(paper-w - 2*outer-margin) / cols - cell-margin` and similar for height.

   Layout mapping: `--per-page 2` = 1×2 portrait or 2×1 landscape (orient by paper); `4` = 2×2; `6` = 2×3 (portrait) / 3×2 (landscape); `9` = 3×3.

5. **Mode: `as-is`** — straight pass-through:

   ```bash
   img2pdf -o "<output>" "<file1>" "<file2>" ...
   ```

   No `--pagesize` or `--imgsize`; img2pdf uses each image's native dimensions and DPI.

6. **ImageMagick fallback** (only if img2pdf is missing or chokes on a format):

   ```bash
   convert <files> \
     -page <paper-spec> \
     -gravity center \
     -extent <paper-spec> \
     -density <dpi> \
     -compress jpeg -quality 90 \
     "<output>"
   ```

   This re-encodes JPEGs (quality loss), so prefer img2pdf when possible. Surface a warning when falling back.

7. Verify output: `pdfinfo "<output>"` (if available) or check file is non-empty PDF magic. Report page count.

## Output

- The PDF at the resolved path.
- Summary: `<n> images → <output> (<pages> pages, <size-MB>MB)`.
- Mode used + tool used (img2pdf primary / ImageMagick fallback).
- List of any skipped or staged-via-conversion files.

## Notes

- `one-per-page` with auto-orient is the default because real-world prints want each photo at maximum size on the page regardless of original orientation. Disable for documents/contracts where every page must be uniform portrait.
- img2pdf is the right default: lossless JPEG embedding means the output PDF is essentially the JPEGs in a PDF wrapper — no quality loss, smallest possible file. ImageMagick re-encodes; only fall back when forced.
- For very large input sets (>200 images) ImageMagick `montage` becomes slow on multi-up mode — chunk and parallelise. For one-per-page mode, img2pdf handles thousands of pages without issue.
- Paper-size internals: A4 = 210×297mm, A3 = 297×420mm, A5 = 148×210mm, Letter = 8.5×11in (215.9×279.4mm), Legal = 8.5×14in, Tabloid = 11×17in.
- Print-shop-friendly defaults: A4, 10mm margin, 300 DPI assumption, auto-orient on. Override only with explicit reason.
- For mixed orientations in `as-is` mode without auto-orient, the resulting PDF will have heterogeneous page sizes — many printers handle this but some don't. Default to `one-per-page` with auto-orient for printer reliability.
