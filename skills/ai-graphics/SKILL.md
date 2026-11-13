---
name: ai-graphics
description: "Generate AI graphics (banners, illustrations, hero images, social cards, characters, etc.) on fal, or Replicate if asked, choosing a cost-effective model per use case. Use when the user asks to create, generate, or make an image, banner, illustration, graphic, or artwork, or to redraw a reference image. For technical diagrams use tech-comms-diagrams."
---

# AI Graphics

Generate banners, hero images, illustrations, social cards, characters and README artwork. For technical diagrams use the `tech-comms-diagrams` plugin.

## Choose the model first

1. Read `references/preferred-image-models.json` at the plugin root and match the job to a `use_cases` entry.
2. Use its `default`. Use `premium` only when the default failed on this job or the user asks. Check `status`: `provisional` means little evidence, so say so if it matters.
3. If no entry fits, or the price matters, use skill `check-model-pricing`. Never choose from a bare `GET https://api.fal.ai/v1/models` listing alone: it is weighted to featured, older and expensive models.
4. Generate a few images, not ten. Two models on the same prompt tells you more than many tries on one.
5. fal is the default backend. Use Replicate when the user asks or a model is only there.

## Run it

**On fal (text-to-image, edits, reference images):** the queue REST API with `$FAL_KEY`. Submit to `https://queue.fal.run/<endpoint>`, poll the returned `status_url` until `COMPLETED`, then GET `response_url`. Use the URLs from the submit response as they are: for endpoints with a subpath (`fal-ai/flux/dev`) status and result live under `owner/app` only.

```bash
bash -c '
R=$(curl -s https://queue.fal.run/<endpoint> -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" -d @args.json)
S=$(echo "$R" | jq -r .status_url); O=$(echo "$R" | jq -r .response_url)
until [ "$(curl -s -H "Authorization: Key $FAL_KEY" "$S" | jq -r .status)" = COMPLETED ]; do sleep 3; done
curl -s -H "Authorization: Key $FAL_KEY" "$O" > result.json'   # images[0].url
curl -sSL -o out.png "$(jq -r '.images[0].url' result.json)"
```

Set the model explicitly and pass a `seed`. Check the real output size: `square` gave 512x512 on FLUX.1 and 1024x1024 on Nano Banana. The input schema for any endpoint is at `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>` (the current edit models take `image_urls`, a list). `image_urls` accepts a `data:image/png;base64,...` URI, so a local file needs no staging. Turn off `enable_prompt_expansion` where it exists. Flatten transparent images onto the target background colour first. `curl https://fal.run/<endpoint>` (synchronous) also works for short jobs.

Model search and price: `GET https://api.fal.ai/v1/models?q=<words>&limit=5` and `GET https://api.fal.ai/v1/models/pricing?endpoint_id=<id>`, both with the Key header.

**Replicate:**

```bash
bash -c 'curl -s -X POST https://api.replicate.com/v1/models/<owner>/<name>/predictions \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" -H "Content-Type: application/json" \
  -H "Prefer: wait" -d "{\"input\":{\"prompt\":\"...\"}}"'   # returns output
```

Input fields differ per model: see `https://replicate.com/<owner>/<name>/api/schema`.

## Prompt style

Write one dense paragraph: subject and pose, background, palette, style ("flat vector", "watercolor") and intended use. With a reference image of a specific character, remove its background, send it as the only image, and write a short instruction: keep this exact character, then only the changes. Describing the character or saying "redraw" makes models drift to a generic one.

## After generating

Open the images and check them against the brief before reporting. Record endpoint, seed and prompt beside the files if they might be regenerated. Report the path and the estimated cost, from list prices.
