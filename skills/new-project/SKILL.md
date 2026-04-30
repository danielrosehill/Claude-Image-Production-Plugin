---
name: new-project
description: Create a new image project inside the user's registered image workspace. Use when the user says "new image project", "create an image project called X", "scaffold a new image set", or similar. Creates a project subfolder with source, working, exports, references layout and an optional git init.
disable-model-invocation: false
allowed-tools: Bash(cat *), Bash(test *), Bash(mkdir *), Bash(ls *), Bash(git *), Bash(date *), Bash(jq *), Read, Write
---

# New Image Project

Scaffold a project folder inside the registered image workspace.

## Procedure

### 1. Resolve the workspace

```bash
CONFIG="${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/image-production/workspace.json"
test -f "$CONFIG" || { echo "No workspace registered — run workspace-setup first."; exit 1; }
WS=$(jq -r .path "$CONFIG" 2>/dev/null || grep -oP '"path":\s*"\K[^"]+' "$CONFIG")
```

### 2. Ask for project metadata

- **Name** — required. Slugify (lowercase, hyphens for spaces).
- **Version control** — ask; default **no**.

### 3. Create the layout

```bash
PROJ="$WS/<slug>"
test -e "$PROJ" && { echo "Already exists: $PROJ"; exit 1; }
mkdir -p "$PROJ"/{source,working,exports,references,thumbnails}
```

| Folder         | Purpose                                                    |
|----------------|------------------------------------------------------------|
| `source/`      | Original images — never edited in place                    |
| `working/`     | In-progress edits, layered files (PSD, XCF, AFPHOTO)       |
| `exports/`     | Final deliverables (web JPEG/WebP, print TIFF, etc.)       |
| `references/`  | Mood boards, reference images, prompts                     |
| `thumbnails/`  | Small previews for indexing                                |

Write a `README.md` in the project root with the slug, ISO date, and notes section.

### 4. (Optional) git init

If the user wants version control, `git init` and add a `.gitignore` excluding `source/` and `exports/` if they're large.

### 5. Confirm

Print the project path. Offer to `cd` or open in a terminal.
