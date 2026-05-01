---
name: auto-deskew
description: Use when the user wants to automatically straighten a tilted image — scanned documents, phone-captured pages, photographed receipts, or slightly off-axis photos. Detects the dominant skew angle and rotates the image to vertical/horizontal, optionally cropping the resulting transparent triangles. Uses ImageMagick `-deskew` for documents and a Hough-line fallback (via Python + OpenCV) for photographs.
---

# Auto Deskew

Straighten a tilted image. Two backends, picked by content type:

- **document** (default) — `magick -deskew 40%`. Detects skew via the Radon-style projection profile that ImageMagick's deskew operator implements. Fast, robust on text/scans up to ±15°.
- **photo** — Python + OpenCV Hough-line transform. Detects the dominant horizontal/vertical line angle (horizons, building edges, table corners) and rotates by its negative. Use for photographs without a clean text baseline.

## When to use

- Scanned documents that came in at an angle.
- Phone snapshots of pages, receipts, whiteboards.
- Slightly-tilted architectural / horizon photos (`--mode photo`).
- Pre-step before OCR — Tesseract accuracy degrades sharply past ±2° skew.

Do **not** use this skill when:
- The image is intentionally tilted (Dutch angle, artistic composition).
- Skew is severe (>15°) — usually means the document was captured upside down or sideways. Detect orientation first (`exiftool -Orientation`, or rotate by 90/180 multiples) before deskewing.
- The image has no straight reference lines (clouds, abstract textures) — Hough will return noise; rotation will be near-random.

## Inputs

1. **Input** — file or directory. Required.
2. **Mode** — `document` (default) | `photo` | `auto` (heuristic: if `magick identify -format "%[colorspace]"` is `Gray` or the image has very low saturation → `document`; else `photo`).
3. **Recursive** — `--recursive` for directory descent.
4. **Output** — default in-place suffix `_deskew`. `--output-dir <path>` for sibling folder. `--overwrite` to replace.
5. **Threshold** (mode=document) — `-deskew` percentage. Default `40%` (ImageMagick's recommended value). Higher = more aggressive detection, more false positives.
6. **Max angle** — default `15°`. If detected skew exceeds this, refuse to rotate and flag the file (probably wrong orientation, not skew).
7. **Crop** — default `on`. After rotation, crop to the largest inscribed rectangle so there are no transparent / black triangle borders. `--no-crop` to keep the full rotated canvas.
8. **Background** — fill colour for the post-rotation triangles when `--no-crop`. Default `white`. Use `none` for transparent (PNG/WebP only).

## Procedure

1. Verify ImageMagick 7+. For `photo` mode, also verify the plugin's uv venv has `opencv-python-headless` and `numpy` (managed by `install-deps`; if missing, point at it).

2. Enumerate inputs (JPEG/JPG/PNG/TIFF/TIF/WebP). Skip and note RAW.

3. **document** mode:

   ```bash
   magick "$IN" -background "$BG" -deskew ${THRESHOLD}% \
     $( [ "$CROP" = on ] && echo "+repage -fuzz 1% -trim +repage" ) \
     "$OUT"
   ```

   `-deskew` applies the rotation. `-trim` with a small fuzz removes the resulting fill border when `CROP=on`. Read back the applied angle from the verbose output (`-verbose`) for the summary.

4. **photo** mode (Python via the plugin's uv venv):

   ```python
   import cv2, numpy as np, sys
   img = cv2.imread(sys.argv[1])
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   edges = cv2.Canny(gray, 50, 150, apertureSize=3)
   lines = cv2.HoughLines(edges, 1, np.pi/720, 200)
   if lines is None:
       print("0.0"); sys.exit(0)
   # Collect angles near horizontal (±30°) and near vertical (±30° of 90°)
   angles = []
   for rho, theta in lines[:200, 0]:
       deg = np.degrees(theta) - 90  # 0 = horizontal line
       if abs(deg) < 30:
           angles.append(deg)
       elif abs(deg - 90) < 30:
           angles.append(deg - 90)
       elif abs(deg + 90) < 30:
           angles.append(deg + 90)
   if not angles:
       print("0.0"); sys.exit(0)
   print(f"{np.median(angles):.3f}")
   ```

   Then rotate via ImageMagick using the detected angle:

   ```bash
   ANGLE=$(uv run --project "$PLUGIN_VENV" python deskew_photo.py "$IN")
   magick "$IN" -background "$BG" -rotate "$(awk "BEGIN{print -1*$ANGLE}")" \
     $( [ "$CROP" = on ] && echo "+repage -fuzz 1% -trim +repage" ) \
     "$OUT"
   ```

5. **Max-angle guard**: if `|angle| > MAX_ANGLE`, skip the file and flag it: `"$IN: detected ${angle}° — exceeds max-angle ${MAX_ANGLE}°, skipping (likely wrong orientation, not skew)"`.

6. **Crop to inscribed rectangle** (when `--no-crop` is off and the simple `-trim` leaves uneven borders): use the analytic formula for the largest inscribed axis-aligned rectangle inside a rotated rectangle. For input `W×H` rotated by `θ`:

   ```
   new_w = (W·|cos θ| - H·|sin θ|) / (cos²θ - sin²θ)   if W ≥ H
   new_h = (H·|cos θ| - W·|sin θ|) / (cos²θ - sin²θ)
   ```

   Crop centred. For small angles (<5°) the difference vs. `-trim` is negligible — `-trim` is fine.

7. For batch, parallelise with `xargs -P $(nproc)`. Skip files ending `_deskew`.

## Output

- Deskewed images at the resolved paths.
- Summary:
  - Files processed / skipped (RAW or non-image) / failed / unchanged (|angle| < 0.1°) / refused (|angle| > max).
  - Per-mode count when mixed.
  - Distribution of detected angles (min / median / max) — sanity check across the batch.

## Notes

- ImageMagick's `-deskew` is tuned for bilevel/grayscale text. On colour photos it often returns 0° or noise — that's why `photo` mode exists.
- For OCR pipelines: deskew before binarisation. After deskew, `magick "$IN" -threshold 50%` or hand off to `tesseract` directly.
- If you want both content types handled in one run: `--mode auto`. The heuristic isn't perfect — review the angle distribution in the summary and re-run misclassified files explicitly.
- This skill rotates only. For perspective correction (four-corner unwarping of a photographed document), use a dedicated tool like `dewarp` or OpenCV's `getPerspectiveTransform` — auto-deskew won't fix keystoning.
