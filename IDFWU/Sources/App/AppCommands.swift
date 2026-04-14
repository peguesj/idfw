import SwiftUI
import AppKit

struct AppCommands: Commands {
    let router: NavigationRouter

    var body: some Commands {
        CommandGroup(replacing: .appInfo) {
            Button("About IDFWU") {
                AboutPanelController.show()
            }
        }

        CommandGroup(replacing: .appSettings) {
            PreferencesMenuItem()
        }

        // Replace the default "New Window" item with project-specific actions.
        // Using `replacing` prevents the system "New Window" from appearing
        // alongside our custom items (which was causing duplicate menu groups).
        CommandGroup(replacing: .newItem) {
            Button("Add Project") {
                NotificationCenter.default.post(name: .addProject, object: nil)
            }
            .keyboardShortcut("n", modifiers: .command)

            Button("Add Scan Root…") {
                Self.presentAddScanRootPanel()
            }
            .keyboardShortcut("o", modifiers: [.shift, .command])

            Button("Sync All") {
                NotificationCenter.default.post(name: .syncAll, object: nil)
            }
            .keyboardShortcut("r", modifiers: [.shift, .command])
        }

        // Inject into the existing View menu. `CommandMenu("View")` would
        // create a second top-level "View" menu next to the system one.
        CommandGroup(after: .sidebar) {
            Divider()
            Button(router.isEventStreamPanelVisible ? "Hide Event Stream" : "Show Event Stream") {
                router.isEventStreamPanelVisible.toggle()
            }
            .keyboardShortcut("e", modifiers: .command)
        }

        CommandGroup(replacing: .help) {
            HelpMenuContent()
        }
    }

    /// Wrapper view so we can use `@Environment(\.openSettings)` inside a
    /// `CommandGroup`, which does not allow environment access directly.
    private struct PreferencesMenuItem: View {
        @Environment(\.openSettings) private var openSettings

        var body: some View {
            Button("Preferences…") {
                openSettings()
            }
            .keyboardShortcut(",", modifiers: .command)
        }
    }

    /// Presents an NSOpenPanel for picking one or more scan-root folders and
    /// registers the selection with the shared `ScanRootStore`.
    @MainActor
    private static func presentAddScanRootPanel() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = true
        panel.prompt = "Add"
        panel.title = "Add Scan Root"
        panel.message = "Select one or more directories to index."

        guard panel.runModal() == .OK else { return }
        let store = ScanRootStore.shared
        for url in panel.urls {
            store.addRoot(url: url)
        }
    }
}

private struct HelpMenuContent: View {
    @Environment(\.openWindow) private var openWindow

    var body: some View {
        Button("IDFWU Help") {
            openWindow(id: "help")
        }
        .keyboardShortcut("?", modifiers: [.command])
    }
}

extension Notification.Name {
    static let addProject = Notification.Name("IDFWU.addProject")
    static let syncAll = Notification.Name("IDFWU.syncAll")
}
