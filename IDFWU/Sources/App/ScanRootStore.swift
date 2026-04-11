import Foundation
import Observation

/// Persisted list of directories to scan for IDFW projects.
/// Stored in UserDefaults as a JSON-encoded `[ScanRoot]`.
@MainActor
@Observable
final class ScanRootStore {
    private static let defaultsKey = "idfwu.scanRoots.v1"
    private static let depthKey = "idfwu.scanRoots.maxDepth"
    private static let markerKey = "idfwu.scanRoots.markers"

    /// Shared instance wired into commands and transfer helpers.
    /// The same instance is injected into SwiftUI as `@State` on `IDFWUApp`.
    static let shared = ScanRootStore()

    var roots: [ScanRoot] = []
    var maxDepth: Int = 2
    var markers: [String] = ScanRootStore.defaultMarkers

    static let defaultMarkers: [String] = [
        ".claude/CLAUDE.md",
        "SKILL.md",
        "Package.swift",
        "pyproject.toml",
        "package.json",
        "mix.exs",
        ".idfw",
    ]

    /// Canonical presets for the "Add Preset" menu.
    static let presets: [ScanRoot] = {
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        return [
            ScanRoot(path: "\(home)/Developer", label: "Developer"),
            ScanRoot(path: "\(home)/.claude/skills", label: "Claude Skills"),
            ScanRoot(path: "\(home)/.claude/projects", label: "Claude Projects"),
            ScanRoot(path: "\(home)/Developer/idfw", label: "IDFW System"),
            ScanRoot(path: "\(home)/Developer/idfw-idfwu", label: "IDFWU Swift"),
        ]
    }()

    init() {
        load()
    }

    // MARK: - Mutations

    func add(_ root: ScanRoot) {
        guard !roots.contains(where: { $0.path == root.path }) else { return }
        roots.append(root)
        save()
    }

    /// Convenience for command-menu integration: accepts a folder URL from an
    /// NSOpenPanel callback.
    func addRoot(url: URL) {
        let label = url.lastPathComponent.isEmpty ? url.path : url.lastPathComponent
        add(ScanRoot(path: url.path, label: label))
    }

    func remove(id: UUID) {
        roots.removeAll { $0.id == id }
        save()
    }

    /// Supports SwiftUI `.onMove` drag-reordering inside a `ForEach`.
    func move(fromOffsets source: IndexSet, toOffsets destination: Int) {
        roots.move(fromOffsets: source, toOffset: destination)
        save()
    }

    func toggleEnabled(id: UUID) {
        guard let idx = roots.firstIndex(where: { $0.id == id }) else { return }
        roots[idx].isEnabled.toggle()
        save()
    }

    func setLabel(id: UUID, label: String) {
        guard let idx = roots.firstIndex(where: { $0.id == id }) else { return }
        roots[idx].label = label
        save()
    }

    func setPath(id: UUID, path: String) {
        guard let idx = roots.firstIndex(where: { $0.id == id }) else { return }
        roots[idx].path = path
        save()
    }

    /// Per-root max-depth override. `nil` falls back to the global `maxDepth`.
    func setMaxDepth(id: UUID, depth: Int?) {
        guard let idx = roots.firstIndex(where: { $0.id == id }) else { return }
        if let depth {
            roots[idx].maxDepth = max(1, min(depth, 5))
        } else {
            roots[idx].maxDepth = nil
        }
        save()
    }

    func setMaxDepth(_ value: Int) {
        maxDepth = max(1, min(value, 5))
        UserDefaults.standard.set(maxDepth, forKey: Self.depthKey)
    }

    // MARK: - Markers

    func addMarker(_ marker: String) {
        let trimmed = marker.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, !markers.contains(trimmed) else { return }
        markers.append(trimmed)
        saveMarkers()
    }

    func removeMarker(_ marker: String) {
        markers.removeAll { $0 == marker }
        saveMarkers()
    }

    func resetMarkers() {
        markers = Self.defaultMarkers
        saveMarkers()
    }

    func saveMarkers() {
        guard let data = try? JSONEncoder().encode(markers) else { return }
        UserDefaults.standard.set(data, forKey: Self.markerKey)
    }

    /// Replaces the markers list wholesale (used by ScopeTransferHandler).
    func setMarkers(_ newMarkers: [String]) {
        markers = newMarkers
        saveMarkers()
    }

    /// Replaces the root list wholesale (used by ScopeTransferHandler).
    func setRoots(_ newRoots: [ScanRoot]) {
        roots = newRoots
        save()
    }

    /// Merges another set of roots + markers (used by ScopeTransferHandler).
    func merge(roots otherRoots: [ScanRoot], markers otherMarkers: [String]) {
        for root in otherRoots where !roots.contains(where: { $0.path == root.path }) {
            roots.append(root)
        }
        for marker in otherMarkers where !markers.contains(marker) {
            markers.append(marker)
        }
        save()
        saveMarkers()
    }

    /// Active (enabled + path-existing) roots as file URLs.
    var activeRootURLs: [URL] {
        let fm = FileManager.default
        return roots
            .filter { $0.isEnabled }
            .compactMap {
                let url = URL(fileURLWithPath: $0.path)
                return fm.isReadableFile(atPath: url.path) || isDirectory(url) ? url : nil
            }
    }

    /// Effective depth for a particular root (per-root override or global).
    func effectiveDepth(for root: ScanRoot) -> Int {
        root.maxDepth ?? maxDepth
    }

    // MARK: - Persistence

    private func load() {
        let defaults = UserDefaults.standard
        if let data = defaults.data(forKey: Self.defaultsKey),
           let decoded = try? JSONDecoder().decode([ScanRoot].self, from: data) {
            roots = decoded
        } else {
            // Seed first-run defaults with the home Developer dir AND idfw dir.
            let home = FileManager.default.homeDirectoryForCurrentUser.path
            roots = [
                ScanRoot(path: "\(home)/Developer", label: "Developer"),
                ScanRoot(path: "\(home)/Developer/idfw", label: "IDFW"),
            ]
            save()
        }

        let storedDepth = defaults.integer(forKey: Self.depthKey)
        maxDepth = storedDepth > 0 ? storedDepth : 2

        if let data = defaults.data(forKey: Self.markerKey),
           let decoded = try? JSONDecoder().decode([String].self, from: data) {
            markers = decoded
        }
    }

    private func save() {
        guard let data = try? JSONEncoder().encode(roots) else { return }
        UserDefaults.standard.set(data, forKey: Self.defaultsKey)
    }

    private func isDirectory(_ url: URL) -> Bool {
        var isDir: ObjCBool = false
        return FileManager.default.fileExists(atPath: url.path, isDirectory: &isDir) && isDir.boolValue
    }
}

/// A single scan root with enablement flag and optional per-root depth override.
struct ScanRoot: Identifiable, Codable, Hashable {
    var id: UUID = UUID()
    var path: String
    var label: String
    var isEnabled: Bool = true
    /// Per-root override for scan depth. `nil` means "inherit from global".
    var maxDepth: Int?

    init(
        id: UUID = UUID(),
        path: String,
        label: String,
        isEnabled: Bool = true,
        maxDepth: Int? = nil
    ) {
        self.id = id
        self.path = path
        self.label = label
        self.isEnabled = isEnabled
        self.maxDepth = maxDepth
    }

    // Custom decoder so old persisted JSON (no `maxDepth` key) decodes cleanly.
    private enum CodingKeys: String, CodingKey {
        case id, path, label, isEnabled, maxDepth
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        self.id = try c.decodeIfPresent(UUID.self, forKey: .id) ?? UUID()
        self.path = try c.decode(String.self, forKey: .path)
        self.label = try c.decode(String.self, forKey: .label)
        self.isEnabled = try c.decodeIfPresent(Bool.self, forKey: .isEnabled) ?? true
        self.maxDepth = try c.decodeIfPresent(Int.self, forKey: .maxDepth)
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(id, forKey: .id)
        try c.encode(path, forKey: .path)
        try c.encode(label, forKey: .label)
        try c.encode(isEnabled, forKey: .isEnabled)
        try c.encodeIfPresent(maxDepth, forKey: .maxDepth)
    }
}
