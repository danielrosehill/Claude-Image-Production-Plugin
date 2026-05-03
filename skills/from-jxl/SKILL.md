---
name: from-jxl
description: Decode JPEG XL images (.jxl) to PNG or JPEG. Use when you need to convert JXL files back to standard formats for compatibility, display, or further editing.
disable-model-invocation: false
allowed-tools: Bash(djxl *), Bash(ls *), Bash(find *), Bash(mkdir *), Bash(rm *), Read, Write
---

# Decode JPEG XL Images

Extract images from JPEG XL (.jxl) files using `djxl`. Outputs PNG or JPEG, with optional recovery of original JPEG bitstream if the source JXL was a lossless JPEG transcode.

## When to use

- Converting JXL files back to PNG for general use or compatibility.
- Recovering the original JPEG bitstream from a lossless-transcoded JXL file via `djxl --jpeg`.
- Batch-decoding a JXL archive to portable formats.

## Inputs to gather

- **Input .jxl file or directory** — single file or folder.
- **Output format** — `png` (default) or `jpeg`. If the user has a JXL that came from a lossless JPEG transcode and wants to recover the original JPEG byte-exact, offer the `jpeg` format and explain the `--jpeg` flag.
- **Output directory** — optional. Default: same directory as input.

## Procedure

### 1. Check tooling

```bash
command -v djxl || echo "djxl not installed — install with: sudo apt install libjxl-tools"
```

Abort if missing.

### 2. Determine scope and format

- **Single file:** direct conversion.
- **Directory (non-recursive):** loop over all `.jxl` files.
- **Recursive:** use `find` to locate `.jxl` files in the tree.

Confirm the output format with the user.

### 3. Decode

**Single file to PNG (default):**

```bash
djxl input.jxl output.png
```

**Single file to JPEG (standard):**

```bash
djxl input.jxl output.jpg
```

**Single file to original JPEG (lossless transcode recovery):**

If the JXL was created via `cjxl in.jpg out.jxl`, this recovers the original JPEG bitstream byte-exact:

```bash
djxl --jpeg input.jxl recovered.jpg
```

**Batch (folder or recursive):**

```bash
find <target> -maxdepth <1|999> -type f -iname '*.jxl' \
  -exec djxl {} {.}.<format> \;
```

(Replace `<format>` with `png` or `jpg`, or `—jpeg` flag for JPEG recovery.)

### 4. Report

After decoding:

- Count of files decoded, skipped, failed.
- Output file sizes and locations.
- If batch, show a summary of converted files.

## Output / side effects

- New PNG or JPEG files created in the output directory.
- Original `.jxl` files remain unchanged.

## Notes

- **Lossless JPEG recovery:** Only use `djxl --jpeg` if you are confident the `.jxl` source was created via lossless JPEG transcode (i.e., `cjxl original.jpg encoded.jxl`). For JXL files created from PNG or other sources, `--jpeg` may produce incorrect results.
- **Alpha channels:** JXL alpha is preserved when decoding to PNG. JPEG does not support transparency, so any alpha will be lost if decoding to JPEG.
- **Color profile:** JXL can carry ICC color profiles; `djxl` preserves them in the output.
- Depends: `apt install libjxl-tools`.
