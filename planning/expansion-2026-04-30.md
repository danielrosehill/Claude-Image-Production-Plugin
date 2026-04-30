# Image-Production Plugin — Expansion Plan (2026-04-30)

## Plugin

- **Name:** `image-production`
- **Path:** `~/repos/github/my-repos/Claude-Image-Production-Plugin`
- **Scope:** Image editing, batch ops, format conversion, filesystem organisation of image libraries (resolution / aspect / orientation / format / EXIF / dedupe).

## Audit

**Already covered:**
- ImageMagick (`convert`, `identify`) — resize, crop, format, filters, identify.
- exiftool — read/scrub metadata, capture-time grouping, camera grouping.
- imagehash + Pillow — perceptual dedupe.
- fdupes — exact dedupe.
- WebP conversion.
- AI: ai-graphics, nano-tech-diagrams skills (fal/replicate-driven).
- bg-removal command.

**Gaps (CLI-side):**
- Modern format encoding — no AVIF (`avifenc`), no JPEG XL (`cjxl`).
- Format-specific *optimisation* — no dedicated lossless/lossy optimisers (`oxipng`, `pngquant`, `jpegoptim`, `mozjpeg`); `compress-images` is generic.
- HEIC ingest — common iPhone import pain, no batch HEIC→JPEG/PNG path (`heif-convert`).
- AI upscaling — no Real-ESRGAN / waifu2x integration for upscaling (counterpart to nano-tech-diagrams' generation flow).
- RAW processing — no `darktable-cli` / `rawtherapee-cli` skill for camera RAW (CR2, ARW, NEF, DNG) → developed JPEG/TIFF.

## Recommended additions

### 1. `heif-convert` (libheif-examples) — HEIC → JPEG/PNG batch (REQUIRED for iPhone users)

- **Licence:** LGPL-3.0.
- **Install:** `sudo apt install libheif-examples` (sometimes packaged as `heif-gdk-pixbuf` deps; `heif-convert` binary is the target).
- **Why it fits:** iPhone exports HEIC by default. The plugin's organisation skills handle HEIC as a format bucket, but there's no skill to *convert* a HEIC batch to a portable format for downstream tooling (web upload, sharing with non-Apple users). Universal pain point.
- **Why not somewhere else:** Format conversion lives here.
- **Skills to add:**
  - `heic-to-jpeg` — Use when the user has a folder of HEIC files (iPhone import) and wants them as JPEG/PNG. Preserves EXIF, supports quality flag, optional `-keep-original` to retain HEIC alongside.
- **Install required?** Optional. apt-only, tiny.

### 2. PNG/JPEG optimisers — `oxipng`, `pngquant`, `jpegoptim`, `mozjpeg` (OPTIONAL bundle)

- **Licences:** MIT (oxipng), GPL-3.0 (pngquant), GPL-2.0+ (jpegoptim), BSD-3 (mozjpeg).
- **Install:** `sudo apt install oxipng pngquant jpegoptim` for the first three; `mozjpeg` typically wants `cargo install mozjpeg-cli` or a binary release.
- **Why it fits:** `compress-images` today is generic. These tools deliver format-specific squeeze: `oxipng` lossless PNG (often 20–40% reduction), `pngquant` lossy palette-based PNG, `jpegoptim` lossless JPEG, `mozjpeg` re-encode for ~10% better compression than libjpeg-turbo.
- **Why not somewhere else:** Image production primitive.
- **Skills to add:**
  - `optimize-png` — Use when the user wants to losslessly (oxipng) or aggressively (pngquant) shrink PNG files in a batch. One skill, mode-flag-driven.
  - `optimize-jpeg` — Use when the user wants to losslessly shrink JPEGs (jpegoptim) or re-encode for better compression (mozjpeg). One skill, mode-flag-driven.
- **Install required?** Optional. Add the apt trio to deps; mozjpeg behind a "want best-quality JPEG" footnote.

### 3. `avifenc` + `cjxl` — modern image formats (OPTIONAL)

- **Licences:** BSD-2 (libavif), Apache-2.0 (libjxl).
- **Install:** `sudo apt install libavif-bin libjxl-tools`.
- **Why it fits:** AVIF and JPEG XL beat WebP on both compression ratio and quality. Already have `convert-to-webp` — the natural extension is `convert-to-avif` and `convert-to-jxl` for users targeting modern browsers / archival storage.
- **Why not somewhere else:** Format conversion is here.
- **Skills to add:**
  - `convert-to-avif` — Use when the user wants to convert JPEG/PNG to AVIF for web delivery or archival. Quality slider, batch mode, preserve EXIF flag.
  - `convert-to-jxl` — Use when the user wants JPEG XL output for archival (lossless re-encode of JPEG is bit-exact reversible, a unique JXL property worth surfacing).
- **Install required?** Optional.

### 4. `realesrgan-ncnn-vulkan` — AI upscaling (OPTIONAL)

- **Licence:** BSD-3.
- **Install:** Single static binary release from GitHub (no apt). Place under the plugin user-data dir or `~/bin/`.
- **Why it fits:** The plugin already does AI generation (`ai-graphics`, `nano-tech-diagrams`); upscaling is the symmetric op. ncnn-vulkan variant is GPU-accelerated, single binary, no Python deps — best agent-fitness in the upscaler space.
- **Why not somewhere else:** AI image post-processing fits image-production.
- **Skills to add:**
  - `upscale-image` — Use when the user wants to upscale a batch of images 2× / 3× / 4× with Real-ESRGAN. Choice of model (default `realesr-animevideov3` for illustration, `realesrgan-x4plus` for photos).
- **Install required?** Optional. Document the binary-download path explicitly (the plugin shouldn't auto-download GitHub releases without consent).

### 5. `darktable-cli` — RAW development (OPTIONAL)

- **Licence:** GPL-3.0.
- **Install:** `sudo apt install darktable` (provides the GUI + the CLI).
- **Why it fits:** Camera RAW (CR2, ARW, NEF, DNG) is currently invisible to the plugin — the organisation commands bucket "RAW" as a format but there's no path to *develop* a RAW into a usable JPEG/TIFF. `darktable-cli` accepts an XMP sidecar (the same one Daniel would author in the GUI) and renders headlessly.
- **Why not somewhere else:** Image production. RawTherapee CLI is an alternative; pick darktable for tighter Linux integration and active maintenance.
- **Skills to add:**
  - `develop-raw` — Use when the user has camera RAW files and wants to render them to JPEG/TIFF using darktable, optionally applying an XMP preset/sidecar.
- **Install required?** Optional. Apt is heavy (pulls full darktable GUI); document the `darktable-cli` binary as the only target.

## Rejected candidates

- **tesseract / OCR** — Out of scope. Image production ≠ text extraction. Belongs in a separate plugin (or document workflow).
- **mat2** — Redundant with `scrub-metadata` (exiftool).
- **G'MIC (`gmic`)** — Tempting (huge filter library), but overlaps with `apply-filters` and the marginal gain is artistic-niche. Reject for v1; revisit if Daniel wants painterly/vintage filters.
- **ImageMagick `magick`** — Already required.
- **GIMP `-b` (Script-Fu)** — Awkward DSL; agent-fit is poor compared to ImageMagick / vips. The existing `install-gimp-plugin` command is enough.
- **waifu2x-converter-cpp / waifu2x-ncnn-vulkan** — Subsumed by Real-ESRGAN-ncnn-vulkan (newer, broader model selection, single-binary).
- **rawtherapee-cli** — Subsumed by darktable-cli (one RAW developer is enough; pick the more agent-friendly).
- **`guetzli`** — Slow (~minute per JPEG), niche. mozjpeg covers the same need with usable throughput.
- **`zopflipng`** — Slow lossless PNG; oxipng achieves comparable ratios in seconds.

## Concrete diffs

### Edits to `skills/install-deps/SKILL.md`

System binaries to add:

```
| `heif-convert` | `which heif-convert` | optional | `sudo apt install libheif-examples` | `brew install libheif` |
| `oxipng` | `which oxipng` | optional | `sudo apt install oxipng` | `brew install oxipng` |
| `pngquant` | `which pngquant` | optional | `sudo apt install pngquant` | `brew install pngquant` |
| `jpegoptim` | `which jpegoptim` | optional | `sudo apt install jpegoptim` | `brew install jpegoptim` |
| `mozjpeg` (`cjpeg-mozjpeg`) | `which cjpeg-mozjpeg` | optional | `cargo install mozjpeg-cli` (or binary) | `brew install mozjpeg` |
| `avifenc` | `which avifenc` | optional | `sudo apt install libavif-bin` | `brew install libavif` |
| `cjxl` / `djxl` | `which cjxl` | optional | `sudo apt install libjxl-tools` | `brew install jpeg-xl` |
| `realesrgan-ncnn-vulkan` | `which realesrgan-ncnn-vulkan` | optional | binary download from upstream releases | binary download |
| `darktable-cli` | `which darktable-cli` | optional | `sudo apt install darktable` (GUI + CLI) | `brew install darktable` |
```

### New skill directories to create

- `skills/heic-to-jpeg/SKILL.md`
- `skills/optimize-png/SKILL.md`
- `skills/optimize-jpeg/SKILL.md`
- `skills/convert-to-avif/SKILL.md`
- `skills/convert-to-jxl/SKILL.md`
- `skills/upscale-image/SKILL.md`
- `skills/develop-raw/SKILL.md`

### README.md updates

Add a new "Optimisation & modern formats" section listing the new skills. Update the Dependencies block to mirror the install-deps table.

### `plugin.json` updates

Add the new SKILL.md paths to the `skills` array.

## Order of operations

1. **`heic-to-jpeg`** — universal iPhone-import pain point, trivial install.
2. **`optimize-png` + `optimize-jpeg`** — fill out compression. apt-only (mozjpeg footnoted as cargo).
3. **`convert-to-avif` + `convert-to-jxl`** — modern formats. apt-only.
4. **`upscale-image`** — useful but binary-download required. Land after the easy wins.
5. **`develop-raw`** — heaviest install (full darktable). Niche use; defer last.

Per Daniel's plans rule: as each item is implemented, **delete it from this file** rather than ticking it off.
