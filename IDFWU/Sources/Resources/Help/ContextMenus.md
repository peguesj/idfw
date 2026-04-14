# Context Menus

Right-click (or Control-click) any project row in the sidebar to open its context menu. The menu provides quick access to the most common per-project operations.

## Menu Items

- **Open in Finder** — reveals the project directory in Finder
- **Reveal in Terminal** — opens a new Terminal window at the project path (respects your default terminal app)
- **Rescan** — re-runs discovery for this project only, refreshing markers, schema documents, and event state
- **Remove from Scope** — removes the *scan root* containing this project from your scan list (see warning below)
- **Copy Path** — copies the absolute filesystem path to the clipboard
- **Open in IDFWU** — sets this project as the active detail-column selection and focuses the window
- **Toggle Favorite** — marks or unmarks the project as a favorite

## Remove from Scope vs. Unfavorite

These two operations are easy to confuse but behave very differently:

- **Remove from Scope** — removes the **entire scan root** that contains this project. Every sibling project in the same root will also disappear from IDFWU. Use this when you're reorganizing your scan roots and no longer want to track a whole parent directory. This does not delete any files on disk.

- **Toggle Favorite (off)** — only affects this single project. The project stays in the sidebar, continues to be scanned, and simply loses its star. Favorites are a personal-preference flag with no side effects on discovery.

**Rule of thumb:** if you want a single project gone, use *Toggle Favorite* or rely on sidebar filters. Only use *Remove from Scope* when you want to stop tracking an entire directory tree.

## Keyboard Equivalent

You can open the context menu for the focused sidebar row with the standard macOS shortcut (right-click or two-finger tap).
