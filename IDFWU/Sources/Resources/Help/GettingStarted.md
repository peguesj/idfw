# Getting Started with IDFWU

**IDFWU** ("I Don't F*** With Uncertainty") is a macOS project manager designed around a simple mental model: you have *folders of folders*, where each inner folder may or may not have an IDFW workspace set up. IDFWU finds those projects, tracks them, and gives you a single place to see what's going on across all of them.

## The Core Idea

Most developers keep their projects in one or two parent directories — `~/Developer`, `~/Projects`, `~/code`. IDFWU calls these **scan roots**. Inside a scan root, each subdirectory is a candidate project. IDFWU looks for **markers** (like `.git`, `package.json`, `Package.swift`, `pyproject.toml`, or an `.idfw/` folder) to decide whether a subdirectory is actually a project.

## Adding Your First Scan Root

1. Open **Preferences** with `Cmd+,`
2. Select the **Scan Roots** tab
3. Click **Add Root…** and choose a parent directory
4. Set the **max depth** (usually 1 or 2)
5. Pick which **markers** qualify a directory as a project

IDFWU will start scanning immediately and populate the sidebar.

## What You'll See

The main window is a **three-column layout**:

- **Sidebar** — grouped list of discovered projects, filterable by scan root, favorite status, and marker type
- **Detail** — the selected project's metadata, schema documents, parsed IDEA files, and recent events
- **Inspector** — the live Event Stream, connector status, and APM telemetry

## Next Steps

- Right-click any project for the context menu (see *Context Menus* in help)
- Learn the keyboard shortcuts (`Cmd+?` any time)
- Hook up a GitHub connector in **Preferences → Connectors** to enrich projects with remote metadata
