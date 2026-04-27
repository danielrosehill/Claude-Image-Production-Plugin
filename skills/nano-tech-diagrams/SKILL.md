---
name: nano-tech-diagrams
description: "Create and edit tech diagrams using the nano-tech-diagrams MCP server (Nano Banana 2 via Fal AI). Supports text-to-image, image-to-image, whiteboard cleanup, and 28+ style presets."
---

# Nano Tech Diagrams

This skill uses the **nano-tech-diagrams** MCP server to create and transform tech diagrams using Fal AI's Nano Banana 2 model.

## MCP Server Location

**Always use `mcp__jungle-shared__nano-tech-diagrams__*` (on ubuntuvm).**

Do not use `jungle-local`. Its schema claims to accept local filesystem paths, but the process runs in an environment that cannot read the workstation's filesystem, so every local-path call fails with ENOENT. The shared instance plus the staging endpoint below is the supported path.

## File Staging (CRITICAL)

The MCP server cannot read workstation file paths directly. For any tool that accepts an `image_path` parameter with a local file, stage it to the residence S3 (`mcp-staging` bucket) and pass the presigned URL as `image_path` — the MCP accepts http(s) URLs directly.

### Staging workflow:
1. **Upload** the local file and get a presigned GET URL:
   ```bash
   URL=$(s3-stage /local/path/to/image.jpg)
   ```
2. **Pass** `$URL` as `image_path` to the MCP tool.
3. Objects auto-expire after 1 day (bucket lifecycle); presigned URL TTL defaults to 1 hour (`--expires` to override).

### Batch staging:
For multiple files, call `s3-stage` for each (can be parallelised), collect the URLs, then call the MCP tools.

### When staging is NOT needed:
- `text_to_image` — no input image required
- When `image_path` is already an `http://` or `https://` URL (Fal media, any public host)

## Saving output to the workstation

The MCP returns a `fal.media` URL. **Do not rely on the `download_to` parameter** — it writes to the ubuntuvm process's filesystem, not the workstation. Download the returned URL yourself:

```bash
curl -sSL -o "/absolute/workstation/path/output.png" "<fal.media URL>"
```

## Available Tools

| Tool | Purpose |
|------|---------|
| `list_styles` | Show all 28+ visual style presets (key, name, category, default aspect ratio) |
| `list_diagram_types` | Show all diagram type presets (network, flowchart, mind map, etc.) |
| `whiteboard_cleanup` | Clean up a whiteboard photo into a polished diagram |
| `image_to_image` | Transform an existing image into a styled tech diagram |
| `text_to_image` | Generate a diagram from a text description (no input image) |

## Defaults

- **Model**: Nano Banana 2 (baked in, not configurable)
- **Resolution**: 1K (default)
- **Reasoning**: Minimal (default)
- **Output format**: PNG
- **Aspect ratio**: auto (pass as parameter to override)

## Workflow

### For whiteboard cleanup:
1. Stage the image with `s3-stage <path>` to get a presigned URL
2. Optionally ask about style preference — default is `clean_polished`
3. Call `whiteboard_cleanup` with the presigned URL as `image_path`
4. If domain-specific terms are present, pass them as `dictionary_words` for accurate spelling
5. Download the returned `fal.media` URL to the workstation (see "Saving output" above)

### For image-to-image transformation:
1. Stage the image with `s3-stage <path>` to get a presigned URL
2. Determine what transformation is needed: style change, diagram type conversion, or custom prompt
3. Call `image_to_image` with at least one of: `prompt`, `style`, or `diagram_type`, and the presigned URL as `image_path`
4. Common combos: `style=blueprint` + `diagram_type=network_diagram`
5. Download the returned `fal.media` URL to the workstation

### For text-to-image generation:
1. Get the user's description of what diagram they want
2. Pick an appropriate `diagram_type` if it matches a preset
3. Pick a `style` if the user has a visual preference
4. Call `text_to_image` — no staging needed (no input image)
5. Download the returned `fal.media` URL to the workstation

## Style Categories

- **Professional**: clean_polished, corporate_clean, hand_drawn_polished, minimalist_mono, ultra_sleek, blog_hero
- **Creative**: colorful_infographic, comic_book, isometric_3d, neon_sign, pastel_kawaii, pixel_art, stained_glass, sticky_notes, watercolor
- **Technical**: blueprint, dark_mode, flat_material, github_readme, photographic, terminal_hacker, visionary
- **Retro & Fun**: chalkboard, psychedelic, mad_genius, retro_80s, woodcut
- **Language**: bilingual_hebrew, translated_hebrew

## Diagram Types

- **Infrastructure**: network_diagram, cloud_architecture, kubernetes_cluster, server_rack
- **Software**: system_architecture, microservices, api_architecture, database_schema
- **Process**: flowchart, decision_tree, sequence_diagram, state_machine, pipeline
- **Conceptual**: mind_map, wireframe, gantt_chart, comparison_table, org_chart

## Notes

- For batch processing, call tools sequentially to avoid API rate limits
- The `dictionary_words` parameter helps with domain-specific terminology (e.g., ["Kubernetes", "Proxmox", "PostgreSQL"])
- Aspect ratio options: auto, 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3, 21:9, 9:21
- Resolution options: 0.5K, 1K (default), 2K, 4K
- The `mcp-staging` S3 bucket has a 1-day object lifecycle; presigned URLs default to 1-hour TTL
