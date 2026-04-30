---
name: install-deps
description: Provision the plugin's tools — system binaries via the host package manager, Python tools into a plugin-owned uv venv at <data-dir>/venv/. Idempotent doctor — run before any command reports a missing dep. Never touches system Python or fights PEP 668.
disable-model-invocation: true
allowed-tools: Bash(which *), Bash(command *), Bash(apt *), Bash(apt-get *), Bash(sudo *), Bash(uv *), Bash(curl *), Bash(python3 *), Bash(magick *), Bash(convert *), Bash(identify *), Bash(exiftool *), Bash(vips *), Bash(vipsthumbnail *), Bash(heif-convert *), Bash(oxipng *), Bash(pngquant *), Bash(jpegoptim *), Bash(avifenc *), Bash(cjxl *), Bash(djxl *), Bash(realesrgan-ncnn-vulkan *), Bash(darktable-cli *), Read, Write
---

# Install Dependencies

Two surfaces:

1. **System binaries** — required: `ImageMagick`, `exiftool`. Optional: `libvips-tools`, `libheif-examples`, `oxipng`, `pngquant`, `jpegoptim`, `mozjpeg`, `libavif-bin`, `libjxl-tools`, `realesrgan-ncnn-vulkan`, `darktable-cli`.
2. **Python tools** — `imagehash`, `Pillow` (perceptual dedupe). Installed into a plugin-owned uv venv at `<data-dir>/venv/`.

The plugin invokes Python via `<data-dir>/venv/bin/python`, so the user's system Python stays untouched and PEP 668 / externally-managed-environment errors never occur.

## Resolve paths

```bash
PLUGIN_DATA_DIR="${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/image-production"
VENV_DIR="$PLUGIN_DATA_DIR/venv"
```

## Procedure

### 1. Detect host

```bash
uname -s
which apt-get apt brew dnf pacman 2>/dev/null
which uv 2>/dev/null
```

Record what's available; this drives which install commands you propose.

### 2. Ensure `uv` is available

`uv` is the only hard prerequisite for the Python side. If missing, propose:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Ask before running. Fall back to system pip with `--break-system-packages` only if the user declines — prefer `uv`.

### 3. Walk the system-binary matrix

| Tool | Detect | Required? | Install (apt) | Install (brew) |
|---|---|---|---|---|
| `magick` / `convert` / `identify` | `which magick \|\| which convert` | required | `sudo apt install imagemagick` | `brew install imagemagick` |
| `exiftool` | `which exiftool` | required | `sudo apt install libimage-exiftool-perl` | `brew install exiftool` |
| `fdupes` | `which fdupes` | optional | `sudo apt install fdupes` | `brew install fdupes` |
| `vips` / `vipsthumbnail` | `which vips` | optional (recommended >500 images) | `sudo apt install libvips-tools` | `brew install vips` |
| `heif-convert` | `which heif-convert` | optional | `sudo apt install libheif-examples` | `brew install libheif` |
| `oxipng` | `which oxipng` | optional | `sudo apt install oxipng` | `brew install oxipng` |
| `pngquant` | `which pngquant` | optional | `sudo apt install pngquant` | `brew install pngquant` |
| `jpegoptim` | `which jpegoptim` | optional | `sudo apt install jpegoptim` | `brew install jpegoptim` |
| `mozjpeg` (`cjpeg-mozjpeg`) | `which cjpeg-mozjpeg` | optional | `cargo install mozjpeg-cli` (or binary) | `brew install mozjpeg` |
| `avifenc` | `which avifenc` | optional | `sudo apt install libavif-bin` | `brew install libavif` |
| `cjxl` / `djxl` | `which cjxl` | optional | `sudo apt install libjxl-tools` | `brew install jpeg-xl` |
| `upscayl-bin` | `which upscayl-bin \|\| ls /opt/Upscayl/resources/bin/upscayl-bin 2>/dev/null` | optional | install Upscayl from <https://upscayl.org> (deb / flatpak / appimage) | install Upscayl from <https://upscayl.org> |
| `realesrgan-ncnn-vulkan` (fallback) | `which realesrgan-ncnn-vulkan` | optional | binary release from upstream | binary release from upstream |
| `darktable-cli` | `which darktable-cli` | optional | `sudo apt install darktable` (GUI + CLI) | `brew install darktable` |
| `img2pdf` | `which img2pdf` | optional | `uv tool install img2pdf` (or `sudo apt install python3-img2pdf`) | `pipx install img2pdf` |

For each: if missing, stage the install command tagged required/optional. Required tools that are missing block the install — surface that clearly.

`realesrgan-ncnn-vulkan` and `mozjpeg` are not in apt — for those, point the user at the upstream releases page rather than auto-downloading. Ask before placing binaries under `~/bin/`.

### 4. Provision the venv

If `<VENV_DIR>` doesn't exist:

```bash
uv venv "$VENV_DIR" --python 3.11
```

If it exists, leave it.

### 5. Install Python packages into the venv

| Package | Required? | Used by |
|---|---|---|
| `Pillow` | required | dedupe (perceptual), inspection |
| `imagehash` | required | dedupe (perceptual) |
| `numpy` | required (Pillow/imagehash dep) | dedupe |

Stage:

```bash
source "$VENV_DIR/bin/activate"
uv pip install Pillow imagehash numpy
```

### 6. Verify

After installs, re-run the detect commands and report a green/red status table per tool. Surface install commands the user still needs to run themselves (sudo, cargo).

## Output

Single status report:
- Required system bins: present / missing.
- Optional system bins: present / missing (with one-line reason to install each).
- Venv: provisioned at `<VENV_DIR>`, Python `<version>`.
- Python packages: installed.

Refuse to mark "OK" if any required tool is missing.
