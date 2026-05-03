---
name: batch-set-copyright
description: Batch-stamp copyright, artist, and rights information on all images in a directory. Use when you need to quickly add copyright metadata to a photo library before distribution or archival — a convenience wrapper around exiftool.
disable-model-invocation: false
allowed-tools: Bash(exiftool *), Bash(find *), Bash(ls *), Bash(date *), Bash(cp *), Bash(mkdir *), Read, Write
---

# Batch Set Copyright on Images

Walk a directory and stamp copyright, artist, and rights metadata on every image using `exiftool`. Common real-world use: archiving a photo library with a consistent copyright statement.

## When to use

- Preparing a personal photo library for distribution or archival with consistent copyright metadata.
- Quickly tagging all images from an event or shoot with the same artist and copyright info.
- Ensuring your photo library has baseline legal metadata before sharing or licensing.

## Inputs to gather

- **Target directory** — folder containing images to tag. Default: current directory.
- **Recursive?** Ask whether to process subdirectories. Default: **no** (flat, current folder only).
- **Artist name** — required. Ask for the photographer or creator name (e.g., "Daniel Rosehill").
- **Copyright string** — optional. If not provided, auto-generate from current year and artist: `© 2026 <Artist>`. Allow the user to override.
- **Rights/Usage statement** (optional) — additional rights text (e.g., "All rights reserved", "Creative Commons BY-SA 4.0"). If omitted, skip this field.
- **Backup before write?** Default: **yes**. Automatic via exiftool `_original` sidecars.

## Procedure

### 1. Check tooling

```bash
command -v exiftool || echo "exiftool not installed — install with: sudo apt install libimage-exiftool-perl"
```

Abort if missing.

### 2. Build metadata strings

- **Artist:** Use the user-provided value.
- **Copyright:** Use provided, or auto-generate: `© <YYYY> <Artist>` where `<YYYY>` is the current year.
- **Rights/Usage:** Use if provided; otherwise omit.

Print a summary for user confirmation before proceeding.

### 3. Count and preview

```bash
# Count images that will be tagged
find <target> -maxdepth <1|999> -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
     -o -iname '*.heic' -o -iname '*.webp' -o -iname '*.tif' -o -iname '*.tiff' \) | wc -l
```

Print:
- Number of images found.
- Metadata to be applied.
- Request confirmation before applying.

### 4. Apply metadata

**Non-recursive:**

```bash
find <target> -maxdepth 1 -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
     -o -iname '*.heic' -o -iname '*.webp' -o -iname '*.tif' -o -iname '*.tiff' \) \
  -exec exiftool -Artist="<artist>" -Copyright="<copyright>" \
    <-Rights="<rights>"> {} \;
```

(Include `-Rights=` only if the user provided a rights string.)

**Recursive:**

```bash
find <target> -maxdepth 999 -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
     -o -iname '*.heic' -o -iname '*.webp' -o -iname '*.tif' -o -iname '*.tiff' \) \
  -exec exiftool -Artist="<artist>" -Copyright="<copyright>" \
    <-Rights="<rights>"> {} \;
```

Show progress as files are processed (especially for large batches).

### 5. Verify

Sample 3–5 images across the directory and confirm metadata was applied:

```bash
exiftool -Artist -Copyright -Rights "<sample1.jpg>"
exiftool -Artist -Copyright -Rights "<sample2.jpg>"
```

### 6. Report

After completion:

- Count of images successfully tagged.
- Count of failures (if any).
- Reminder: `_original` sidecars have been created (location noted).
- Option: offer to remove `_original` sidecars if the user is confident the write succeeded.

## Output / side effects

- Copyright, Artist, and optional Rights metadata written to all images in scope.
- `_original` sidecars created in the same directories (can be removed post-verification).
- Original images modified; create a backup directory first if preservation is critical.

## Notes

- **Auto-generated copyright:** The script uses the system date (`date +%Y`) to build the year. If images are from a prior year, the user should provide a custom copyright string (e.g., "© 2024 Daniel Rosehill").
- **Metadata format:** `exiftool` writes to EXIF IFD0 / IPTC / XMP as appropriate. Different image readers may check different formats; this skill writes comprehensively so compatibility is high.
- **Batch verification:** For large directories, consider sampling rather than checking every file. Spot-check 5–10% of the batch.
- **Rights field variations:** Some tools recognize `Rights`, others use `UsageRights` or custom XMP fields. The `Rights` tag is most portable; if compatibility issues arise, document alternatives in the report.
- **Preserve prior metadata:** By default, this skill adds/updates copyright metadata without touching other tags. If the user wants a fresh start (nuke all, then add new), use the `scrub-metadata` skill first.
- Depends: `apt install libimage-exiftool-perl`.
