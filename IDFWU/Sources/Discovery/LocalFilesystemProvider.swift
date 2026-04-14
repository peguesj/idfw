import Foundation

struct LocalFilesystemProvider: ProjectProvider {
    let name = "filesystem"
    let scanRoots: [URL]
    let markers: [String]
    let maxDepth: Int

    private static let defaultMarkers: [String] = [
        ".claude/CLAUDE.md",
        "SKILL.md",
        "Package.swift",
        "pyproject.toml",
        "package.json",
        "mix.exs",
        ".idfw",
    ]

    private static let skipNames: Set<String> = [
        "node_modules", "build", "dist", ".build", "DerivedData",
        ".git", ".venv", "venv", "__pycache__", ".next", ".nuxt",
    ]

    init(
        scanRoots: [URL]? = nil,
        markers: [String]? = nil,
        maxDepth: Int = 2
    ) {
        self.scanRoots = scanRoots ?? [
            FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Developer")
        ]
        self.markers = markers ?? Self.defaultMarkers
        self.maxDepth = max(1, min(maxDepth, 5))
    }

    func discover() async throws -> [DiscoveredProject] {
        let fm = FileManager.default
        var results: [DiscoveredProject] = []
        var seenPaths = Set<String>()

        for root in scanRoots {
            guard isDirectory(root, fm: fm) else { continue }
            scan(dir: root, depth: 0, fm: fm, results: &results, seen: &seenPaths)
        }

        return results.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    func isAvailable() async -> Bool {
        !scanRoots.isEmpty && scanRoots.contains { FileManager.default.isReadableFile(atPath: $0.path) }
    }

    // MARK: - Private

    private func scan(
        dir: URL,
        depth: Int,
        fm: FileManager,
        results: inout [DiscoveredProject],
        seen: inout Set<String>
    ) {
        if depth > maxDepth { return }

        // If this dir itself is a project, capture it and stop descending.
        if depth > 0, hasMarker(at: dir, fm: fm) {
            let path = dir.path
            if !seen.contains(path) {
                seen.insert(path)
                results.append(makeProject(from: dir))
            }
            return
        }

        // Use the path-based API which is a thin wrapper around readdir()
        // — it never pre-fetches properties or follows symlinks, unlike the
        // URL-based variant which can stat() every entry for .skipsHiddenFiles.
        guard let names = try? fm.contentsOfDirectory(atPath: dir.path) else { return }

        for name in names {
            // Skip hidden files/dirs (readdir doesn't filter them)
            if name.hasPrefix(".") { continue }
            if Self.skipNames.contains(name) { continue }

            let child = dir.appendingPathComponent(name)

            // lstat()-based check: only descend into real directories.
            // Symlinks are skipped entirely — any target could be on an
            // unresponsive volume, iCloud, or network mount.
            guard isLocalDirectory(child, fm: fm) else { continue }

            if hasMarker(at: child, fm: fm) {
                let path = child.path
                if !seen.contains(path) {
                    seen.insert(path)
                    results.append(makeProject(from: child))
                }
                continue
            }

            scan(dir: child, depth: depth + 1, fm: fm, results: &results, seen: &seen)
        }
    }

    /// Uses stat() which follows symlinks — safe only for user-configured
    /// scan roots where following is intentional.
    private func isDirectory(_ url: URL, fm: FileManager) -> Bool {
        var isDir: ObjCBool = false
        return fm.fileExists(atPath: url.path, isDirectory: &isDir) && isDir.boolValue
    }

    /// Uses lstat() via attributesOfItem — never follows symlinks.
    /// Returns true only for real (non-symlink) directories. Symlinks are
    /// skipped entirely during discovery to avoid blocking on unresponsive
    /// targets (external volumes, iCloud, network mounts).
    private func isLocalDirectory(_ url: URL, fm: FileManager) -> Bool {
        guard let attrs = try? fm.attributesOfItem(atPath: url.path) else { return false }
        return attrs[.type] as? FileAttributeType == .typeDirectory
    }

    private func hasMarker(at dir: URL, fm: FileManager) -> Bool {
        markers.contains { fm.fileExists(atPath: dir.appendingPathComponent($0).path) }
    }

    private func makeProject(from dir: URL) -> DiscoveredProject {
        DiscoveredProject(
            id: dir.path,
            name: dir.lastPathComponent,
            path: dir.path,
            source: "filesystem",
            identifier: String?.none,
            planeId: String?.none,
            planeUrl: String?.none,
            apmPort: Int?.none,
            description: String?.none,
            stack: [String]?.none,
            lastActive: String?.none,
            metadata: [String: AnyCodableValue]?.none
        )
    }
}
