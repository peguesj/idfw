import SwiftUI
import AppKit

struct AdvancedSettingsView: View {
    @State private var statusMessage: String = ""

    private let resetKeys: [String] = [
        "appearance",
        "appearance.accent.red",
        "appearance.accent.green",
        "appearance.accent.blue",
        "appearance.accent.alpha",
        "scan.autoRefreshSeconds",
        "scan.refreshOnFocus",
        "scan.defaultDepth",
        "connectors.apmUrl"
    ]

    var body: some View {
        Form {
            Section("Reset") {
                Button(role: .destructive) {
                    confirmReset()
                } label: {
                    Label("Reset All Defaults", systemImage: "arrow.counterclockwise.circle")
                }
                Text("Clears all saved preferences. Keychain secrets are unaffected.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Section("Logs") {
                Button {
                    exportLogs()
                } label: {
                    Label("Export Logs...", systemImage: "square.and.arrow.up")
                }

                Button {
                    openLogFolder()
                } label: {
                    Label("Open Log Folder", systemImage: "folder")
                }
            }

            if !statusMessage.isEmpty {
                Section {
                    Text(statusMessage)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .formStyle(.grouped)
        .padding()
    }

    // MARK: - Reset

    private func confirmReset() {
        let alert = NSAlert()
        alert.messageText = "Reset All Defaults?"
        alert.informativeText = "This will clear all saved preferences. This action cannot be undone."
        alert.alertStyle = .warning
        alert.addButton(withTitle: "Reset")
        alert.addButton(withTitle: "Cancel")

        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            let defaults = UserDefaults.standard
            for key in resetKeys {
                defaults.removeObject(forKey: key)
            }
            statusMessage = "Defaults reset at \(Date().formatted(date: .omitted, time: .standard))"
        }
    }

    // MARK: - Export Logs

    private func exportLogs() {
        let panel = NSSavePanel()
        panel.title = "Export Logs"
        panel.nameFieldStringValue = "idfwu-logs-\(Int(Date().timeIntervalSince1970)).log"
        panel.allowedContentTypes = [.plainText]
        panel.canCreateDirectories = true

        guard panel.runModal() == .OK, let url = panel.url else { return }

        let info = ProcessInfo.processInfo
        let content = """
        Log export from IDFWU at \(Date())

        Process: \(info.processName)
        PID: \(info.processIdentifier)
        Host: \(info.hostName)
        OS: \(info.operatingSystemVersionString)
        Arguments: \(info.arguments.joined(separator: " "))
        Environment keys: \(info.environment.keys.sorted().joined(separator: ", "))

        Note: AppLogger uses os.Logger (unified logging). For a full log capture, use:
            log show --predicate 'subsystem == "\(Bundle.main.bundleIdentifier ?? "com.inceptionglass")"' --last 1h
        """

        do {
            try content.write(to: url, atomically: true, encoding: .utf8)
            statusMessage = "Exported to \(url.lastPathComponent)"
        } catch {
            FileHandle.standardError.write(Data("Log export failed: \(error)\n".utf8))
            statusMessage = "Export failed: \(error.localizedDescription)"
        }
    }

    // MARK: - Open Log Folder

    private func openLogFolder() {
        let fm = FileManager.default
        guard let home = fm.homeDirectoryForCurrentUser as URL? else { return }
        let logDir = home.appendingPathComponent("Library/Logs/IDFWU", isDirectory: true)

        if !fm.fileExists(atPath: logDir.path) {
            do {
                try fm.createDirectory(at: logDir, withIntermediateDirectories: true)
            } catch {
                FileHandle.standardError.write(Data("Failed to create log dir: \(error)\n".utf8))
                statusMessage = "Could not create log folder"
                return
            }
        }

        NSWorkspace.shared.activateFileViewerSelecting([logDir])
    }
}

#Preview {
    AdvancedSettingsView()
}
