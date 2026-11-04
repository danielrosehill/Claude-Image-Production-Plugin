---
name: check-model-pricing
description: Check what an image model costs on fal (default) or Replicate, search fal's library for a model, and review or update the preferred image models per use case. Use when asked "how much is this model", "what's cheapest for X", "check fal pricing", "review the fal library", "update our preferred models", or before a bulk image run.
---

# Check model pricing

Prices come from the live API, not memory. fal is the default backend and Replicate is the supported alternative.
Preferred models live in `references/preferred-image-models.json` at the plugin root.

## Check a price

Run from the plugin root (`FAL_KEY` and `REPLICATE_API_TOKEN` are in Infisical):

```bash
with-secrets python3 scripts/model_price.py google/nano-banana-2.1 fal-ai/birefnet/v2
with-secrets python3 scripts/model_price.py --search klein
with-secrets python3 scripts/model_price.py --backend replicate black-forest-labs/flux-schnell
```

How to read the result:

- **`unit`:** `images` is per image and `megapixels` is per MP (1024x1024 is about 1.05 MP, 512x512 about 0.26 MP). `compute seconds` depends on run time.
- **`placeholder: true`:** the API's `unit_price` of 1 is not a price. These models bill by tokens (GPT Image, Nano Banana 2.1, some others). `page_price` holds the text from the fal model page. Use the panel's per-image figure from the reference file, or work it out from that text.
- **Replicate:** the API has no price field (`api_price` is always null). `page_prices` is scraped from the model page and picks up unrelated figures, so treat it as a hint and read <https://replicate.com/OWNER/MODEL> for the real price.
- **`error: HTTP 404`:** the id is wrong or retired. Use `--search`.

fal generation responses carry no cost, so any total you report is an estimate from list prices. Say so.

## Review the library and update preferred models

Do this when asked, or when the reference's `updated` date is more than about two months old and a real job depends on it.

1. Snapshot the catalogue with `Tech-Graphics-Benchmark`: `with-secrets uv run python scripts/fal_catalogue.py` writes `catalogue/fal-YYYY-MM-DD.jsonl`. Diff it against the previous snapshot for new endpoints.
2. Shortlist for the use case at about $0.05 per image or less, plus one reference model above that.
3. Try candidates small, with skill `ai-eval/informal-image-eval` if it needs a proper round. A few images on the actual job is enough for a provisional entry.
4. Edit the reference: change `default`, `budget` or `premium`, write what was seen in `evidence`, set `status`, and bump `updated`.

Rules for the reference:

- Evidence is per use case. Don't carry a text-fidelity result over to illustration or characters.
- `status` is `evaluated`, or `provisional` for a handful of tries. An agent read is not human annotation, so say which it was.
- Never replace a default on price alone. It needs at least one look at real output.
