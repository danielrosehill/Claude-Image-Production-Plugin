# Scrub Small Images

Identify and move images below a configurable size threshold — typically thumbnails, icons, favicons, chat-app previews, and web-sidebar gunk that clutters a library import.

## Task

1. **Confirm threshold** — default **longest edge < 500 px**. Ask if the user wants a different cutoff (200 px for aggressive scrub, 1000 px to cull everything non-print-worthy).

2. **Ask which folder to operate on** — default is the current working directory. Confirm recursion; default recursive (small images usually hide in subfolders).

3. **Probe every image** for dimensions (respecting EXIF Orientation so portrait phone shots aren't miscategorised):
   ```bash
   identify -auto-orient -format "%w %h %i\n" *.jpg *.png *.heic *.webp 2>/dev/null
   # or
   exiftool -s -s -s -ImageWidth -ImageHeight "image.jpg"
   ```

4. **Build a candidate list** — images where `max(width, height) < threshold`. Show the user a table: filename, dimensions, format, size on disk.

5. **Wait for confirmation before moving anything.** This feels destructive — never auto-execute.

6. **Move confirmed files** to `small/` (a sibling bucket in the target folder). Preserve relative subpaths if operating recursively. On filename collision, append a short suffix. **Do not delete.**

7. **Log** to `notes/scrub-small-images-{timestamp}.md`:
   - Threshold used
   - Files moved / files kept
   - Full list of moved files with dimensions

8. **Offer a follow-up** — if many images are borderline (e.g. 480–520 px at a 500 px cutoff), ask whether to review those manually before finalising.

## Notes

- Use `max(width, height)` (longest edge) rather than total pixel count — a 100×1000 column banner is more useful than a 300×300 icon even though they're the same pixel count.
- Skip non-image files silently; list them in the log.
- `small/` is the disposal bucket — the user decides when to empty it.
