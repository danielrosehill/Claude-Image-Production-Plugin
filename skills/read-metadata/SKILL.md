---
name: read-metadata
description: Read and display EXIF, IPTC, XMP, and other metadata from images as structured JSON. Use when you need to inspect image metadata without modifying it — opposite of scrub-metadata, which removes metadata.
disable-model-invocation: false
allowed-tools: Bash(exiftool *), Bash(ls *), Bash(find *), Bash(jq *), Read, Write
---

# Read Image Metadata

Extract metadata from image files using `exiftool` and output as structured JSON. Supports single files, batch operations, and filtering by metadata group (EXIF, IPTC, XMP, GPS, etc.).

## When to use

- Inspecting the metadata on a photo before sharing or publishing.
- Auditing a batch of images to verify copyright, GPS, or camera information.
- Programmatically querying metadata for file organization or validation.

## Inputs to gather

- **Input file or directory** — single image or folder. Default: current directory.
- **Recursive?** If directory, ask whether to descend. Default: **no** (flat).
- **Filter/group** (optional) — ask if they want a specific metadata subset (e.g., EXIF only, GPS only, copyright-related tags). Default: all metadata.
- **Output format** — JSON (default) or a human-readable summary. Recommend JSON for programmatic use, summary for quick inspection.

## Procedure

### 1. Check tooling

```bash
command -v exiftool || echo "exiftool not installed — install with: sudo apt install libimage-exiftool-perl"
```

Abort if missing.

### 2. Determine scope

- **Single file:** direct read.
- **Directory (non-recursive):** read all image files in the folder.
- **Recursive:** use `find` to walk the tree.

### 3. Read metadata

**Single file, full metadata as JSON:**

```bash
exiftool -j "<file.jpg>"
```

**Single file, summary (human-readable):**

```bash
exiftool -G1 -a -s "<file.jpg>" | head -50
```

**Filtered by group (EXIF only):**

```bash
exiftool -j -G1 -EXIF "<file.jpg>"
```

**Common filters:**

- `-EXIF` — EXIF metadata only.
- `-IPTC` — IPTC tags (description, keywords, copyright).
- `-XMP` — XMP metadata (structured, often used by Adobe).
- `-GPS` — GPS coordinates (latitude, longitude, altitude).
- `-MakerNote` — camera-specific metadata.

**Batch (directory or recursive):**

```bash
find <target> -maxdepth <1|999> -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
     -o -iname '*.heic' -o -iname '*.webp' -o -iname '*.tif' \) \
  -exec exiftool -j {} \; > metadata.json
```

### 4. Summarize or display

**For JSON output:**

If the user wants a summary, parse the JSON:

```bash
exiftool -j "<file.jpg>" | jq '.[] | {File, Make, Model, DateTime, GPSLatitude, GPSLongitude, Copyright}'
```

**For a batch report:**

```bash
exiftool -j -a -s "<target>/*" | jq '.[] | {FileName, Make, Model, LensModel, FocalLength, ISO, ExposureTime, FNumber}'
```

### 5. Report

Print the metadata (JSON or summary, per user preference). If batch:

- Count of files read.
- Any files with missing metadata.
- Common metadata patterns (e.g., "15 images from Canon EOS 5D Mark III", "8 images missing GPS").

## Output / side effects

- Metadata displayed on stdout (or saved to a JSON file if requested).
- No files modified.

## Notes

- **Metadata standards overlap:** EXIF, IPTC, and XMP sometimes describe the same field (e.g., copyright, description, keywords). `exiftool -j` merges these intelligently; check the JSON keys to see what's present.
- **Camera-specific tags:** Each camera manufacturer (Canon, Nikon, Sony, etc.) embeds maker-specific metadata. Run with `-MakerNote` to inspect.
- **GPS privacy:** Check for `-GPS` tags before sharing a photo. Many smartphone cameras and some cameras embed GPS by default.
- **Phone metadata:** iPhones embed extensive metadata in EXIF and XMP, including model, iOS version, and processing applied.
- **PNG text chunks:** PNG metadata lives in text chunks (`tEXt`, `iTXt`) rather than EXIF. `exiftool` reads them as XMP or PNG metadata.
- **Batch JSON:** Combine multiple JSON objects with `jq -s '.' output.json` to create a single JSON array for programmatic processing.
- Depends: `apt install libimage-exiftool-perl`.
