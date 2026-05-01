---
name: auto-white-balance
description: Use when the user wants to automatically correct the white balance of an image (or batch) — neutralise colour casts from indoor lighting, mixed light, underwater shots, scans, or uncalibrated cameras. Implements gray-world (default), white-patch (per-channel auto-level), and a combined mode via ImageMagick. Operates on JPEG/PNG/TIFF/WebP; for RAW use `darktable-cli` instead.
---

# Auto White Balance

Neutralise colour casts without per-image manual correction. Three algorithms, one CLI.

- **gray-world** (default) — assume the average of the scene is neutral grey. Scale each RGB channel so its mean equals the global mean. Robust on most natural scenes.
- **white-patch** — assume the brightest pixels are white. Per-channel `-auto-level` stretches each channel to full range. Strong correction; fails on scenes lacking a true white reference.
- **combined** — gray-world first, then a gentle white-patch pass at 50% strength. Good default for mixed-light indoor shots.

## When to use

- Indoor photos under tungsten/fluorescent/LED with the wrong WB preset.
- Scanned prints / slides with age-related cast.
- Underwater or aquarium shots (heavy blue/green cast).
- Batch normalisation before publishing a gallery shot across multiple lighting conditions.

Do **not** use this skill when:
- Source is a RAW file (CR2/NEF/ARW/DNG/RAF) — use `darktable-cli` with `--apply-custom-presets` and the `temperature` module set to `as shot to reference`. White-balancing a baked JPEG throws away headroom that's still in the RAW.
- The cast is intentional (golden hour, sodium streetlamps for mood, blue-hour landscapes). Auto-WB will flatten it.
- The image is a deliberately monochromatic / toned edit.

## Inputs

1. **Input** — file or directory. Required.
2. **Mode** — `gray-world` (default) | `white-patch` | `combined`.
3. **Recursive** — `--recursive` for directory descent.
4. **Output** — default in-place suffix `_wb` next to the source. `--output-dir <path>` to write into a sibling folder. `--overwrite` to replace.
5. **Strength** — `0.0` to `1.0` (default `1.0`). Blends the corrected image with the original via `-compose blend -define compose:args=<pct>`. Use `0.5` for a softer touch.
6. **Preserve luminance** — default `on`. After channel scaling, rescale so the mean luminance matches the original (prevents brightness drift). `--no-preserve-luma` to disable.

## Procedure

1. Verify ImageMagick 7+. `magick -version | head -1`. Fall back to `convert` (IM6) if `magick` is missing — the syntax below works on both with the leading binary swapped. If neither, point at `install-deps`.

2. Enumerate inputs. Accept JPEG/JPG/PNG/TIFF/TIF/WebP. Skip and note RAW formats.

3. **gray-world**:

   ```bash
   magick "$IN" \
     -colorspace sRGB \
     -channel R -evaluate multiply $(magick "$IN" -colorspace sRGB -format "%[fx:mean/mean.r]" info:) \
     -channel G -evaluate multiply $(magick "$IN" -colorspace sRGB -format "%[fx:mean/mean.g]" info:) \
     -channel B -evaluate multiply $(magick "$IN" -colorspace sRGB -format "%[fx:mean/mean.b]" info:) \
     +channel "$OUT"
   ```

   Each `fx:mean/mean.<c>` is the gain that drives that channel's mean to the global mean. Three `info:` calls is wasteful for batch — cache via a single `magick identify -format "%[fx:mean] %[fx:mean.r] %[fx:mean.g] %[fx:mean.b]" "$IN"` and compute gains in shell.

4. **white-patch**:

   ```bash
   magick "$IN" -channel RGB -auto-level +channel "$OUT"
   ```

   Independent per-channel histogram stretch to `[0,1]`. Aggressive; clips highlights if any channel already saturates.

5. **combined**:

   Run gray-world to a temp file, then:

   ```bash
   magick "$TMP" \( +clone -channel RGB -auto-level +channel \) \
     -compose blend -define compose:args=50 -composite "$OUT"
   ```

6. **Preserve luminance** (when enabled): after step 3/4/5, measure luminance before and after and rescale:

   ```bash
   L_IN=$(magick "$IN"  -colorspace Gray -format "%[fx:mean]" info:)
   L_OUT=$(magick "$WB" -colorspace Gray -format "%[fx:mean]" info:)
   GAIN=$(awk "BEGIN{print $L_IN/$L_OUT}")
   magick "$WB" -evaluate multiply "$GAIN" "$OUT"
   ```

7. **Strength blend** (when `<1.0`):

   ```bash
   magick "$IN" "$WB" -compose blend -define compose:args=$(awk "BEGIN{print $STRENGTH*100}") -composite "$OUT"
   ```

8. For batch, parallelise with `xargs -P $(nproc)` over the file list. Skip files that already end in `_wb` to avoid recursive re-processing.

## Output

- Corrected images at the resolved paths.
- Summary:
  - Files processed / skipped (RAW or non-image) / failed.
  - Per-mode count when mixed.
  - Average per-channel gain across the batch (sanity check — if R-gain ≈ G-gain ≈ B-gain ≈ 1.0, the batch had no cast and the run was a no-op).

## Notes

- Gray-world fails on scenes dominated by one colour (snow, foliage, red brick wall). For those, `white-patch` is more honest, or skip auto-WB entirely and use a colour picker on a known-neutral patch.
- For batch mixed-lighting normalisation, run `combined` at `--strength 0.7` — strong enough to neutralise obvious casts, weak enough to preserve scene character.
- Output colour profile: ImageMagick respects the input ICC profile. If the source has no profile, it's treated as sRGB. Use `-profile sRGB.icc` explicitly if the pipeline downstream is profile-strict.
- This skill is the single-image / batch primitive. The orchestrator `apply-filters` may call it as one step; this skill exists to do WB-only work without the rest of the pipeline.
