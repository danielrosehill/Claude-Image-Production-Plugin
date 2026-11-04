---
name: ai-graphics
description: "Generate AI graphics (banners, illustrations, hero images, social cards, etc.) with Nano Banana 2 via the fal-ai tools. Use when the user asks to create, generate, or make an image, banner, illustration, graphic, or artwork. For technical diagrams use tech-comms-diagrams."
---

# AI Graphics

Generate AI graphics — banners, hero images, illustrations, social cards, README artwork — with **Nano Banana 2** (`fal-ai/nano-banana-2`) through the gateway's `fal-ai` upstream. For technical diagrams use the `tech-comms-diagrams` plugin instead.

## Tool access

The `fal-ai` tools may not be listed natively; call them as `mcp__gateway__toolbox__call_tool(name="fal-ai__generate_image", arguments={...})`. Tools used here: `fal-ai__generate_image` (text-to-image), `fal-ai__generate_image_from_image` and `fal-ai__edit_image` (image input), `fal-ai__upload_file` (local file to URL). Run `fal-ai__list_models` (`category: "image"`) to see current model ids.

## Hard rules

- Set `model: "fal-ai/nano-banana-2"` explicitly (the tool default is `flux_schnell`). There is no `resolution` parameter, so output size is the model's default.
- Pick `image_size` (enum only: `square`, `landscape_4_3`, `landscape_16_9`, `portrait_3_4`, `portrait_9_16`; there is no `aspect_ratio` and no 21:9):
  - Banners / hero images / social cards: `landscape_16_9`
  - Square avatars / icons: `square`
  - Portraits: `portrait_3_4` or `portrait_9_16`
- Default `output_format` to `png` unless the user asks otherwise.
- The tool cannot save to disk (no `download_to`); download the returned URL yourself to a sensible path (e.g., `assets/banner.png`).

## ## Prompt style

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
3. Call `fal-ai__generate_image` with `model`, `prompt`, `image_size`, `output_format`.
4. The result contains an image URL. Download it:
   ```bash
   curl -sSL -o "/absolute/target/path.png" "<image URL>"
   ```
5. Report the local path to the user.

Example arguments:
```
{"model": "fal-ai/nano-banana-2", "prompt": "<detailed paragraph>", "image_size": "landscape_16_9", "output_format": "png"}
```

## Procedure: image input (transform / edit)

The tools take `image_url`, not a local path (the parameter is `image_url`, not `image_path`). For a local file, get a URL first: `fal-ai__upload_file`, or the `cloud-storage:stage-file` skill if installed.

1. Confirm the transformation with the user.
2. Call `fal-ai__generate_image_from_image` (`image_url`, `prompt`, `strength`, `output_format`) with `model: "fal-ai/nano-banana-2/edit"`, or `fal-ai__edit_image` (`image_url`, `instruction`) for a plain edit. The nano-banana edit ids appear in `list_models` but the tools' documented options are the flux ones (`fal-ai/flux-2/edit`, `fal-ai/flux/dev/image-to-image`); if the call rejects the nano-banana id, fall back to one of those and tell the user. Neither tool has `dictionary_words`; put required text spellings in the prompt.
3. Download the returned URL to the target folder with `curl -sSL -o`.
4. Report the local path to the user.
