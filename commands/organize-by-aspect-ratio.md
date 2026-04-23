# Organize Images by Aspect Ratio

Sort images in the current folder (or a user-specified folder) into aspect-ratio buckets.

## Task

1. **Ask which folder to operate on** — default is the current working directory. Confirm recursion; default flat.

2. **Probe each image** for width × height:
   ```bash
   identify -format "%w %h %i\n" *.jpg *.png *.heic *.webp 2>/dev/null
   # or
   exiftool -s -s -s -ImageWidth -ImageHeight "image.jpg"
   ```

3. **Compute aspect ratio** as `width / height` and bucket with a small tolerance (±2%):
   - `1x1/` — square (0.98–1.02)
   - `4x3/` — landscape 4:3 (≈1.333)
   - `3x2/` — landscape 3:2 (≈1.5)
   - `16x9/` — landscape 16:9 (≈1.778)
   - `3x2-portrait/` — portrait 2:3 (≈0.667)
   - `9x16-portrait/` — portrait 9:16 (≈0.5625)
   - `panorama/` — ratio > 2.5 or < 0.4
   - `other/` — doesn't match any of the above

4. **Preview before acting** — table of image → bucket, counts per bucket. Wait for user confirmation.

5. **Prefer symlinks or CSV manifest over physical moves**:
   - Option A: symlinked subfolders
   - Option B: `metadata/aspect-ratio-buckets.csv`
   - Option C: physical move on explicit confirmation

6. **Log** to `notes/organize-by-aspect-ratio-{timestamp}.md` with bucket counts and any probe failures.

## Notes

- The ±2% tolerance matters — phone photos often land slightly off nominal ratios after crop.
- Panorama threshold (>2.5:1) is conservative; drop to 2.0:1 if the user is sorting a stitched-panorama archive.
- Respect EXIF Orientation when computing w/h — a portrait JPEG often stores landscape pixels with orientation=6. Use `identify` with auto-orient or read the `Orientation` tag explicitly.
