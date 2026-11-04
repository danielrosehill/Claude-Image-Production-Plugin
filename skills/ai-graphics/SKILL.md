---
name: ai-graphics
description: "Generate AI graphics (banners, illustrations, hero images, social cards, characters, etc.) on fal, or Replicate if asked, choosing a cost-effective model per use case. Use when the user asks to create, generate, or make an image, banner, illustration, graphic, or artwork, or to redraw a reference image. For technical diagrams use tech-comms-diagrams."
---

# AI Graphics

Generate banners, hero images, illustrations, social cards, characters and README artwork. For technical diagrams use the `tech-comms-diagrams` plugin.

## Choose the model first

1. Read `references/preferred-image-models.json` at the plugin root and match the job to a `use_cases` entry.
2. Use its `default`. Use `premium` only when the default failed on this job or the user asks. Check `status`: `provisional` means little evidence, so say so if it matters.
3. If no entry fits, or the price matters, use skill `check-model-pricing`. Never choose from `fal-ai__list_models` alone: it returns about 20 featured models out of hundreds, weighted to older and expensive ones.
4. Generate a few images, not ten. Two models on the same prompt tells you more than many tries on one.
5. fal is the default backend. Use Replicate when the user asks or a model is only there.

## Run it

**Text-to-image on fal:** `mcp__gateway__toolbox__call_tool(name="fal-ai__generate_image", arguments={...})`. Set `model` explicitly (the tool default is `flux_schnell`) and pass a `seed`. It accepts any endpoint id. `image_size` is an enum (`square`, `landscape_4_3`, `landscape_16_9`, `portrait_3_4`, `portrait_9_16`); `square` gave 512x512 on FLUX.1 and 1024x1024 on Nano Banana, so check the size you get. The tool can't save to disk: download the URL with `curl -sSL -o`.

**Image input on fal (edits, reference images):** call the REST endpoint. The current edit models take `image_urls` (a list), while the gateway tools send one `image_url` and document only older FLUX options. The schema for any endpoint is at `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>`.

```bash
with-secrets bash -c 'curl -s https://fal.run/<endpoint> -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" -d @args.json'   # returns images[0].url
```

`image_urls` accepts a `data:image/png;base64,...` URI, so a local file needs no staging. Turn off `enable_prompt_expansion` where it exists. Flatten transparent images onto the target background colour first.

**Replicate:**

```bash
with-secrets bash -c 'curl -s -X POST https://api.replicate.com/v1/models/<owner>/<name>/predictions \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" -H "Content-Type: application/json" \
  -H "Prefer: wait" -d "{\"input\":{\"prompt\":\"...\"}}"'   # returns output
```

Input fields differ per model: see `https://replicate.com/<owner>/<name>/api/schema`.

## Prompt style

Write one dense paragraph: subject and pose, background, palette, style ("flat vector", "watercolor") and intended use. With a reference image, list the features to keep, then the changes.

## After generating

Open the images and check them against the brief before reporting. Record endpoint, seed and prompt beside the files if they might be regenerated. Report the path and the estimated cost, from list prices.
