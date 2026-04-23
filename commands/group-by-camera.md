# Group Images by Camera

Cluster images by EXIF camera Make + Model.

## Task

1. **Ask which folder to operate on** — default is the current working directory. Confirm recursion; default flat.

2. **Read camera metadata** for each image:
   ```bash
   exiftool -s -s -s -Make -Model -LensModel "image.jpg"
   ```
   Build a bucket label of the form `{Make}_{Model}` with spaces and slashes replaced by hyphens (e.g. `NIKON-CORPORATION_NIKON-D850`, `Apple_iPhone-15-Pro`, `SONY_ILCE-7M3`).

3. **Bucket files**:
   - `{Make}_{Model}/` — one folder per unique (Make, Model) pair
   - `no-exif/` — images with no readable camera metadata (screenshots, scrubbed photos, generated art)
   - `unknown/` — EXIF present but Make or Model missing

4. **Preview before acting** — table of bucket label → count, plus a sample filename per bucket. Wait for user confirmation. Offer to merge near-duplicate bucket names (common: `NIKON CORPORATION` vs `NIKON`).

5. **Prefer symlinks or CSV manifest over physical moves**:
   - Option A: symlinked subfolders
   - Option B: `metadata/camera-buckets.csv` with `filename,make,model,bucket`
   - Option C: physical move on explicit confirmation

6. **Log** to `notes/group-by-camera-{timestamp}.md` with bucket counts and the no-EXIF / unknown tallies.

## Notes

- Lens model is interesting but produces fragmented buckets — include it in the CSV manifest but not in the folder label.
- Phone photos often have consistent Make/Model but many firmware variants; don't try to split on firmware.
- If a user's library is dominated by `no-exif/`, that usually means it was previously scrubbed — note this in the log.
