---
name: new-workflow
description: Scaffold a multi-touchpoint image workflow inside the registered image workspace — a structured pipeline with explicit human review gates and optional cloud-AI generation/edit steps (Fal nano-banana via MCP). Use when the user says "new image workflow", "scaffold a workflow", "set up an image pipeline", "iterative image project", or describes a job that needs multiple rounds of generation → review → revision → export.
disable-model-invocation: false
allowed-tools: Bash(cat *), Bash(test *), Bash(mkdir *), Bash(ls *), Bash(git *), Bash(date *), Bash(jq *), Bash(curl *), Read, Write, Edit
---

# New Image Workflow

Scaffold a structured, multi-stage image workflow inside the user's registered image workspace. Unlike `new-project` (a flat source/working/exports layout), a workflow expects **iteration**: generation, human review, revision, and export are explicit stages, each with their own folder and manifest entry.

Cloud AI (Fal nano-banana via the `nano-tech-diagrams` MCP) is wired in as an optional driver for the generation and revision stages.

## When to use this vs. new-project

- **`new-project`** — single batch of images, photo-editing style, no iteration loop.
- **`new-workflow`** — generative or hybrid work with multiple touchpoints: brief → references → generate → review → revise → export. Use when the user expects to come back to the project across several sessions and wants a stable structure to resume into.

## Procedure

### 1. Resolve the workspace

```bash
CONFIG="${CLAUDE_USER_DATA:-${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins}/image-production/workspace.json"
test -f "$CONFIG" || { echo "No workspace registered — run workspace-setup first."; exit 1; }
WS=$(jq -r .path "$CONFIG")
```

### 2. Gather workflow metadata

Ask (or infer if obvious):

- **Name** — required. Slugify (lowercase, hyphens).
- **Brief** — one or two sentences describing the deliverable.
- **Cloud-AI driver** — default `fal-nano-banana` (via `mcp__jungle-shared__nano-tech-diagrams__*`). `none` if the user is bringing their own images.
- **Expected rounds** — how many revision cycles to scaffold (default 3).
- **Final aspect ratio / resolution** — for export-stage placeholders.

### 3. Create the layout

```bash
PROJ="$WS/<slug>"
test -e "$PROJ" && { echo "Already exists: $PROJ"; exit 1; }
mkdir -p "$PROJ"/{01-brief,02-references,03-generation,04-review,05-revision,06-export,_manifest}
mkdir -p "$PROJ"/05-revision/round-{1..N}   # N = expected rounds
```

| Stage              | Purpose                                                                 | Touchpoint? |
|--------------------|-------------------------------------------------------------------------|:-----------:|
| `01-brief/`        | `brief.md` — goal, audience, constraints, do/don't list                 | ✓ user      |
| `02-references/`   | Mood board, reference images, prompt fragments                          | ✓ user      |
| `03-generation/`   | First-pass generations (Fal output lives here)                          | ai          |
| `04-review/`       | Selected candidates from `03-generation/` + review notes                | ✓ user      |
| `05-revision/`     | Per-round subfolders with revised generations + notes                   | ai + user   |
| `06-export/`       | Final deliverables — sized, formatted, metadata-scrubbed                | ai          |
| `_manifest/`       | `workflow.json` — pipeline state; `prompts.md` — running prompt log     | ai          |

### 4. Write the manifest

`$PROJ/_manifest/workflow.json`:

```json
{
  "slug": "<slug>",
  "created": "<ISO date>",
  "brief": "<one-line summary>",
  "driver": "fal-nano-banana | none",
  "stages": [
    {"id": "01-brief",       "status": "pending", "type": "human"},
    {"id": "02-references",  "status": "pending", "type": "human"},
    {"id": "03-generation",  "status": "pending", "type": "ai"},
    {"id": "04-review",      "status": "pending", "type": "human"},
    {"id": "05-revision",    "status": "pending", "type": "ai+human", "rounds": N, "current_round": 0},
    {"id": "06-export",      "status": "pending", "type": "ai"}
  ],
  "final": {"aspect_ratio": "<...>", "resolution": "1K", "format": "png"}
}
```

### 5. Seed templates

- `01-brief/brief.md` — markdown template with sections: Goal, Audience, Deliverables, Constraints, Do, Don't, Reference Links.
- `_manifest/prompts.md` — append-only log; one heading per generation call with the prompt, model params, and resulting filenames.
- `README.md` at project root — slug, brief, driver, ISO date, stage checklist (mirrors `workflow.json`), and a "Resume here" pointer to the first non-`done` stage.

### 6. (Optional) git init

If the workspace itself is a git repo (check `git -C "$WS" rev-parse --git-dir`), the new workflow is automatically tracked — no separate init. Otherwise, ask whether to `git init` the project folder.

### 7. Confirm and hand off

Report:
- Project path
- Current stage (`01-brief`)
- Next action (open `01-brief/brief.md` and fill in)

## Driving the workflow

Subsequent sessions resume by reading `_manifest/workflow.json` and continuing from the first stage with `status != "done"`.

### Cloud AI generation (stage 03 + 05)

When the active stage is `ai`-typed and the driver is `fal-nano-banana`:

1. Read the brief + references; compose a dense one-paragraph prompt (see `ai-graphics` skill for prompt style).
2. Call `mcp__jungle-shared__nano-tech-diagrams__text_to_image` with `resolution: "1K"` and the configured aspect ratio. For revision rounds that build on a prior image, use `mcp__jungle-shared__nano-tech-diagrams__image_to_image` and pass the selected candidate.
3. Download the returned `fal.media` URL into the stage folder:
   ```bash
   curl -sSL -o "$PROJ/03-generation/$(date +%s)-<slug>.png" "<fal URL>"
   ```
4. Append a log entry to `_manifest/prompts.md`: stage, round, prompt, params, output filename.
5. Mark the stage `awaiting-review` in `workflow.json` and surface the candidates to the user.

### Human touchpoints (stage 01, 02, 04, 05-review)

At each human stage, **stop and prompt the user**. Do not auto-advance. Show:
- What was just produced (file list, thumbnails if available)
- The decision needed (which candidates to keep, what to change, etc.)
- Where to record the decision (a `notes.md` in the stage folder)

After the user records the decision, mark the stage `done` and advance.

### Export (stage 06)

When all revision rounds are `done`:

1. Take the selected final images from the last `05-revision/round-N/` folder.
2. Apply: resize to target resolution, convert to target format, scrub metadata (use `optimize-jpeg` / `convert-to-webp` / `scrub-metadata` skills as appropriate).
3. Write to `06-export/` with stable filenames (`<slug>-<variant>.<ext>`).
4. Mark stage `done`.

## Notes

- Don't overwrite existing files in `03-generation/` or `05-revision/round-*/` — always timestamp-prefix.
- The manifest is the source of truth; the README is a human-readable mirror, regenerate it from the manifest when state changes.
- If the user changes the driver mid-flow (e.g., switches from cloud-AI to bringing their own), update `workflow.json` and note it in `prompts.md`.
