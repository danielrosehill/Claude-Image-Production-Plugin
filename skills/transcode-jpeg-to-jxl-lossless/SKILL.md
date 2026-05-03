---
name: transcode-jpeg-to-jxl-lossless
description: Losslessly transcode JPEG files to JPEG XL, preserving the original JPEG bitstream while achieving ~20% file size reduction. Use when archiving JPEG photo libraries where the goal is smaller files without re-compression artifacts.
disable-model-invocation: false
allowed-tools: Bash(cjxl *), Bash(find *), Bash(ls *), Bash(wc *), Bash(du *), Read, Write
---

# Losslessly Transcode JPEG to JPEG XL

Walk a directory of JPEG files and convert them to JPEG XL (.jxl) format using lossless encoding. `cjxl` automatically detects JPEG bitstream and preserves it without re-compression. Reports byte savings; explains how to recover the original JPEG if needed.

## When to use

- Archiving JPEG photo libraries to save space (typically 15–25% reduction) without image degradation.
- Preparing a photo collection for long-term storage where compatibility with JPEG is not required.
- Building a smaller-footprint JXL archive that can still yield the original JPEG via `djxl --jpeg`.

## Inputs to gather

- **Source directory** — folder containing JPEG files (`.jpg` or `.jpeg`). Default: current directory.
- **Recursive?** Ask whether to process subdirectories. Default: **no** (flat, current folder only).
- **Output location** — optional. Default: same directory as originals (`.jxl` files sit alongside `.jpg`).
- **Dry run first?** Recommend a preview pass showing the count and byte savings estimate, before committing to the conversion.

## Procedure

### 1. Check tooling

```bash
command -v cjxl || echo "cjxl not installed — install with: sudo apt install libjxl-tools"
```

Abort if missing.

### 2. Preview

Show the user what will happen:

```bash
# Count JPEGs in scope
find <target> -maxdepth <1|999> -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' \) | tee /tmp/jpegs.txt | wc -l

# Estimate original size
find <target> -maxdepth <1|999> -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' \) -exec du -ch {} + | tail -1
```

Print:
- Number of JPEG files found.
- Total original size.
- Estimated output size (advise 20% reduction as a rough baseline).
- Confirm before proceeding.

### 3. Transcode

Use `-d 0` (lossless) and a reasonable effort (suggest 6–7 for balance):

**Folder (non-recursive):**

```bash
find <target> -maxdepth 1 -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' \) \
  -exec cjxl -d 0 -e 7 {} {.}.jxl \;
```

**Recursive:**

```bash
find <target> -maxdepth 999 -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' \) \
  -exec cjxl -d 0 -e 7 {} {.}.jxl \;
```

(The `-d 0` flag ensures lossless encoding. Effort 7 balances speed and compression. Effort 9 is slower but slightly smaller; only recommend if the user has time.)

### 4. Verify and report

After transcoding:

```bash
# Count JXL files created
find <target> -maxdepth <1|999> -type f -iname '*.jxl' | wc -l

# Total size of JXL files
find <target> -maxdepth <1|999> -type f -iname '*.jxl' -exec du -ch {} + | tail -1

# Bytes saved (original size - new size)
du -ch <target> | tail -1
```

Print:
- Files successfully transcoded.
- Original total size vs. new total size.
- Bytes saved and percentage reduction.
- Any failures (transodes that produced errors).

### 5. Explain recovery path

Inform the user:

> If you ever need to recover the original JPEG bitstream byte-exact (for legal/archival purposes), run:
> ```bash
> djxl --jpeg archive.jxl recovered.jpg
> ```
> This works because `cjxl` detected and preserved the original JPEG structure.

## Output / side effects

- `.jxl` files created in the source directory (or user-specified output folder).
- Original `.jpg` files remain untouched.
- No backup is created; if the originals must be preserved, the user should copy them first.

## Notes

- **Lossless JPEG preservation:** `cjxl` auto-detects JPEG bitstreams and preserves them exactly. This is why `djxl --jpeg` can recover the original — it's not a re-encoded approximation.
- **Effort 7 vs. 9:** Effort 7 compresses in seconds per image; effort 9 can take minutes. For batch workflows, 7 is recommended. Use 9 only if compression size is the overriding concern.
- **Size savings:** Typical JPEG → JXL lossless reduction is 15–25%, depending on the original JPEG quality. Do not oversell — some JPEGs may compress only 5–10%.
- **Selective transcoding:** If you want to skip already-small files or transcode only above a size threshold, filter the find output (e.g., `-size +100k` for files larger than 100 KB).
- Do not delete the original JPEG files automatically. Let the user confirm removal after verifying the JXL output.
- Depends: `apt install libjxl-tools`.
