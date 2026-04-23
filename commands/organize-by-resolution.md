# Organize Images by Resolution

Sort images in the current folder (or a user-specified folder) into resolution-based subfolders.

## Task

1. **Ask which folder to operate on** — default is the current working directory. Confirm recursion: descend into subfolders, or flat only? Default flat.

2. **Probe each image** for pixel dimensions. Prefer `identify` (ImageMagick) for speed; fall back to `exiftool` for formats it mishandles (HEIC, some RAW):
   ```bash
   identify -format "%w %h %i\n" "*.jpg" "*.png" "*.heic" "*.webp" 2>/dev/null
   # or
   exiftool -s -s -s -ImageWidth -ImageHeight "image.jpg"
   ```

3. **Bucket images** by the longest edge (so portrait and landscape shots land in the same tier):
   - `8K/` — longest edge ≥ 7680
   - `4K/` — longest edge ≥ 3840 and < 7680
   - `2K/` — longest edge ≥ 2560 and < 3840
   - `1080p-class/` — longest edge ≥ 1920 and < 2560
   - `720p-class/` — longest edge ≥ 1280 and < 1920
   - `SD/` — longest edge ≥ 640 and < 1280
   - `tiny/` — longest edge < 640
   - `other/` — probe failures, non-image files

4. **Preview before acting** — print a table of image → bucket with counts per bucket. Do not move anything until the user confirms.

5. **Prefer symlinks or a CSV manifest over physical moves** unless the user asks otherwise:
   - Option A: symlinked subfolders (`4K/photo.jpg → ../photo.jpg`)
   - Option B: `metadata/resolution-buckets.csv` mapping file → bucket
   - Option C: physical move (only on explicit confirmation)

6. **Log** to `notes/organize-by-resolution-{timestamp}.md` with bucket counts, method chosen (symlink / manifest / move), and any probe failures.

## Notes

- Check `identify` (from ImageMagick) is installed before using it; otherwise fall back to `exiftool`.
- Skip non-image files silently, but list them in the log.
- For RAW formats (NEF, CR2, ARW, DNG), `exiftool` is more reliable than `identify`.
