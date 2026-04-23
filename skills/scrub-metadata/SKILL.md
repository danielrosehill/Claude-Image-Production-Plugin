---
name: scrub-metadata
description: Strip EXIF / IPTC / XMP metadata from images using exiftool. Use when the user wants to remove identifying metadata (GPS, camera, timestamps, thumbnails) from a single image, a folder, or a recursive tree before sharing or publishing. Supports preview, backup-first, whitelist of fields to keep (e.g. Orientation), and recursive operation. Logs each run to notes/.
disable-model-invocation: false
allowed-tools: Bash(exiftool *), Bash(mkdir *), Bash(cp *), Bash(find *), Bash(ls *), Bash(wc *), Bash(date *), Read, Write
---

# Scrub Image Metadata

Remove EXIF / IPTC / XMP metadata from images in place (or to a copy), with preview and logging. Wraps `exiftool` — do not hand-roll metadata parsing.

## When to use

- Before publishing photos to a public blog, social media, or client deliverable.
- Bulk-cleaning an archive that may contain GPS or serial-number metadata.
- Preparing reference images for distribution where only orientation should be preserved.

## Procedure

### 1. Establish scope

Ask the user (and confirm before touching files):

- **Target path** — single file, folder, or recursive tree. Default: current working directory.
- **Recursive?** If the target is a folder, ask whether to descend into subfolders. Default **no** (flat, current folder only) unless the user says "recursive" or supplies a root.
- **Backup first?** Default **yes** — `exiftool` keeps `_original` sidecars automatically, but offer an explicit `backup/` copy for the nervous case.
- **Whitelist** — fields to preserve. Common sensible default: keep `Orientation` so the image renders right-way-up. Ask if the user wants to preserve anything else (ColorSpace, ICC profile, copyright).
- **Dry run vs apply** — always preview first.

### 2. Check tooling

```bash
command -v exiftool || echo "exiftool not installed — install with: sudo apt install libimage-exiftool-perl"
```

Abort if missing.

### 3. Preview what will be stripped

Run a read-only pass and show the user a summary:

```bash
# Show metadata currently present on a sample file
exiftool -G1 -a -s "sample.jpg"

# Count files that would be touched
find <target> -maxdepth <1|999> -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
     -o -iname '*.heic' -o -iname '*.webp' -o -iname '*.tif' \
     -o -iname '*.tiff' \) | wc -l
```

Print:
- File count by extension.
- Which tag groups will be removed (EXIF, GPS, IPTC, XMP, MakerNotes, Thumbnail).
- Which tags will be kept (the whitelist).
- Whether a `backup/` copy will be made.

Wait for user confirmation.

### 4. Backup (if requested)

```bash
mkdir -p backup/
cp -r <target>/. backup/
```

Note that `exiftool` also keeps its own `<file>_original` sidecars in-place unless `-overwrite_original` is passed — decide with the user whether to keep those or clean them up at the end.

### 5. Strip metadata

Two patterns — pick based on scope:

**Folder (non-recursive):**

```bash
exiftool -all= -tagsFromFile @ -Orientation \
  -ext jpg -ext jpeg -ext png -ext heic -ext webp -ext tif -ext tiff \
  "<target>"
```

**Recursive tree:**

```bash
exiftool -r -all= -tagsFromFile @ -Orientation \
  -ext jpg -ext jpeg -ext png -ext heic -ext webp -ext tif -ext tiff \
  "<target>"
```

If the user asked to keep additional fields, extend the `-tagsFromFile @ -Field1 -Field2 ...` list. If the user asked to preserve **nothing** (full nuke), drop the `-tagsFromFile` clause — just `-all=`.

To discard the `_original` sidecars in the same run, append `-overwrite_original`. Only do this if a backup was made in step 4, or if the user explicitly waived backup.

### 6. Verify

Sample a few output files and show their remaining metadata:

```bash
exiftool -G1 -a -s "<sample-output>.jpg"
```

Confirm only whitelisted tags remain. If unexpected metadata survived (common with PNG text chunks or XMP sidecars), flag it and offer a second pass with `-xmp:all=` or a manual `exiftool -ext xmp -overwrite_original -all= <path>`.

### 7. Log

Write `notes/scrub-metadata-{YYYY-MM-DD-HHMMSS}.md` in the target folder (or the cwd if the target was a single file). Include:

- Target path and whether recursive.
- Backup taken? Where?
- Whitelist used.
- File count processed, count skipped, count failed.
- Sample before/after metadata dump for one file.
- Any warnings (XMP sidecars found, MakerNotes that resisted strip, etc.).

If `notes/` doesn't exist, create it.

## Notes

- `exiftool` is the only sane tool for this — don't use `convert -strip` (ImageMagick) as the primary path; it silently drops colour profiles and doesn't touch XMP sidecars reliably.
- **GPS is the most common sensitive leak** — always explicitly confirm it's gone in step 6 (`exiftool -GPS:all <file>` should return nothing).
- For HEIC from iPhones, there are often **two** copies of EXIF (container + embedded). `exiftool -all=` handles both, but verify.
- For PNGs, metadata lives in `tEXt` / `iTXt` / `eXIf` chunks — `exiftool -all=` covers them. Do not rely on `optipng -strip all` as a primary scrubber.
- Never operate on the only copy of irreplaceable originals without a backup. If the user is working on an archive, insist on step 4.
- Do not push scrubbed files anywhere automatically — that's a human decision.
