---
name: fast-thumbnail
description: Use when the user wants to generate thumbnails at scale — index views, contact sheets, web previews, or just shrinking a library to manageable sizes. Wraps `vipsthumbnail` for sub-second-per-image generation, much faster than ImageMagick on large batches.
---

# Fast Thumbnail (vipsthumbnail)

Generate thumbnails at high throughput using `vipsthumbnail`. Distinct from `fast-resize`: this is purpose-built for "make small previews of every image in this folder" workflows where output is always a downscale and quality is "good enough for a thumbnail".

## When to use

- Building a contact-sheet / web-gallery / index of an image library.
- Pre-rendering thumbnails for a UI / filesystem browser.
- Bulk-shrinking large originals to share / archive.

Do **not** use this skill when:
- The user wants the *same* size as the originals — that's a no-op.
- The user is upscaling — use `fast-resize` (or `upscale-image` for AI upscale).
- The user wants to keep original quality — this skill assumes lossy thumbnail-grade output.

## Inputs

1. **Input directory** — required.
2. **Size** — pixel size. Single number is shorthand for `NxN` (fit within square). Default: `512`.
3. **Output dir** — default: `<input>/thumbnails/`. The skill never overwrites originals.
4. **Format** — output format. Default: `jpg` (best size/quality balance for thumbs). Options: `jpg`, `png`, `webp`, `avif`.
5. **Quality** — JPEG/WebP/AVIF quality. Default: `80`.
6. **Recursive** — `--recursive` to descend. Mirrors subdirectory structure under the output dir.
7. **Naming** — default: same base name. `--prefix <s>` or `--suffix <s>` if collision is a risk.

## Procedure

1. Verify `vipsthumbnail` is on PATH. If missing, point at `install-deps`. No graceful fallback — if vips isn't installed, the skill's whole reason to exist is gone; tell the user to install or use `batch-resize`.

2. Enumerate input files (image extensions only).

3. For each file:

   ```bash
   vipsthumbnail "<input>" \
     --size "<size>" \
     --output "<output-dir>/<basename>.<ext>[Q=<quality>]"
   ```

   For non-JPEG outputs, the `[Q=N]` syntax still works for WebP/AVIF.

4. For very large batches, parallelise with `find ... | xargs -P <ncpu> -I{} vipsthumbnail ...`. vips is internally threaded but per-image work is small enough that process-level parallelism wins on >5k batches.

5. Track progress and skipped files (corrupt, wrong format).

## Output

- Thumbnails at `<output-dir>/`.
- Summary: `<n> thumbnails, <total-output-MB>MB, <elapsed-s>s, avg <ms>ms/image`.
- Failed files listed.

## Notes

- `vipsthumbnail` shrink-on-load: for JPEG sources, it decodes at the smallest DCT scale ≥ target — so generating a 256-px thumbnail from a 4000-px JPEG is *much* faster than full decode + resize. This is the headline reason to use it.
- Sharpen-on-shrink is on by default (vipsthumbnail applies a mild sharpen after downscale). Add `--no-rotate` and explicit `--linear` flags only if Daniel asks; the defaults are sensible for thumbnails.
- For contact-sheet *layout* (multiple thumbs into a grid image), this skill produces the inputs; combine with ImageMagick `montage` separately.
- ICC handling: vipsthumbnail strips ICC by default to keep file sizes small (right call for thumbs). If colour-accurate thumbs are needed, pass `--export-profile <path-to-srgb.icc>`.
