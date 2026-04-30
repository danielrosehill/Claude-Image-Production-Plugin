---
name: workspace-setup
description: Register or create the user's image production workspace — a folder on disk where they keep image projects. Use on first run, or when the user says "set up my image workspace", "register my image workspace", "change my image workspace path", or similar. Persists the path so other skills (open-workspace, new-project) can reference it.
disable-model-invocation: false
allowed-tools: Bash(mkdir *), Bash(ls *), Bash(test *), Bash(realpath *), Bash(date *), Bash(jq *), Bash(git *), Read, Write
---

# Image Workspace Setup

Register the folder the user treats as their image production workspace. Individual projects live as subfolders inside it.

## Data store

```
${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/image-production/workspace.json
```

Do **not** write under `~/.claude/`.

## Procedure

### 1. Check for existing config

```bash
DATA_DIR="${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/image-production"
CONFIG="$DATA_DIR/workspace.json"
test -f "$CONFIG" && cat "$CONFIG"
```

If one exists, show the path and ask whether to keep or change it.

### 2. Ask the user

1. **Existing or new?** — do they already have an image workspace, or should one be created?
2. **Path?**
   - Existing: ask for absolute path; verify with `test -d`.
   - New: propose `~/media-workspaces/images` as the default. Don't auto-create until the user confirms.

### 3. (New only) Version control

Ask whether to `git init` the workspace. Default **no** — image libraries can be large.

### 4. Create + persist

```bash
mkdir -p "$DATA_DIR"
mkdir -p "<chosen-path>"   # only if new
```

Write `workspace.json`:

```json
{
  "path": "/absolute/path",
  "created": "<ISO-8601>",
  "version_controlled": false,
  "type": "image"
}
```

Use `realpath` to canonicalize.

### 5. Confirm

Print the registered path. Remind the user they can now say "open my image workspace" or "create a new image project".
