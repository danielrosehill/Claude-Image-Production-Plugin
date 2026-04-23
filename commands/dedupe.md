# Deduplicate Images

Find and remove duplicate or near-duplicate images.

## Task

1. **Ask which folder to operate on** — default is the current working directory. Confirm recursion; default recursive for dedup (since duplicates often live in sibling folders).

2. **Ask the user what kind of dedup** they want:
   - **Exact duplicates** — byte-identical files (md5 / sha1). Fast, reliable. Use `fdupes` or a quick md5 pass.
   - **Near-duplicates** — same image re-encoded, resized, or lightly edited. Use perceptual hashing (dHash / pHash) via Python + `imagehash`, or `findimagedupes`.
   - **Both** — exact first, then perceptual on the remainder.

3. **Run detection**:

   Exact:
   ```bash
   fdupes -r <target>/
   # or
   find <target> -type f \( -iname '*.jpg' -o -iname '*.png' -o -iname '*.heic' \
     -o -iname '*.webp' -o -iname '*.tif' -o -iname '*.tiff' \) \
     -exec md5sum {} + | sort | uniq -D -w 32
   ```

   Perceptual (Python + imagehash — preferred; tolerant of re-encodes and mild edits):
   ```bash
   python3 -c "
   import imagehash, pathlib
   from PIL import Image
   hashes = {}
   for p in pathlib.Path('.').rglob('*'):
       if p.suffix.lower() in {'.jpg','.jpeg','.png','.heic','.webp','.tif','.tiff'}:
           try: h = imagehash.dhash(Image.open(p))
           except Exception: continue
           hashes.setdefault(str(h), []).append(str(p))
   for h, files in hashes.items():
       if len(files) > 1: print(h, files)
   "
   ```

   Check tools before invoking: `command -v fdupes`, `python3 -c 'import imagehash'`. If `imagehash` is missing, offer `pip install imagehash Pillow` or a `pipx run` one-liner.

4. **Present duplicate groups** — for each group show filename, size, dimensions, format, and mtime. Mark the proposed **keeper** (default: largest dimensions, then largest byte size, then earliest mtime). Let the user override keeper per group.

5. **Wait for confirmation.** Never auto-remove.

6. **Move non-keepers** to `archive/duplicates/` (preserving the relative path as a manifest sidecar). Do not delete. The user decides when to empty `archive/`.

7. **Log** to `notes/dedupe-{timestamp}.md`:
   - Method used (exact / perceptual / both) and threshold (Hamming distance for perceptual — default 0 for identical dHash, up to 5 for "near")
   - Group count, files moved, files kept
   - Full keeper / non-keeper list

## Notes

- Perceptual hashing across very different resolutions is unreliable — warn the user if they're mixing thumbnails with originals.
- RAW + JPEG pairs from the same shot are **not** duplicates — exclude RAW extensions from perceptual dedup by default, and flag pair relationships separately.
- `fdupes` handles the exact case fast; don't reimplement it in Python unless `fdupes` is unavailable.
- Never delete. `archive/duplicates/` is the disposal path.
