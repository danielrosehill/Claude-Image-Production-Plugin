---
name: convert-to-avif
description: Use when the user wants AVIF output — modern web format with ~30% better compression than WebP at the same visual quality, and ~50% better than JPEG. Wraps `avifenc`. Companion to `convert-to-webp`. Best target for new web work; check browser support if delivering to ancient clients.
---

# Convert to AVIF

Encode JPEG/PNG/TIFF to AVIF. AVIF beats WebP on compression ratio and supports 10/12-bit, HDR, and lossless modes. Browser support is universal as of 2024 (Chrome 85+, Firefox 113+, Safari 16.4+).

## When to use

- Web-prep where modern browser support is fine.
- Archival of high-bit-depth photos (10/12-bit AVIF preserves more than JPEG).
- Pre-step inside `web-ready` orchestrator.

Do **not** use this skill when:
- Output must work in Safari <16.4 / IE / very old Android browsers — fall back to WebP or JPEG.
- Source is already AVIF — no point re-encoding.
- You need lossless re-encoding of a JPEG that should remain bit-exact-decodable — that's `convert-to-jxl`'s unique trick, not AVIF's.

## Inputs

1. **Input** — file or directory. Required.
2. **Quality** — `avifenc -q N` (0–100). Default `60` (visually equivalent to JPEG q82, much smaller). `80` for archival; `45` for aggressive.
3. **Speed/effort** — `avifenc -s <0..10>`. Default `6` (balanced). `0` is best compression but very slow; `10` is fast but bigger files.
4. **Lossless** — `--lossless`. Enables lossless mode (ignores quality). For exact archival of PNG.
5. **Bit depth** — `--depth 8|10|12`. Default `8`. Use `10` for HDR or 16-bit source.
6. **Output dir** — default: `<input-dir>/avif/`. Skill never overwrites originals.
7. **Recursive** — `--recursive` for directory descent.
8. **Preserve EXIF** — default off (web-prep assumption). `--keep-exif` to copy EXIF over via `exiftool`.

## Procedure

1. Verify `avifenc` is on PATH. If missing, point at `install-deps`.

2. Enumerate inputs (jpg, jpeg, png, tiff — skip others with note).

3. For each file:

   ```bash
   avifenc -q <quality> -s <speed> [--lossless] [--depth <n>] "<input>" "<output>"
   ```

   Per-file. avifenc is single-threaded per encode but accepts `--jobs N` for tile-parallel — useful on large images. For batch parallelism, use `xargs -P <ncpu>`.

4. If `--keep-exif` was set, post-process:

   ```bash
   exiftool -tagsfromfile "<input>" -all:all "<output>" -overwrite_original
   ```

5. Track size deltas.

## Output

- AVIF files at `<output-dir>/`.
- Summary:
  - Files processed / failed.
  - Total: `<orig-MB>` → `<new-MB>` (`<pct>%` saved).
  - Quality estimate per file (using `--qcolor` if requested).

## Notes

- AVIF encoding is *slow* compared to JPEG/WebP. Speed `6` is ~2–4× slower than `cwebp`. Speed `0` can be 30× slower. Pick `6` unless archiving.
- `--speed 6 --quality 60` is the de facto web-prep default — quality matches q82 JPEG at roughly half the bytes.
- Animation: avifenc supports animated AVIF from PNG sequences (`avifenc -i input1.png -i input2.png ...`) but this skill focuses on still images.
- Decode support outside browsers is uneven (older image viewers may not decode). Check before mass-converting an archive.
- For *guaranteed* lossless re-encode of a JPEG (bit-exact reversible), use `convert-to-jxl` instead — JXL has a unique lossless-JPEG mode.
