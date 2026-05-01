[![Claude Code View Marketplace](https://img.shields.io/badge/Claude%20Code-View%20Marketplace-blue?style=for-the-badge&logo=github)](https://github.com/danielrosehill/Claude-Code-Plugins)

## Image Production Plugin

**Version:** 2.0.0

A Claude Code plugin for image editing, batch operations, format conversion, and filesystem organisation of image libraries. Companion to `audio-production` and `video-production`.

## Installation

```bash
/plugin marketplace add https://github.com/danielrosehill/Claude-Code-Plugins
/plugin install image-production@danielrosehill
```

## Commands

### Editing

- `/image-production:apply-filters` — apply filters (blur, sharpen, colour adjustments) across a batch
- `/image-production:bg-removal` — remove image backgrounds
- `/image-production:crop-images` — batch-crop to aspect ratio or fixed dimensions
- `/image-production:batch-resize` — resize a batch to target dimensions
- `/image-production:compress-images` — lossy/lossless compression

### Conversion

- `/image-production:convert-to-webp` — convert JPEG/PNG to WebP
- `/image-production:separate-photos-and-video` — split mixed media imports

### Organisation

- `/image-production:organize-by-resolution` — bucket by pixel dimensions (8K / 4K / 2K / 1080p / 720p / SD / tiny)
- `/image-production:organize-by-aspect-ratio` — bucket by ratio (1:1, 4:3, 3:2, 16:9, portrait variants, panorama)
- `/image-production:organize-by-orientation` — portrait / landscape / square
- `/image-production:organize-by-format` — JPEG / PNG / HEIC / WebP / RAW / other
- `/image-production:group-by-time` — cluster by EXIF capture time into year/month/day
- `/image-production:group-by-camera` — cluster by EXIF Make + Model
- `/image-production:dedupe` — exact and perceptual duplicate detection
- `/image-production:scrub-small-images` — move images below a size threshold to `small/`
- `/image-production:sort-media` — general-purpose media sort
- `/image-production:images-here` — quick inventory of images in the current folder

### Utilities

- `/image-production:install-gimp-plugin` — install a GIMP plugin system-wide

## Skills

- **install-deps** — provision system binaries (ImageMagick, exiftool, optional libvips/heif/optimisers/AVIF/JXL/Real-ESRGAN/darktable) and a plugin-owned uv venv with `Pillow` + `imagehash`. Idempotent doctor. See `skills/install-deps/SKILL.md`.
- **scrub-metadata** — strip EXIF / IPTC / XMP metadata from images using `exiftool`. Supports preview, backup-first, recursive operation, whitelist of fields to preserve (e.g. Orientation), and per-run logging. See `skills/scrub-metadata/SKILL.md`.
- **fast-resize** — batch resize via libvips (5–10× ImageMagick on large batches). Falls back to ImageMagick if `vips` isn't installed. See `skills/fast-resize/SKILL.md`.
- **fast-thumbnail** — high-throughput thumbnail generation via `vipsthumbnail`, with shrink-on-load JPEG decoding for sub-second-per-image runs. See `skills/fast-thumbnail/SKILL.md`.
- **optimize-png** — shrink PNGs losslessly (`oxipng`, 20–40% typical) or lossily (`pngquant`, 60–80%). See `skills/optimize-png/SKILL.md`.
- **optimize-jpeg** — lossless JPEG squeeze (`jpegoptim`) or recompress with better quantisation (`mozjpeg`, ~10–15% smaller). See `skills/optimize-jpeg/SKILL.md`.
- **convert-to-avif** — modern web format via `avifenc` (~30% better than WebP at same quality). See `skills/convert-to-avif/SKILL.md`.
- **web-ready** — orchestrator: ingest anything (HEIC, RAW, JPEG, PNG, TIFF) → strip EXIF → resize → encode AVIF + WebP + JPEG fallback → optimise. Profiles for blog / gallery / thumbnail / archival-web. See `skills/web-ready/SKILL.md`.
- **images-to-pdf** — combine images into a PDF on a standard paper size (A4 default). Modes: one-per-page (auto-orient), multi-up (2/4/6/9 per page), as-is. Lossless JPEG embedding via `img2pdf`, ImageMagick fallback. See `skills/images-to-pdf/SKILL.md`.
- **auto-white-balance** — automatic white balance correction (gray-world / white-patch / combined) via ImageMagick. Single image or batch, optional luminance preservation, blend strength. See `skills/auto-white-balance/SKILL.md`.
- **auto-tone** — automatic tonal correction (auto-level / auto-gamma / punch) via ImageMagick. Hue-preserving by default, blend-strength knob, batch-aware. See `skills/auto-tone/SKILL.md`.
- **auto-deskew** — automatic skew correction. ImageMagick `-deskew` for documents, OpenCV Hough-line fallback for photos. Inscribed-rectangle crop, max-angle guard. See `skills/auto-deskew/SKILL.md`.
- **upscale-image** — AI upscale 2× / 3× / 4× via `upscayl-bin` (Upscayl's bundled CLI) or `realesrgan-ncnn-vulkan` fallback. GPU-accelerated, model-selectable (photo / anime / lite). See `skills/upscale-image/SKILL.md`.

## Dependencies

- **ImageMagick** (`identify`, `convert`) — for dimension probing and basic editing
- **exiftool** (`libimage-exiftool-perl`) — for metadata read/scrub and timestamp extraction
- **Python 3 + `imagehash` + `Pillow`** (optional) — for perceptual deduplication
- **fdupes** (optional) — fast exact-duplicate detection

## Conventions

All organisation commands:

- Default to the current working directory, and ask before operating recursively.
- Preview the plan before touching files.
- Prefer symlinks or CSV manifests over physical moves for large batches.
- Log every run to `notes/{command-name}-{timestamp}.md`.
- Never delete — the disposal bucket is `archive/` or `small/`, and the user decides when to empty it.

## Author

**Daniel Rosehill**
- Website: [danielrosehill.com](https://danielrosehill.com)
- Email: public@danielrosehill.com
- GitHub: [@danielrosehill](https://github.com/danielrosehill)

## License

MIT.
