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

        guard let children = try? fm.contentsOfDirectory(
            at: dir,
            includingPropertiesForKeys: [.isDirectoryKey],
            options: [.skipsHiddenFiles]
        ) else { return }

        for child in children {
            guard isDirectory(child, fm: fm) else { continue }
            let name = child.lastPathComponent
            if Self.skipNames.contains(name) { continue }

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

    private func isDirectory(_ url: URL, fm: FileManager) -> Bool {
        var isDir: ObjCBool = false
        return fm.fileExists(atPath: url.path, isDirectory: &isDir) && isDir.boolValue
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
