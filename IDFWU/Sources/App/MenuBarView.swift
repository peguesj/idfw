import SwiftUI
import AppKit

/// Menubar popover content for the `MenuBarExtra`.
///
/// Sections:
///  - Open Main Window
///  - Recent Projects (up to 5) — posts `.openRecentProject` with stub id
///  - Quick Add Scan Root… (NSOpenPanel)
///  - Sync All (posts `.syncAll`, shows toast)
///  - Preferences… (⌘,)
///  - About IDFWU
///  - Quit (⌘Q)
struct MenuBarView: View {
    var router: NavigationRouter

    @Environment(\.openWindow) private var openWindow
    @Environment(\.openSettings) private var openSettings
    @Environment(ToastNotifier.self) private var toastNotifier
    @Environment(RecentProjectsStore.self) private var recentProjectsStore
    @Environment(ScanRootStore.self) private var scanRootStore

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Button {
                openMainWindow()
            } label: {
                Label("Open Main Window", systemImage: "macwindow")
            }
            .buttonStyle(.plain)

            Divider()

            // Recent Projects
            Text("Recent Projects")
                .font(.caption)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 4)

            if recentProjectsStore.recent.isEmpty {
                Text("No recent projects")
                    .font(.caption)
                    .foregroundStyle(.tertiary)
                    .padding(.horizontal, 4)
                    .padding(.vertical, 2)
            } else {
                ForEach(recentProjectsStore.recent) { stub in
                    Button {
                        openRecent(stub: stub)
                    } label: {
                        Label(stub.name, systemImage: "cube.fill")
                    }
                    .buttonStyle(.plain)
                }
            }

            Divider()

            Button {
                presentAddScanRootPanel()
            } label: {
                Label("Quick Add Scan Root…", systemImage: "folder.badge.plus")
            }
            .buttonStyle(.plain)

            Button {
                NotificationCenter.default.post(name: .syncAll, object: nil)
                toastNotifier.show("Sync requested")
            } label: {
                Label("Sync All", systemImage: "arrow.triangle.2.circlepath")
            }
            .buttonStyle(.plain)

            Divider()

            Button {
                openSettings()
            } label: {
                Label("Preferences…", systemImage: "gearshape")
            }
            .buttonStyle(.plain)
            .keyboardShortcut(",", modifiers: .command)

            Button {
                showAboutPanel()
            } label: {
                Label("About IDFWU", systemImage: "info.circle")
            }
            .buttonStyle(.plain)

            Divider()

            Button {
                NSApplication.shared.terminate(nil)
            } label: {
                Label("Quit", systemImage: "xmark.circle")
            }
            .buttonStyle(.plain)
            .keyboardShortcut("q", modifiers: .command)
        }
        .padding(10)
        .frame(minWidth: 240)
    }

    // MARK: - Actions

    @MainActor
    private func openMainWindow() {
        openWindow(id: "main")
        NSApp.activate(ignoringOtherApps: true)
    }

    @MainActor
    private func openRecent(stub: RecentProjectStub) {
        // Post so interested views (SidebarView, etc.) can select the project
        // once discovery is populated.
        NotificationCenter.default.post(
            name: .openRecentProject,
            object: nil,
            userInfo: ["projectID": stub.id]
        )
        openMainWindow()
    }

    @MainActor
    private func presentAddScanRootPanel() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = true
        panel.prompt = "Add"
        panel.title = "Add Scan Root"
        panel.message = "Select one or more directories to index."

        guard panel.runModal() == .OK else { return }
        for url in panel.urls {
            scanRootStore.addRoot(url: url)
        }
        toastNotifier.show("Added \(panel.urls.count) scan root\(panel.urls.count == 1 ? "" : "s")")
    }

    @MainActor
    private func showAboutPanel() {
        // TODO: AboutPanelController from Wave 4 — fall back to the stock panel.
        NSApp.orderFrontStandardAboutPanel(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
}

extension Notification.Name {
    /// Posted from the menubar when a user picks a project from the Recent
    /// list. `userInfo["projectID"]` contains the stub id.
    static let openRecentProject = Notification.Name("IDFWU.openRecentProject")
}

#Preview {
    MenuBarView(router: NavigationRouter())
        .environment(ToastNotifier())
        .environment(RecentProjectsStore.shared)
        .environment(ScanRootStore.shared)
}
