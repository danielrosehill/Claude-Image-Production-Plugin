---
name: to-jxl
description: Convert images to JPEG XL format (.jxl) with quality presets (lossless, visually lossless, or web). Use when you want optimal compression for photo archival or long-term storage, especially from JPEG originals where lossless transcoding preserves the original bitstream at smaller file size.
disable-model-invocation: false
allowed-tools: Bash(cjxl *), Bash(ls *), Bash(find *), Bash(mkdir *), Bash(rm *), Read, Write
---

# Convert Images to JPEG XL

Encode images to JPEG XL (.jxl) format using `cjxl`. Supports lossless, visually lossless, and web quality presets, with optional effort (compression) tuning.

## When to use

- Converting photos to JXL for archival, where file size matters and quality must be preserved.
- Lossless-transcoding existing JPEG files to save ~20% file size without re-compression artifacts.
- Creating web-optimized JXL variants with controlled visual loss.

## Inputs to gather

- **Input file or directory** — single image, folder, or recursive tree. If omitted, ask for the path.
- **Quality preset** — ask which tier: `lossless` (full fidelity, `-d 0`), `visually-lossless` (imperceptible loss, `-d 1.0`, default), or `web` (visible compression acceptable, `-d 3.0`). Default: visually-lossless.
- **Effort level** — optional, range 1–9 (1 = fastest, 9 = slowest/best compression). Default: 7. Only ask if the user is concerned about speed vs file size.

## Procedure

### 1. Check tooling

```bash
command -v cjxl || echo "cjxl not installed — install with: sudo apt install libjxl-tools"
```

Abort if missing.

### 2. Map quality presets to distance

- `lossless` → `-d 0`
- `visually-lossless` → `-d 1.0`
- `web` → `-d 3.0`

Set `effort=7` unless the user overrides.

### 3. Determine scope

- **Single file:** run one conversion.
- **Directory (non-recursive):** ask before processing, then loop over image files in the folder.
- **Recursive:** use `find` to locate all images in the tree.

Ask for confirmation before batch operations.

### 4. Convert

**Single file:**

```bash
cjxl -d <distance> -e <effort> input.jpg output.jxl
```

**Batch (folder or recursive):**

```bash
find <target> -maxdepth <1|999> -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
     -o -iname '*.gif' -o -iname '*.webp' -o -iname '*.tif' \) \
  -exec cjxl -d <distance> -e <effort> {} {.}.jxl \;
```

Show progress (file count, time remaining estimate if batch is large).

### 5. Report

After conversion:

- Count of files converted, skipped, failed.
- Original vs. converted file sizes; report total bytes saved.
- If any conversions failed, list them and suggest manual inspection.

## Output / side effects

- New `.jxl` files created in the same directory as originals (or in a user-specified output folder).
- Original files remain unchanged.

## Notes

- **Lossless JPEG→JXL transcoding:** `cjxl` auto-detects JPEG bitstream and preserves it. To recover the original JPEG bit-exact later, use `djxl --jpeg input.jxl recovered.jpg`. This is the killer feature for photo archives.
- **Effort vs. speed:** Effort 7 is a good default (reasonable compression in 1–2 seconds per MP). Effort 9 can take minutes on large files. Only use 9 for final archival encodes, not batch preview work.
- **Alpha channels:** JXL supports them natively. PNGs with transparency will retain it.
- Depends: `apt install libjxl-tools`.
