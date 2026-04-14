# Managing Scan Roots

A **scan root** is a parent directory that IDFWU watches for projects. IDFWU is built on the "dir of dirs" model: a scan root is a folder whose children are candidate projects, each of which may or may not have an IDFW workspace configured.

## Seeded Defaults

On first launch, IDFWU seeds two scan roots:

- `~/Developer` — your main development parent directory
- `~/Developer/idfw` — projects already tracked by the IDFW CLI

You can disable, remove, or reorder these at any time. Removing a seeded root does not delete any files — it only stops IDFWU from scanning it.

## Per-Root Settings

Each scan root has independent configuration:

- **Max depth** — how deep to recurse. `1` means only immediate children; `2` allows one level of nesting (useful for monorepos or `projects/foo/bar` layouts). Higher values slow scans and increase noise.
- **Markers** — file or directory names that qualify a folder as a project. Defaults include `.git`, `Package.swift`, `package.json`, `pyproject.toml`, `Cargo.toml`, `.idfw/`. You can add custom markers (e.g. `mix.exs`, `go.mod`).
- **Enabled toggle** — temporarily disable a root without deleting it. Useful when swapping between work and personal contexts.

## Managing the List

- **Drag-reorder** — the order in the list controls grouping priority in the sidebar. Drag rows to reorder.
- **Export** — write the current scan root configuration to a JSON file for backup or sharing.
- **Import** — load a previously exported JSON config. Imported roots are *added* to the existing list, not merged.

## Tips

- Start with depth `1` and widen only if you're missing projects
- Use separate roots for work vs. personal rather than one deep root
- If a scan is slow, check for large `node_modules` or `.venv` directories inside candidate projects
