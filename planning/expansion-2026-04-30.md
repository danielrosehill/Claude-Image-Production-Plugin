# Image-Production Plugin — Expansion Plan (2026-04-30)

## Plugin

- **Name:** `image-production`
- **Path:** `~/repos/github/my-repos/Claude-Image-Production-Plugin`
- **Scope:** Image editing, batch ops, format conversion, filesystem organisation, **and web-ready output pipeline**.

## Direction (post-2026-04-30 redirect)

Focus on **outbound** workflows — getting images web-ready and compressed — over inbound format conversion. Ingestion (HEIC, RAW) is folded into the `web-ready` orchestrator rather than getting standalone skills.

Plus: **image → PDF on A4** for digital-printer workflows is a recurring task and gets its own skill.

## Remaining items

### 1. `upscale-image` — Upscayl-bin (and Real-ESRGAN fallback)

- **Tool:** `upscayl-bin` (bundled with Upscayl install — same `realesrgan-ncnn-vulkan` syntax with extra bundled models), fallback to standalone `realesrgan-ncnn-vulkan`.
- **Install:** Detect `upscayl-bin` first (`/opt/Upscayl/resources/bin/upscayl-bin` or flatpak path). If absent, point at Upscayl install or upstream realesrgan release.
- **Why it fits:** Daniel uses Upscayl regularly. Single binary, GPU-accelerated, no Python.
- **Skill to add:**
  - `upscale-image` — Use when the user wants to AI-upscale a batch 2× / 3× / 4×. Picks Upscayl model (`upscayl-standard-4x`, `upscayl-lite-4x`, `realesrgan-x4plus`, `realesrgan-x4plus-anime`) or accepts an explicit `--model` flag.
- **Inputs:** input dir/file, scale factor, model, output dir.

### 2. `convert-to-jxl` — archival JPEG XL (LOW PRIORITY, cheap to add)

- **Tool:** `cjxl` from `libjxl-tools`.
- **Why it fits:** Unique value: JXL can losslessly re-encode an existing JPEG bit-exactly reversibly, and decode is faster than re-decoding the original. ~20% smaller than the source JPEG with zero quality loss. Archival use — not web (browser support is still patchy).
- **Skill to add:**
  - `convert-to-jxl` — Use when the user wants archival JPEG XL output. Supports lossless-from-JPEG mode (the unique JXL trick) and lossy-from-PNG mode.

## Rejected / dropped (post-redirect)

- **heic-to-jpeg** — subsumed by `web-ready` orchestrator (HEIC is just another input).
- **develop-raw** — same. RAW flows through `web-ready`'s decode stage. Standalone skill deferred indefinitely; revisit only if Daniel wants explicit darktable preset application.
- **Generic Real-ESRGAN skill** — replaced by `upscale-image` keyed on Upscayl-bin.
- **tesseract / OCR** — wrong domain.
- **mat2** — redundant with `scrub-metadata`.
- **G'MIC, GIMP `-b`, waifu2x-cpp, rawtherapee-cli, guetzli, zopflipng** — out of scope or subsumed.

## Concrete diffs (remaining)

### Edits to `skills/install-deps/SKILL.md`

Add to system-binary table:

```
| `cjxl` / `djxl` | `which cjxl` | optional | `sudo apt install libjxl-tools` | `brew install jpeg-xl` |
| `upscayl-bin` | `which upscayl-bin \|\| ls /opt/Upscayl/resources/bin/upscayl-bin` | optional | install Upscayl from upscayl.org | install Upscayl from upscayl.org |
```

### New skill directories to create

- `skills/upscale-image/SKILL.md`
- `skills/convert-to-jxl/SKILL.md`

### plugin.json

Register the three new skills in the `skills` array.

### README.md

Add the three new skills to the Skills section.

## Order of operations (remaining)

1. **`upscale-image`** (Upscayl-bin) — handy daily tool.
2. **`convert-to-jxl`** — cheap, archival nice-to-have.

Per Daniel's plans rule: as each item is implemented, **delete it from this file** rather than ticking it off.
