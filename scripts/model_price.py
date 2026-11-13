#!/usr/bin/env python3
"""Check image model list prices on fal (default) or Replicate. Prints JSON.

Needs FAL_KEY (fal) or REPLICATE_API_TOKEN (--backend replicate) in the environment.

  python3 scripts/model_price.py google/nano-banana-2.1 fal-ai/birefnet/v2
  python3 scripts/model_price.py --search klein
  python3 scripts/model_price.py --backend replicate black-forest-labs/flux-schnell
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

def need_env(name):
    v = os.environ.get(name)
    if not v:
        sys.exit("error: set " + name + " in the environment (from your own secrets manager or shell)")
    return v


FAL = "https://api.fal.ai/v1"
UA = {"User-Agent": "model-price-check"}


def fetch(url, headers=None, raw=False):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
            return body.decode("utf-8", "replace") if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("rate-limited: " + url)


def fal_headers():
    return {"Authorization": "Key " + need_env("FAL_KEY")}


def fal_page_price(endpoint):
    """Token-billed models have a placeholder API price; the model page holds the real text."""
    try:
        html = fetch("https://fal.ai/models/" + endpoint, raw=True)
    except urllib.error.HTTPError:
        return None
    m = re.search(r'pricingInfoOverride\\?"\s*:\s*\\?"(.{1,400}?)\\?"[,}]', html)
    return m.group(1) if m else None


def fal_price(endpoint):
    q = urllib.parse.urlencode({"endpoint_id": endpoint})
    try:
        p = fetch(f"{FAL}/models/pricing?{q}", fal_headers())["prices"][0]
    except urllib.error.HTTPError as e:
        return {"backend": "fal", "endpoint": endpoint, "error": f"HTTP {e.code}"}
    out = {"backend": "fal", "endpoint": endpoint, "unit_price": p["unit_price"], "unit": p["unit"], "currency": p["currency"]}
    if p["unit_price"] == 1 and p["unit"] in ("units", "credits"):
        out["placeholder"] = True
        out["page_price"] = fal_page_price(endpoint)
    return out


def fal_search(term):
    hits = []
    for cat in ("text-to-image", "image-to-image"):
        cursor = None
        while True:
            params = {"category": cat, "status": "active", "limit": 100}
            if cursor:
                params["cursor"] = cursor
            page = fetch(f"{FAL}/models?{urllib.parse.urlencode(params)}", fal_headers())
            hits += [m["endpoint_id"] for m in page["models"] if term.lower() in json.dumps(m).lower()]
            cursor = page.get("next_cursor")
            if not page.get("has_more") or not cursor:
                break
    return sorted(set(hits))


def replicate_price(model):
    """Replicate's API exposes no price field, so this confirms the model and reads its page."""
    try:
        m = fetch("https://api.replicate.com/v1/models/" + model,
                  {"Authorization": "Bearer " + need_env("REPLICATE_API_TOKEN")})
    except urllib.error.HTTPError as e:
        return {"backend": "replicate", "endpoint": model, "error": f"HTTP {e.code}"}
    out = {"backend": "replicate", "endpoint": model, "run_count": m.get("run_count"), "api_price": None}
    html = fetch(f"https://replicate.com/{model}", raw=True)
    out["page_prices"] = sorted(set(re.findall(r"\$\d+(?:\.\d+)?(?: per [a-z ]{3,30}| / [a-z ]{3,30})?", html)))[:8]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--backend", choices=["fal", "replicate"], default="fal")
    ap.add_argument("--search", help="fal only: find active image endpoints by keyword, then price them")
    a = ap.parse_args()
    ids = list(a.ids)
    if a.search:
        if a.backend != "fal":
            sys.exit("--search is fal only")
        ids += fal_search(a.search)[:25]
    if not ids:
        ap.error("give at least one model id, or --search")
    check = fal_price if a.backend == "fal" else replicate_price
    print(json.dumps([check(i) for i in ids], indent=2))


if __name__ == "__main__":
    main()
