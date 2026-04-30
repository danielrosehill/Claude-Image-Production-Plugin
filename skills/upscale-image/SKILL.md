---
name: upscale-image
description: Use when the user wants to AI-upscale images 2× / 3× / 4× — recovering detail in low-res sources, prepping small photos for print, enlarging AI-generated images. Wraps `upscayl-bin` (the CLI bundled with Upscayl) with its model library; falls back to standalone `realesrgan-ncnn-vulkan` if Upscayl isn't installed. GPU-accelerated via Vulkan.
---

# Upscale Image (Upscayl)

AI upscaling via `upscayl-bin` — the CLI shipped with the Upscayl GUI. Same Vulkan-accelerated `realesrgan-ncnn-vulkan` engine as standalone, but with Upscayl's curated model selection bundled.

## When to use

- Low-res source needs to be enlarged for print or display.
- AI-generated image at 1024px wants 4096px output without re-prompting.
- Old photos / screenshots need detail recovery.

Do **not** use this skill when:
- The source is already large enough — upscaling rarely improves a 4K-native image.
- The user wants traditional bicubic / lanczos upscaling — `fast-resize` is the right tool (much faster, no AI).
- The image is text/document-heavy — upscalers can hallucinate glyph detail; consider `tesseract` re-OCR + re-typeset instead.

## Inputs

1. **Input** — file or directory. Required.
2. **Scale** — `2`, `3`, or `4` (Upscayl's bundled models are 4× natively; 2× and 3× are produced by post-resize). Default `4`.
3. **Model** — one of:
   - `upscayl-standard-4x` (default — best general-purpose photo upscaler).
   - `upscayl-lite-4x` (faster, lower quality, good for batches).
   - `realesrgan-x4plus` (classic, slightly different texture handling).
   - `realesrgan-x4plus-anime` (illustrations, line art, anime).
   - `remacri-4x` / `ultramix-balanced-4x` (alternative photo models if installed).
   - Or `--model-path <dir> --model-name <name>` to point at a custom model.
4. **Output dir** — default: `<input-dir>/upscaled/`. Skill never overwrites originals.
5. **Output format** — default `png` (lossless preserves the upscale fidelity). `jpg` option for size-sensitive batches (uses quality 92).
6. **Recursive** — `--recursive` for directory descent.
7. **GPU** — default auto-detect. `--gpu <n>` to pick a specific GPU. `--cpu` to force CPU (slow — only for headless boxes).

## Procedure

1. Locate the binary. Check in order:
   - `which upscayl-bin`
   - `/opt/Upscayl/resources/bin/upscayl-bin`
   - `~/.var/app/org.upscayl.Upscayl/data/bin/upscayl-bin` (Flatpak)
   - `which realesrgan-ncnn-vulkan` (fallback — same syntax, smaller model selection)

   If none found, point the user at `install-deps` (Upscayl install instructions: <https://upscayl.org>).

2. Locate the models directory. For upscayl-bin, typically:
   - `/opt/Upscayl/resources/models/`
   - `~/.var/app/org.upscayl.Upscayl/data/models/`
   - User-custom dir at `~/.config/Upscayl/models/`

   For standalone realesrgan-ncnn-vulkan, models are alongside the binary or in `./models/`.

   Verify the requested model exists in the resolved dir (each model is a `.param` + `.bin` pair).

3. Enumerate inputs (image extensions only).

4. For each file:

   ```bash
   <binary> \
     -i "<input>" \
     -o "<output>.png" \
     -s 4 \
     -m "<models-dir>" \
     -n "<model>"
   ```

   The `-s` flag is fixed at the model's native scale (almost always 4). For non-4× output:

   - **Scale 2 or 3:** run 4× upscale, then post-resize down via `vipsthumbnail` to `(orig × scale)` dimensions:
     ```bash
     vipsthumbnail "<intermediate-4x.png>" --size "<target-w>x<target-h>" \
       --output "<final>.<ext>[Q=92]"
     ```
   - **Scale 4 native:** the upscaler output is final.

5. **Output format conversion** if `--output-format jpg`:

   ```bash
   cjpeg-mozjpeg -quality 92 -progressive < "<output>.png" > "<output>.jpg"
   rm "<output>.png"
   ```

6. **Sequential, not parallel.** Vulkan GPU is single-resource — running multiple upscales concurrently doesn't help and may OOM the GPU on large images. Run one at a time.

7. **Memory awareness.** For very large inputs (>4000px on the long side), the Vulkan tile size matters. Default is fine; if the binary reports OOM, retry with `-t 100` (smaller tile = less VRAM, slightly slower). Surface this to the user rather than silently failing.

## Output

- Upscaled images at `<output-dir>/`.
- Summary:
  - Files processed / failed.
  - Per-file: input dimensions → output dimensions, model used, elapsed seconds.
  - Total elapsed.
  - GPU device that was used (from upscayl-bin's stderr).

## Notes

- Upscayl's `upscayl-standard-4x` produces visibly better results than vanilla `realesrgan-x4plus` on most photos — keep the default unless the user has a reason.
- Anime/illustration content: switch to `realesrgan-x4plus-anime` or one of the anime-specific Upscayl variants. Photo models smear line art.
- Compute time: ~5–20s per 1080p input on a mid-range GPU; 1–3 minutes per image on CPU. Batch a folder overnight for CPU runs.
- Output format default is PNG because JPEG re-encoding immediately after upscale undoes some of the perceptual gain. JPEG only when the user explicitly wants smaller files.
- Combining with other skills:
  - `web-ready` after upscale → use the `gallery` profile to ship the upscaled output to the web at sensible quality.
  - `images-to-pdf` after upscale → enlarge then print at higher DPI.
- This skill does not auto-install Upscayl or download models. The user owns that step. Models are typically several hundred MB total.
