# Organize Images by Orientation

Sort images into `portrait/`, `landscape/`, and `square/` buckets.

## Task

1. **Ask which folder to operate on** — default is the current working directory. Confirm recursion; default flat.

2. **Probe each image** for width × height, respecting EXIF Orientation (so a rotated-in-metadata portrait JPEG isn't miscategorised):
   ```bash
   exiftool -s -s -s -ImageWidth -ImageHeight -Orientation "image.jpg"
   # or, auto-oriented:
   identify -auto-orient -format "%w %h %i\n" "image.jpg"
   ```

3. **Bucket** by the *displayed* dimensions:
   - `portrait/` — height > width
   - `landscape/` — width > height
   - `square/` — width == height (±1 px tolerance for off-by-one)

4. **Preview before acting** — table of image → bucket, counts per bucket. Wait for confirmation.

5. **Prefer symlinks or CSV manifest over physical moves**:
   - Option A: symlinked subfolders
   - Option B: `metadata/orientation-buckets.csv`
   - Option C: physical move on explicit confirmation

6. **Log** to `notes/organize-by-orientation-{timestamp}.md` with bucket counts.

## Notes

- **Always honour EXIF Orientation.** Raw pixel dimensions lie for rotated phone photos — without `-auto-orient` or reading the Orientation tag, portrait shots land in `landscape/`.
- Skip non-image files silently; list them in the log.
