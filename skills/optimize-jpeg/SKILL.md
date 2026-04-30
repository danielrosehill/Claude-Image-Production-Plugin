---
name: optimize-jpeg
description: Use when the user wants to shrink JPEG files — losslessly with `jpegoptim` (~5–15% reduction, no re-encode) or with re-compression via `mozjpeg` (~10–15% better than libjpeg-turbo at the same visual quality). Web-prep workhorse for photo libraries.
---

# Optimize JPEG

Squeeze JPEG file size. Two modes:

- **lossless** (default) — `jpegoptim --strip-all`. Repacks Huffman tables and strips metadata. No re-encode, no quality change.
- **recompress** — `mozjpeg` (`cjpeg-mozjpeg`). Re-encodes with better quantisation tables; 10–15% smaller than libjpeg-turbo for the same SSIM. Quality flag controls trade-off.

## When to use

- Web-prep: photo galleries, blog images, anything destined for upload.
- Archive squeeze: lossless mode is the no-regret option for any JPEG-heavy folder.
- Pre-step inside `web-ready` orchestrator.

Do **not** use this skill when:
- Source is PNG → use `optimize-png`.
- Source is HEIC/RAW/TIFF — pipe through `web-ready` (or convert first).
- The JPEG is already heavily compressed (<70% quality estimate) — recompress will visibly degrade.

## Inputs

1. **Input** — file or directory. Required.
2. **Mode** — `lossless` (default) or `recompress`.
3. **Recursive** — `--recursive` for directory descent.
4. **In-place** — default. `--output-dir <path>` to write copies.
5. **Quality** (mode=recompress) — `cjpeg-mozjpeg -quality N`. Default `82` (web-quality). `90` for archival; `75` for aggressive web compression.
6. **Strip metadata** — default `on` for both modes. EXIF/IPTC/XMP gone. Use `--keep-metadata` to preserve.
7. **Progressive** — default `on`. Smaller files + better perceived load. `--baseline` to disable for compatibility with very old decoders.

## Procedure

1. Verify the relevant binary. `which jpegoptim` for lossless; `which cjpeg-mozjpeg` (or fallback `which cjpeg`) for recompress. If missing, point at `install-deps`.

2. Enumerate inputs (JPEG/JPG only — skip with note).

3. **Lossless** (jpegoptim):

   ```bash
   jpegoptim --strip-all --all-progressive [--dest <out-dir>] "<input>"
   ```

   `--all-progressive` forces progressive output (smaller). `--strip-all` removes EXIF/IPTC/XMP/comments. Drop these if `--keep-metadata` was set.

4. **Recompress** (mozjpeg):

   mozjpeg's CLI is decode-then-encode, so for in-place behaviour:

   ```bash
   djpeg "<input>" | cjpeg-mozjpeg -quality <q> -progressive [-optimize] > "<output>"
   ```

   Or use `jpegtran-mozjpeg` for lossless transforms when only metadata stripping + Huffman repack is desired (essentially a faster jpegoptim).

   For batch, parallelise with `xargs -P <ncpu>`.

5. Sanity-check: any output file >95% of input size in recompress mode — keep the original instead. cjpeg-mozjpeg occasionally inflates already-optimised inputs.

## Output

- Optimised JPEGs at the resolved paths.
- Summary:
  - Files processed / skipped / failed / kept-original (where recompress would have inflated).
  - Total: `<orig-MB>` → `<new-MB>` (`<pct>%` saved).
  - Visible-quality flag: if recompress was used and the source had a quality estimate <75 (via `identify -format "%Q"`), surface a warning per file.

## Notes

- mozjpeg is a drop-in libjpeg-turbo replacement with smarter trellis quantisation. It's slower than libjpeg-turbo by ~3× — fine for web-prep, not for thumbnail generation.
- For "I just want it smaller, don't touch quality": always use `lossless` mode. Free win.
- The orchestrator (`web-ready`) defaults to: resize first, then encode WebP/AVIF, fall back to mozjpeg for JPEG output. This skill exists to do JPEG-only optimisation without that pipeline.
