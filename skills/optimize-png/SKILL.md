---
name: optimize-png
description: Use when the user wants to shrink PNG files in a batch — losslessly with `oxipng` (typical 20–40% reduction, byte-identical decode) or aggressively with `pngquant` (lossy palette quantisation, 60–80% reduction with near-imperceptible quality loss for web use). Web-prep workhorse.
---

# Optimize PNG

Squeeze PNG file size. Two modes:

- **lossless** (default) — `oxipng`. Byte-identical decode. Always safe.
- **lossy** — `pngquant`. Palette-quantised; visible artefacts only on smooth gradients. Right call for web/UI assets.

## When to use

- Web-prep: PNG screenshots, UI assets, illustrations destined for upload.
- Archival: shave a few hundred MB off a folder of PNG masters losslessly.
- Pre-step inside `web-ready` orchestrator.

Do **not** use this skill when:
- Source is JPEG → use `optimize-jpeg`.
- Source is RAW/HEIC/TIFF → run `web-ready` end-to-end first.
- Quality must be bit-perfect for cryptographic hashing → only use `lossless` mode.

## Inputs

1. **Input** — file or directory. Required.
2. **Mode** — `lossless` (default) or `lossy`.
3. **Recursive** — `--recursive` for directory descent.
4. **In-place** — default. `--output-dir <path>` to write copies.
5. **Lossless level** (mode=lossless) — `oxipng -o <0..6>`. Default `4`. `6` is ~20% slower for ~1–2% extra compression.
6. **Lossy quality** (mode=lossy) — `pngquant --quality min-max`. Default `65-80` (web-good). Increase floor for sensitive material.
7. **Strip metadata** — default off. `--strip` removes EXIF/iTXt/zTXt/tIME chunks (oxipng `--strip safe`). Use when web-prep doesn't need camera info.

## Procedure

1. Verify the relevant binary exists. `which oxipng` for lossless; `which pngquant` for lossy. If missing, point at `install-deps`.

2. Enumerate inputs (PNG only — skip non-PNG with a one-line note).

3. **Lossless** (oxipng):

   ```bash
   oxipng -o <level> [--strip safe] [--out <out-dir>] "<input>"
   ```

   In-place is the default; pass `--out` only if `--output-dir` was set. `oxipng` is multithreaded by default — no need to xargs-parallelise.

4. **Lossy** (pngquant):

   ```bash
   pngquant --quality <min>-<max> --skip-if-larger --strip --output "<output>" "<input>"
   ```

   `--skip-if-larger` is critical — pngquant occasionally produces a larger file on already-quantised inputs; this prevents inflation.
   `--strip` removes optional chunks (default off in pngquant — explicitly enable for web-prep).

5. Track total before/after sizes; report the savings.

## Output

- Optimised PNG files at the resolved paths.
- Summary table:
  - Files processed / skipped / failed.
  - Total: `<orig-MB>` → `<new-MB>` (`<pct>%` saved).
  - Worst compressors (files with <5% savings) — flag for inspection.

## Notes

- `oxipng` lossless on a typical screenshot: 20–40% reduction. On already-optimised PNGs (e.g. via Photoshop "Save for Web"): often 1–5%.
- `pngquant` is irreversible. Keep originals if there's any chance the file will need further editing.
- For *animated* PNGs (APNG): both tools handle them but check output visually first.
- Combining lossy then lossless (`pngquant` → `oxipng`) gets a few extra % off — the orchestrator (`web-ready`) does this automatically; this skill keeps it as separate modes for explicit control.
