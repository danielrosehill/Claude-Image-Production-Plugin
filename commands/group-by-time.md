# Group Images by Capture Time

Cluster images by EXIF `DateTimeOriginal` into year / month (and optionally day) folders.

## Task

1. **Ask which folder to operate on** — default is the current working directory. Confirm recursion; default flat.

2. **Confirm granularity** with the user:
   - `YYYY/` only
   - `YYYY/MM/` (default)
   - `YYYY/MM/DD/`
   - Custom (e.g. session-based, gap > N hours starts a new group)

3. **Read capture timestamps** for each image. Prefer, in order:
   1. `exiftool` `DateTimeOriginal`
   2. `exiftool` `CreateDate` / `MediaCreateDate`
   3. `exiftool` `FileModifyDate` (fallback — **warn the user** when falling back, since mtime reflects copy time)
   ```bash
   exiftool -s -s -s -DateTimeOriginal -CreateDate -FileModifyDate "image.jpg"
   ```

4. **Build a timeline** — sorted (filename, timestamp) list. Show the user min/max timestamps and any suspicious gaps / duplicates.

5. **Propose grouping** — print bucket labels (`2026/04/`, `2026/04/18/`) with image counts. Flag any file that fell back to mtime. Let the user rename buckets (e.g. `2026-04-18_wedding/`).

6. **Preview before acting**, then choose method:
   - Option A: `metadata/time-groups.csv` with `filename,timestamp,group` (no moves)
   - Option B: symlinked folders (`time-groups/2026/04/photo.jpg → ../../../photo.jpg`)
   - Option C: physical move on explicit confirmation

7. **Log** to `notes/group-by-time-{timestamp}.md`:
   - Granularity used
   - Bucket labels and counts
   - Files that fell back to mtime (flagged for review)
   - Files with no usable timestamp at all (bucketed to `unknown-date/`)

## Notes

- **Timezone matters.** If EXIF lacks a TZ offset, ask the user which TZ to assume (and record it in the log). Default to the system TZ (Israel IST/IDT here).
- For mixed-source imports (phone + camera + screenshots), timestamps from different devices may drift — flag clips that cluster oddly.
- Never mutate originals. Prefer the CSV manifest for archives with many files.
- Files with no EXIF and no reliable mtime go to `unknown-date/` — don't invent a timestamp.
