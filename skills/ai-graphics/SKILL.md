---
name: ai-graphics
description: "Generate AI graphics (banners, illustrations, hero images, social cards, etc.) using Fal AI's Nano Banana 2. Use when the user asks to create, generate, or make an image, banner, illustration, graphic, or artwork. Always render at 1K resolution."
---

# AI Graphics

Generate AI graphics — banners, hero images, illustrations, social cards, README artwork — using Fal AI's **Nano Banana 2** model via the **nano-tech-diagrams** MCP server.

## MCP Server Location

**Always use `mcp__jungle-shared__nano-tech-diagrams__*` (runs on ubuntuvm).**

Do not use `jungle-local` — it claims to accept local filesystem paths but runs in an environment that cannot read the workstation's filesystem, so every local-path call fails with ENOENT. The shared instance is the working path; pair it with the staging endpoint below for any image input.

## Hard rules

- **Always use `resolution: "1K"`.** Do not use 0.5K, 2K, or 4K unless the user explicitly overrides. 1K is the standard for this workflow.
- Pick an appropriate `aspect_ratio` for the use case:
  - Banners / hero images: `21:9` or `16:9`
  - Social cards / OG images: `16:9`
  - Square avatars / icons: `1:1`
  - Portraits: `2:3` or `9:16`
- Save to a sensible path using `download_to` (e.g., `assets/banner.png`, `images/hero.png`) — don't just leave the fal.media URL floating.
- Default `output_format` to `png` unless the user asks otherwise.

## Prompt style

Nano Banana 2 rewards **detailed, descriptive prompts**. Include:

- Subject and pose
- Setting / background
- Lighting and mood
- Color palette
- Style descriptors (e.g., "polished digital illustration", "cinematic", "flat vector", "watercolor")
- Intended use (e.g., "suitable for a GitHub repository banner")

Keep prompts one dense paragraph rather than a bullet list.

## Procedure: text-to-image

1. Confirm subject, vibe, aspect ratio with the user if unclear.
2. Ensure the target directory exists (`mkdir -p` via Bash).
3. Call `mcp__jungle-shared__nano-tech-diagrams__text_to_image` with the prompt, aspect ratio, and `output_format`.
4. The MCP returns a `fal.media` URL. **Do not rely on the MCP's `download_to` parameter** — the ubuntuvm process cannot write to the workstation filesystem. Instead, capture the URL and download it yourself:
   ```bash
   curl -sSL -o "/absolute/target/path.png" "<fal.media URL>"
   ```
5. Report the local path to the user.

Example:
```
mcp__jungle-shared__nano-tech-diagrams__text_to_image(
  prompt="<detailed paragraph>",
  aspect_ratio="21:9",
  output_format="png"
)
# then: curl -sSL -o /abs/path/banner.png <returned URL>
```

## Procedure: image-to-image (and whiteboard_cleanup)

Local input files must be staged to S3 first — the MCP cannot read local paths directly, but it accepts http(s) URLs.

1. Confirm the transformation with the user (prompt, aspect ratio, target output path).
2. **Stage the input file** to the `mcp-staging` S3 bucket:
   ```bash
   URL=$(s3-stage /local/path/to/input.jpg)
   ```
   `s3-stage` returns a presigned GET URL (default 1-hour TTL).
3. Call `mcp__jungle-shared__nano-tech-diagrams__image_to_image` with `image_path="$URL"`, plus your prompt, aspect ratio, and `output_format`. Use `dictionary_words` for any text that must be spelled correctly.
4. The MCP returns a `fal.media` URL. Download to the target folder:
   ```bash
   curl -sSL -o "/absolute/target/path.jpg" "<fal.media URL>"
   ```
5. Report the local path to the user.

Staged objects expire after 1 day (bucket lifecycle), so you don't need to clean them up.
