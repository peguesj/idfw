import Foundation
import AppKit

/// JSON payload for exporting / importing the ScanRootStore contents.
struct ScopeExportPayload: Codable {
    var version: Int
    var exportedAt: Date
    var roots: [ScanRoot]
    var markers: [String]

    static let currentVersion: Int = 1
}

/// Handles NSSavePanel / NSOpenPanel driven export and import of scope
/// configuration. Runs off the main actor where possible but touches
/// AppKit panels and the store on the main actor.
actor ScopeTransferHandler {
    enum TransferError: Error, LocalizedError {
        case userCancelled
        case encodingFailed
        case decodingFailed(String)
        case writeFailed(String)
        case readFailed(String)

        var errorDescription: String? {
            switch self {
            case .userCancelled: return "Cancelled by user."
            case .encodingFailed: return "Failed to encode scope payload."
            case .decodingFailed(let detail): return "Failed to decode scope payload: \(detail)"
            case .writeFailed(let detail): return "Failed to write scope file: \(detail)"
            case .readFailed(let detail): return "Failed to read scope file: \(detail)"
            }
        }
    }

    // MARK: - Export

    func export(from store: ScanRootStore) async throws -> URL {
        let payload = await MainActor.run {
            ScopeExportPayload(
                version: ScopeExportPayload.currentVersion,
                exportedAt: Date(),
                roots: store.roots,
                markers: store.markers
            )
        }

        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601

        let data: Data
        do {
            data = try encoder.encode(payload)
        } catch {
            throw TransferError.encodingFailed
        }

        let destination = try await MainActor.run { () throws -> URL in
            let panel = NSSavePanel()
            panel.allowedContentTypes = [.json]
            panel.nameFieldStringValue = "idfwu-scope.json"
            panel.title = "Export IDFWU Scope"
            panel.message = "Save your scan roots and markers to a JSON file."
            guard panel.runModal() == .OK, let url = panel.url else {
                throw TransferError.userCancelled
            }
            return url
        }

        do {
            try data.write(to: destination, options: .atomic)
        } catch {
            throw TransferError.writeFailed(error.localizedDescription)
        }

        return destination
    }

    // MARK: - Import

    func `import`(into store: ScanRootStore, url: URL) async throws {
        let data: Data
        do {
            data = try Data(contentsOf: url)
        } catch {
            throw TransferError.readFailed(error.localizedDescription)
        }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        let payload: ScopeExportPayload
        do {
            payload = try decoder.decode(ScopeExportPayload.self, from: data)
        } catch {
            throw TransferError.decodingFailed(error.localizedDescription)
        }

        let mode = await MainActor.run { () -> ImportMode in
            let alert = NSAlert()
            alert.messageText = "Import Scope"
            alert.informativeText =
                "This file contains \(payload.roots.count) scan roots and \(payload.markers.count) markers. " +
                "Merge with your current scope or replace it entirely?"
            alert.addButton(withTitle: "Merge")
            alert.addButton(withTitle: "Replace")
            alert.addButton(withTitle: "Cancel")
            let response = alert.runModal()
            switch response {
            case .alertFirstButtonReturn: return .merge
            case .alertSecondButtonReturn: return .replace
            default: return .cancel
            }
        }

        switch mode {
        case .cancel:
            throw TransferError.userCancelled
        case .merge:
            await MainActor.run {
                store.merge(roots: payload.roots, markers: payload.markers)
            }
        case .replace:
            await MainActor.run {
                store.setRoots(payload.roots)
                store.setMarkers(payload.markers)
            }
        }
    }

    private enum ImportMode {
        case merge
        case replace
        case cancel
    }
}
