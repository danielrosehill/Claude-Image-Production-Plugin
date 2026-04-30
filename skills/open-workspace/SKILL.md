---
name: open-workspace
description: Open the user's registered image workspace folder. Use when the user says "open my image workspace", "take me to my image workspace", or similar. Reads the path from workspace.json and opens a terminal there.
disable-model-invocation: false
allowed-tools: Bash(cat *), Bash(test *), Bash(ls *), Bash(jq *), Bash(konsole *), Bash(gnome-terminal *), Bash(xdg-open *), Bash(command *), Read
---

# Open Image Workspace

```bash
CONFIG="${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/image-production/workspace.json"
test -f "$CONFIG" || { echo "No image workspace registered. Run workspace-setup first."; exit 1; }
WS=$(jq -r .path "$CONFIG" 2>/dev/null || grep -oP '"path":\s*"\K[^"]+' "$CONFIG")
test -d "$WS" || { echo "Workspace path missing: $WS"; exit 1; }

if command -v konsole >/dev/null; then
  konsole --workdir "$WS" &
elif command -v gnome-terminal >/dev/null; then
  gnome-terminal --working-directory="$WS" &
elif command -v xdg-open >/dev/null; then
  xdg-open "$WS" &
fi

echo "Workspace: $WS"
ls -la "$WS"
```

If config is missing or stale, redirect to `workspace-setup`.
