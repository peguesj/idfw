import AppKit
import Foundation
import SwiftUI

/// Namespaced static helpers used by project-row `.contextMenu` buttons in
/// the sidebar. All methods run on the main actor because they drive AppKit
/// APIs (NSWorkspace, NSPasteboard).
enum ProjectRowContextActions {

    /// Notification posted when the user picks "Open in IDFWU" from a row's
    /// context menu. `userInfo["project"]` contains the `DiscoveredProject`.
    static let openProjectNotification = Notification.Name("idfwu.openProject")

    // MARK: - Finder / Terminal

    @MainActor
    static func revealInFinder(path: String) {
        let url = URL(fileURLWithPath: path)
        NSWorkspace.shared.activateFileViewerSelecting([url])
    }

    @MainActor
    static func revealInTerminal(path: String) {
        let directory = URL(fileURLWithPath: path)
        let terminalURL = URL(fileURLWithPath: "/Applications/Utilities/Terminal.app")
        let configuration = NSWorkspace.OpenConfiguration()

        NSWorkspace.shared.open(
            [directory],
            withApplicationAt: terminalURL,
            configuration: configuration
        ) { _, error in
            if let error {
                NSLog(
                    "ProjectRowContextActions.revealInTerminal failed for %@: %@",
                    path,
                    error.localizedDescription
                )
            }
        }
    }

    // MARK: - Pasteboard

    @MainActor
    static func copyPath(_ path: String) {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(path, forType: .string)
    }

    // MARK: - In-app selection

    /// Broadcasts a notification so that `RootView` / `NavigationRouter` can
    /// select the project without a direct dependency on this file.
    @MainActor
    static func openInIDFWU(_ project: DiscoveredProject) {
        NotificationCenter.default.post(
            name: openProjectNotification,
            object: nil,
            userInfo: ["project": project]
        )
    }
}
