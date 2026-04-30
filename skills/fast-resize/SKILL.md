---
name: fast-resize
description: Use when the user wants to resize a large batch of images (>500 files) where ImageMagick throughput is the bottleneck. Wraps libvips for 5–10× faster batch resize at lower memory. Falls back to ImageMagick if `vips` isn't installed. Same outputs as `batch-resize` — different engine.
---

# Fast Resize (libvips)

Batch image resize using libvips. Material throughput improvement over ImageMagick on large libraries — typical 5–10× speed-up and lower peak memory.

## When to use

- Batch is >500 images.
- The user is feeling ImageMagick's slowness (or is about to).
- The job is "resize this directory" — pure resize without compositing or filters.

Do **not** use this skill for:
- Small batches (<100 images) — `batch-resize` is fine, no point swapping engines.
- Resize-with-filter / resize-with-text / multi-op pipelines — ImageMagick is the better tool for compound work.

## Inputs

1. **Input directory** — required.
2. **Target size** — one of:
   - `--width N` — resize so width = N, height auto.
   - `--height N` — resize so height = N, width auto.
   - `--max NxM` — fit within NxM box (preserves aspect).
   - `--exact NxM` — force exact dimensions (may distort or crop).
3. **Output mode** — `in-place` (overwrite) or `--output-dir <path>` (default: `<input>/resized/`).
4. **Filter** — interpolation kernel: `lanczos3` (default — best quality), `cubic`, `linear`, `nearest`.
5. **Recursive** — `--recursive` to descend into subdirectories. Default: top-level only.
6. **Format preserve** — by default keeps source format. `--to <ext>` to change format on the way out.

## Procedure

1. Verify `vips` is on PATH. If missing, fall back to ImageMagick `convert` with the same parameters and warn that this will be slower (point at `install-deps`).

2. Enumerate input files (filter to image extensions: jpg, jpeg, png, webp, tiff, gif, heic, avif, jxl).

3. For each file, build the vips command. Two main forms:

   **Fit within box (preserves aspect):**
   ```bash
   vipsthumbnail "<input>" --size "<W>x<H>" --output "<output>[Q=85]"
   ```

   `vipsthumbnail` is the right tool for "resize down" — it's optimised for thumbnail-style ops and handles JPEG shrink-on-load (free 8× speedup for 1/8-size targets).

   **Exact resize via `vips`:**
   ```bash
   vips resize "<input>" "<output>" <scale-factor> --kernel <kernel>
   ```

   For `--width`/`--height`, compute scale = target / source. `vipsthumbnail` is preferred when shrinking; use `vips resize` when upscaling or when source dimensions vary widely.

4. Run in parallel where safe. vips is internally threaded; running multiple processes via xargs/parallel adds little. One process per CPU core is the sweet spot for large batches.

5. Report progress every N files (every 10% or every 100, whichever is more frequent).

## Output

- Resized images at the resolved output paths.
- Summary: `<n> files processed, <total-input-MB>MB → <total-output-MB>MB, <elapsed-s>s, avg <ms>ms/image`.
- List of any files that failed (corrupt, unsupported format, permission errors).
- If output-dir was used and any source files had identical names from different subdirectories without `--recursive` flattening logic, flag the collision.

## Notes

- `vipsthumbnail` accepts `[Q=N]` syntax for JPEG quality on output (default 75; 85 is a good balance).
- Wide colour gamut: vips preserves ICC profiles by default. If the user is processing display-P3 / Adobe RGB images, that's a feature.
- HEIC / AVIF / JXL: vips supports these if compiled with the right libs (apt's `libvips-tools` includes libheif and libjxl on recent Ubuntu).
- ImageMagick fallback path: if `vips` is missing, run `convert "<input>" -resize <WxH> "<output>"` per file. Same output, slower.
