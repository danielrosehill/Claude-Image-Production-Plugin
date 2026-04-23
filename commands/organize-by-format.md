# Organize Images by File Format

Sort images into format-based subfolders.

## Task

1. **Ask which folder to operate on** — default is the current working directory. Confirm recursion; default flat.

2. **Classify each file** by extension (case-insensitive), with `file` / `exiftool` as a fallback for extensionless or misnamed files:
   - `JPEG/` — `.jpg`, `.jpeg`
   - `PNG/` — `.png`
   - `HEIC/` — `.heic`, `.heif`
   - `WebP/` — `.webp`
   - `RAW/` — `.nef` (Nikon), `.cr2` / `.cr3` (Canon), `.arw` (Sony), `.dng` (Adobe), `.raf` (Fuji), `.orf` (Olympus), `.rw2` (Panasonic)
   - `TIFF/` — `.tif`, `.tiff`
   - `GIF/` — `.gif`
   - `BMP/` — `.bmp`
   - `SVG/` — `.svg`
   - `other/` — anything that doesn't match, including extensionless files and unknown formats

   ```bash
   # Fallback when extension is missing or misleading:
   exiftool -s -s -s -FileType "image"
   # or
   file --mime-type "image"
   ```

3. **Preview before acting** — table of format → count, plus a sample filename per bucket. Wait for confirmation.

4. **Prefer symlinks or CSV manifest over physical moves**:
   - Option A: symlinked subfolders
   - Option B: `metadata/format-buckets.csv`
   - Option C: physical move on explicit confirmation

5. **Log** to `notes/organize-by-format-{timestamp}.md` with bucket counts and any files flagged as format/extension mismatch.

## Notes

- Flag extension/format mismatch explicitly (e.g. a `.jpg` that `exiftool` reports as PNG) — these are often the interesting files in an import.
- RAW sidecars (`.xmp`) should be kept adjacent to their RAW — when moving/symlinking, pair them.
- HEIC support requires `libheif` to be present if further commands read the image; the bucketing itself is extension-based and doesn't need it.
