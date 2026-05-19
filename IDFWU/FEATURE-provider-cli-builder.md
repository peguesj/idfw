# IDFWU — Provider-CLI Builder & IDFW/FORCE Expansion

> Branch `feat/provider-cli-builder` · APM `formation-6751` · 4 commits · 23 files · +2176/-30

Turns a free-form idea into reality through provider AI CLIs, governed by the
IDFW/IDEA gated lifecycle — Lovable/Replit, but technical and FORCE-aware.

## What shipped

| Capability | Where |
|---|---|
| **Provider-CLI orchestration** — Claude/Codex/Gemini/GitHub Copilot adapters, stdin prompts, normalized event stream, 5s-TTL detection | `Sources/Providers/` |
| **Guided `/idea` pathway** — canonical discover→define→plan→execute with per-phase prompts, artifacts, gate criteria from `~/.claude/skills/idea/SKILL.md` | `IDEAPathway.swift`, `BuilderOrchestrator.swift` |
| **Bundled daemon** — `DaemonController` spawns the `/idea` FastAPI daemon (uv relocatable venv embedded), reads real port from registry, health-probes | `Sources/Services/DaemonController.swift`, `Scripts/bundle-daemon.sh` |
| **Context inheritance** — detects each CLI's config/skills, stages `~/.idfwu/mcp.json`→`<cwd>/.mcp.json`, layered system preamble | `ProviderContext.swift` |
| **PUML/WSD rendering** — `plantuml -tsvg -pipe`, Code\|Preview\|Split pill | `Sources/Diagram/`, `Sources/Views/Diagram/` |
| **Builder UI** — hero prompt, IDEA lifecycle stepper, gate cards, daemon status bar | `Sources/Views/Builder/`, `DaemonStatusBar.swift` |
| **Hook autofixes** — `~/.claude/hooks/idfwu/*.py` cwd→home log paths; nested-session noise filtered from transcript | `ProviderStreamParser.swift` + global hooks |

## Verification (coalesce matrix)

- build debug/release: **PASS** · GUI launch: **PASS** · guided pathway Discovery→Definition gates: **PASS (screenshot-verified)**
- bundled daemon `/api/v3/health` on :4040: **PASS** · `plantuml -tsvg`: **PASS** · hook autofix: **PASS** (no FileNotFoundError)
- No test target (SwiftPM app); verification = clean build + live gated GUI run.

## DRTW notes

`plantuml`, `uv`, native `Picker(.segmented)` all host-installed → zero new deps. App not App-Sandboxed → `Process` can spawn CLIs + the bundled interpreter. Provider layer mirrors `~/Developer/open-design`'s `AgentAdapter` pattern.

## Open / next

- Not pushed (external-mutation boundary) — merge: `git -C ~/Developer/idfw merge feat/provider-cli-builder`
- Pre-existing `MermaidWebView` references a missing `mermaid-renderer.html` (mermaid preview blank until asset added) — not introduced here
- Roadmap: P0 wire DecisionGate/AG-UI · P1 in-app editor + live preview · P2 YUNG command palette · P3 provider context merge
