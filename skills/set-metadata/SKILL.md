---
name: set-metadata
description: Write EXIF, IPTC, and XMP metadata tags to image files. Use when you need to add or update metadata like artist name, copyright, description, keywords, or GPS coordinates on individual images.
disable-model-invocation: false
allowed-tools: Bash(exiftool *), Bash(ls *), Bash(find *), Bash(cp *), Bash(rm *), Read, Write
---

# Write Metadata to Images

Set metadata tags on image files using `exiftool`. Supports EXIF, IPTC, and XMP metadata, with automatic backup of original files.

## When to use

- Adding copyright and artist information to a photo before distribution.
- Manually setting GPS coordinates if they were not captured.
- Batch-updating descriptions or keywords across multiple images.
- Fixing incorrect camera model or lens metadata.

## Inputs to gather

- **Input file or directory** — single image or folder.
- **Metadata key-value pairs** — ask the user for the tags and values they want to set. Common fields:
  - `Artist` — photographer or creator name.
  - `Copyright` — copyright statement (e.g., "© 2026 Daniel Rosehill").
  - `Description` / `ImageDescription` — image description text.
  - `Keywords` — comma-separated keywords.
  - `LensModel` — lens description (if not auto-detected).
  - `GPSLatitude` / `GPSLongitude` / `GPSAltitude` — GPS coordinates.
  - `DateTimeOriginal` — capture date/time (format: `YYYY:MM:DD HH:MM:SS`).
- **Backup before write?** Default: **yes**. exiftool creates `_original` sidecars; offer an explicit backup copy for safety.

## Procedure

### 1. Check tooling

```bash
command -v exiftool || echo "exiftool not installed — install with: sudo apt install libimage-exiftool-perl"
```

Abort if missing.

### 2. Validate tag names

Ask the user to confirm the exiftool tag names. Common mappings:

| User-facing | exiftool tag |
|---|---|
| Artist | Artist |
| Creator | Creator |
| Copyright | Copyright |
| Description | ImageDescription |
| Keywords | Keywords |
| Lens | LensModel |
| Camera model | Model |

**Gotcha:** EXIF, IPTC, and XMP may use different tag names for the same logical field. exiftool auto-detects the appropriate target; document which format will be used:

```bash
exiftool -a -G1 "<sample.jpg>" | grep -i copyright
```

This shows which groups (EXIF, IPTC, XMP) currently carry copyright info on the sample file.

### 3. Confirm metadata and scope

Print a summary:

- Tags to be set: list all key-value pairs.
- Target files: count and confirm.
- Backup location: where `_original` sidecars will be stored.
- Confirm before proceeding.

### 4. Backup (if requested)

```bash
# exiftool creates _original sidecars by default, but also offer explicit backup
mkdir -p backup/
cp -r "<target>" backup/
```

### 5. Write metadata

**Single file:**

```bash
exiftool -Artist="Daniel Rosehill" -Copyright="© 2026 Daniel Rosehill" \
  -ImageDescription="Sample photo" "<file.jpg>"
```

**Multiple tags at once:**

```bash
exiftool \
  -Artist="<artist>" \
  -Copyright="<copyright>" \
  -ImageDescription="<desc>" \
  -Keywords="<key1>,<key2>" \
  "<file.jpg>"
```

**Batch (directory or recursive):**

```bash
find <target> -maxdepth <1|999> -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \
     -o -iname '*.heic' -o -iname '*.webp' -o -iname '*.tif' \) \
  -exec exiftool -Artist="<artist>" -Copyright="<copyright>" {} \;
```

Append `-overwrite_original` to discard `_original` sidecars, but only if a backup was made in step 4.

### 6. Verify

Sample a few output files and confirm the metadata was written:

```bash
exiftool -Artist -Copyright -ImageDescription "<sample.jpg>"
```

If metadata did not stick (e.g., PNG text chunks), try the XMP-specific path:

```bash
exiftool -XMP:Artist="<artist>" -XMP:Copyright="<copyright>" "<file.png>"
```

### 7. Cleanup (optional)

If the user accepted `-overwrite_original`, remove `_original` sidecars:

```bash
find <target> -maxdepth <1|999> -type f -iname '*_original' -delete
```

## Output / side effects

- Metadata tags written to original files (or to a copy if the user requested a separate output directory).
- `_original` sidecars created in the same directory as each file (unless `-overwrite_original` was used).
- Original files are modified (unless a backup was made in step 4).

## Notes

- **EXIF vs. IPTC vs. XMP:** The same field (e.g., copyright) can live in EXIF, IPTC, and/or XMP. Some readers check only one format. `exiftool` intelligently maps to the appropriate group, but document which format was used:
  - EXIF: structured, camera/lens/exposure info. Limited size.
  - IPTC: editorial metadata (keywords, description, copyright). Limited size.
  - XMP: extensible, can hold arbitrary key-value pairs.
- **PNG and HEIC:** exiftool writes metadata to PNG as XMP in iTXt chunks. HEIC is complex; check the `_original` sidecar to ensure metadata persisted.
- **Tag size limits:** EXIF and IPTC have field-length limits. Very long descriptions (>500 chars) should go in XMP. exiftool warns if a value is too large.
- **Permanent writes:** Always create a backup before bulk metadata writes. Metadata corruption is rare but possible.
- **Preserve other metadata:** By default, `exiftool -Tag=value file` preserves all other metadata. Use `-all=` if you want to nuke everything before writing (not recommended).
- Depends: `apt install libimage-exiftool-perl`.
