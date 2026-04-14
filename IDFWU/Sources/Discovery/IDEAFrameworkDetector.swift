import Foundation

/// Status of an IDEA framework installation inside a project directory.
///
/// `.initialized` means the project contains one or more hard signals that it
/// is wired into the IDFW / IDEA framework (documents, schemas, FORCE config,
/// etc.). `.uninitialized` means none of the expected markers were found —
/// these projects can be bootstrapped via `/idea new`.
enum IDEAFrameworkStatus: Sendable, Hashable {
    case initialized(IDEAFrameworkInventory)
    case uninitialized
    case unknown
}

/// Summary of IDEA artifacts discovered inside a project. Used to surface a
/// compact badge in the sidebar and a richer banner in the document list.
struct IDEAFrameworkInventory: Sendable, Hashable {
    var ideaDirectory: Bool
    var configFile: String?
    var schemaCount: Int
    var documentCount: Int
    var diagramCount: Int
    var forcePresent: Bool

    var signalCount: Int {
        var count = 0
        if ideaDirectory { count += 1 }
        if configFile != nil { count += 1 }
        if schemaCount > 0 { count += 1 }
        if documentCount > 0 { count += 1 }
        if diagramCount > 0 { count += 1 }
        if forcePresent { count += 1 }
        return count
    }

    var isInitialized: Bool { signalCount > 0 }

    static let empty = IDEAFrameworkInventory(
        ideaDirectory: false,
        configFile: nil,
        schemaCount: 0,
        documentCount: 0,
        diagramCount: 0,
        forcePresent: false
    )
}

/// Detects whether a project directory has the IDEA / IDFW framework
/// initialized. Pure and stateless — safe to share across views.
actor IDEAFrameworkDetector {

    /// IDEA document extensions (per IDFW schema catalog: IDDA, IDDV, IDFPJ, IDFW).
    private static let ideaDocumentSuffixes: [String] = [
        ".idda.json", ".iddv.json", ".idfpj.json", ".idfw.json",
        ".IDDA.json", ".IDDV.json", ".IDFPJ.json", ".IDFW.json",
    ]

    /// Diagram files the IDEA framework understands. Mermaid + PlantUML are
    /// the dominant formats emitted by `/idea define` and `/idea rev-eng`.
    private static let diagramSuffixes: [String] = [
        ".mmd", ".mermaid", ".puml", ".plantuml",
    ]

    /// Filenames that mark a project as IDFW-bootstrapped.
    private static let configMarkers: [String] = [
        "idfw.config.yaml",
        "idfw.config.yml",
        "idfw.config.json",
        ".idfw",
        "idfw.yaml",
    ]

    func detect(projectPath: String) async -> IDEAFrameworkStatus {
        let fm = FileManager.default
        let root = (projectPath as NSString).standardizingPath
        var isDir: ObjCBool = false
        guard fm.fileExists(atPath: root, isDirectory: &isDir), isDir.boolValue else {
            return .unknown
        }

        var inventory = IDEAFrameworkInventory.empty

        // 1. `.idea/` marker directory (distinct from JetBrains — we only care
        //    if it contains IDEA framework JSON, not an .iml file).
        let ideaDir = (root as NSString).appendingPathComponent(".idea")
        if fm.fileExists(atPath: ideaDir, isDirectory: &isDir), isDir.boolValue {
            if let contents = try? fm.contentsOfDirectory(atPath: ideaDir),
               contents.contains(where: { $0.hasSuffix(".json") || $0.hasSuffix(".yaml") }) {
                inventory.ideaDirectory = true
            }
        }

        // 2. Top-level config markers.
        for marker in Self.configMarkers {
            let path = (root as NSString).appendingPathComponent(marker)
            if fm.fileExists(atPath: path) {
                inventory.configFile = marker
                break
            }
        }

        // 3. FORCE framework — either `.force/` project runtime or `force/` package.
        for dir in [".force", "force"] {
            let path = (root as NSString).appendingPathComponent(dir)
            if fm.fileExists(atPath: path, isDirectory: &isDir), isDir.boolValue {
                inventory.forcePresent = true
                break
            }
        }

        // 4. Shallow scan (1-level deep) for schemas, IDEA documents, diagrams.
        //    We deliberately stop at one level to keep the detector cheap — the
        //    full scan lives in `ProjectDocumentScanner`.
        let topLevel = (try? fm.contentsOfDirectory(atPath: root)) ?? []
        let idfwSubdir = topLevel.contains("idfw")
            ? (root as NSString).appendingPathComponent("idfw")
            : nil
        let searchRoots = [root] + (idfwSubdir.map { [$0] } ?? [])

        for searchRoot in searchRoots {
            let items = (try? fm.contentsOfDirectory(atPath: searchRoot)) ?? []
            for item in items {
                let lower = item.lowercased()
                // Schemas
                if lower.hasSuffix(".schema.json") || lower.hasSuffix(".schemas.json") {
                    inventory.schemaCount += 1
                }
                // IDEA documents
                if Self.ideaDocumentSuffixes.contains(where: { lower.hasSuffix($0.lowercased()) }) {
                    inventory.documentCount += 1
                }
                // Diagrams
                if Self.diagramSuffixes.contains(where: { lower.hasSuffix($0) }) {
                    inventory.diagramCount += 1
                }
            }
        }

        // 5. `docs/diagrams/` and `diagrams/` conventionally hold Mermaid files.
        for dir in ["docs/diagrams", "diagrams"] {
            let path = (root as NSString).appendingPathComponent(dir)
            if fm.fileExists(atPath: path, isDirectory: &isDir), isDir.boolValue {
                let items = (try? fm.contentsOfDirectory(atPath: path)) ?? []
                inventory.diagramCount += items.filter { name in
                    Self.diagramSuffixes.contains(where: { name.lowercased().hasSuffix($0) })
                }.count
            }
        }

        return inventory.isInitialized ? .initialized(inventory) : .uninitialized
    }
}
