---
name: svg-to-raster
description: Use when the user wants to rasterize SVG files — convert SVG to PNG, PDF, or PostScript at a chosen resolution. Wraps CairoSVG (Python, in the plugin venv). Single file or batch. Companion to `vectorize` (other direction).
---

# SVG to Raster

Rasterize SVG files to PNG / PDF / PS via [CairoSVG](https://github.com/Kozea/CairoSVG). Runs from the plugin's uv venv — no system Python pollution.

## When to use

- Convert logo / icon / diagram SVGs to PNG for use in slides, social, or pipelines that don't accept SVG.
- Render an SVG at multiple resolutions (e.g. 1×, 2×, 3× for app assets).
- Bake an SVG into a PDF for print or archival.

Do **not** use this skill when:
- Source is already raster — wrong direction; use `vectorize` instead.
- You need to *edit* the SVG — CairoSVG is render-only.
- The SVG uses advanced filters / unsupported CSS — CairoSVG covers SVG 1.1 well but newer features may not render. Inspect output and warn the user.

## Inputs

1. **Input** — SVG file or directory. Required.
2. **Format** — `png` (default), `pdf`, `ps`.
3. **Output dir** — default: `<input-dir>/<format>/`. Never overwrites originals.
4. **Scale** — multiplier on the SVG's intrinsic size. Default `1.0`. Use `2.0`, `3.0` for hi-DPI.
5. **Width / Height** — explicit pixel dimensions (overrides scale). Pass one to preserve aspect; both to force.
6. **DPI** — for PDF/PS output. Default `96`.
7. **Background** — default transparent. Pass a CSS colour (`#ffffff`, `white`) for solid fill.
8. **Recursive** — `--recursive` for directory descent.

## Procedure

1. Resolve venv: `VENV_DIR="${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/image-production/venv"`.

2. Verify `cairosvg` is importable in the venv:

   ```bash
   "$VENV_DIR/bin/python" -c "import cairosvg" 2>&1
   ```

   If missing → point at `install-deps`. If it imports but raises a libcairo error, surface the system-lib install command (`sudo apt install libcairo2` / `brew install cairo`).

3. Enumerate `*.svg` inputs (case-insensitive). Skip non-SVG with note.

4. For each file, call CairoSVG via Python one-liner (keeps the skill self-contained — no helper script needed):

   ```bash
   "$VENV_DIR/bin/python" -c "
   import cairosvg, sys
   kwargs = {'url': sys.argv[1], 'write_to': sys.argv[2]}
   # Inject scale / dimensions / dpi / background as appropriate
   cairosvg.svg2png(**kwargs)  # or svg2pdf / svg2ps
   " "<input.svg>" "<output.png>"
   ```

   Function map: `png → svg2png`, `pdf → svg2pdf`, `ps → svg2ps`.

   Optional kwargs: `scale=<float>`, `output_width=<int>`, `output_height=<int>`, `dpi=<int>`, `background_color="<css>"`.

5. Track file sizes and any render warnings (CairoSVG prints to stderr for unsupported features).

## Output

- Rasterized files at `<output-dir>/`.
- Summary:
  - Files processed / failed.
  - Per-file: source dimensions → output dimensions, output size.
  - Any render warnings (unsupported SVG features).

## Notes

- CairoSVG is LGPL-3.0; using it as a CLI dependency is fine, no licence contagion.
- For multi-resolution batch (e.g. app icon set), call this skill multiple times with different `--scale` values, or wrap in a small loop.
- If you need true SVG editing or advanced filter support, look at Inkscape CLI (`inkscape --export-type=png`). CairoSVG is the lighter-weight pure-Python option.
- Animated SVG (SMIL) is not supported — CairoSVG renders the initial frame only.
