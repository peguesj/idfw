import Foundation

actor ProjectDocumentScanner {

    func scan(projectPath: String) async -> [ProjectDocument] {
        let fm = FileManager.default
        let root = (projectPath as NSString).standardizingPath
        var results: [ProjectDocument] = []

        // IDEA typed documents (*.idfw.json, *.iddv.json, *.idda.json, *.idfpj.json ...)
        results += collectGlob(
            root: root,
            patterns: [
                "*.idfw.json", "*.iddv.json", "*.iddg.json", "*.iddc.json",
                "*.idda.json", "*.idfpj.json", "*.idpc.json", "*.idpg.json", "*.ddd.json",
            ],
            type: .idea, fm: fm
        )

        // Schema files
        results += collectGlob(root: root, patterns: ["*.schema.json", "*.schemas.json"], type: .schema, fm: fm)

        // FORCE framework (both project runtime and importable package).
        for dir in [".force", "force"] {
            let path = (root as NSString).appendingPathComponent(dir)
            if fm.fileExists(atPath: path) {
                results += collectRecursive(directory: path, ext: "json", type: .force, fm: fm)
                results += collectRecursive(directory: path, ext: "yaml", type: .force, fm: fm)
            }
        }

        // Diagrams — top-level + conventional docs/diagrams/ and diagrams/ dirs.
        let diagramExts = ["mmd", "mermaid", "puml", "plantuml"]
        for ext in diagramExts {
            results += collectGlob(root: root, patterns: ["*.\(ext)"], type: .diagram, fm: fm)
        }
        for dir in ["docs/diagrams", "diagrams"] {
            let path = (root as NSString).appendingPathComponent(dir)
            if fm.fileExists(atPath: path) {
                for ext in diagramExts {
                    results += collectRecursive(directory: path, ext: ext, type: .diagram, fm: fm)
                }
            }
        }

        // Config files
        let configNames = [
            "pyproject.toml", "Package.swift", "mix.exs", "package.json", "Cargo.toml",
            "idfw.config.yaml", "idfw.config.yml", "idfw.config.json", "idfw.yaml",
        ]
        for name in configNames {
            let fullPath = (root as NSString).appendingPathComponent(name)
            if let doc = documentAt(path: fullPath, type: .config, fm: fm) {
                results.append(doc)
            }
        }
        // .claude/CLAUDE.md
        let claudeMd = (root as NSString).appendingPathComponent(".claude/CLAUDE.md")
        if let doc = documentAt(path: claudeMd, type: .config, fm: fm) {
            results.append(doc)
        }

        // Top-level documentation
        let docNames = ["README.md", "CHANGELOG.md", "CLAUDE.md", "LICENSE", "CONTRIBUTING.md"]
        for name in docNames {
            let fullPath = (root as NSString).appendingPathComponent(name)
            if let doc = documentAt(path: fullPath, type: .doc, fm: fm) {
                results.append(doc)
            }
        }

        // Markdown inside docs/ (one level deep — avoids pulling in huge wikis).
        let docsDir = (root as NSString).appendingPathComponent("docs")
        if fm.fileExists(atPath: docsDir) {
            results += collectGlob(root: docsDir, patterns: ["*.md"], type: .doc, fm: fm)
        }

        // Also scan for IDEA docs + schema files in subdirectories (1 level deep).
        if let topLevel = try? fm.contentsOfDirectory(atPath: root) {
            for dir in topLevel where !dir.hasPrefix(".") {
                let subdir = (root as NSString).appendingPathComponent(dir)
                var isDir: ObjCBool = false
                if fm.fileExists(atPath: subdir, isDirectory: &isDir), isDir.boolValue {
                    results += collectGlob(root: subdir, patterns: ["*.schema.json", "*.schemas.json"], type: .schema, fm: fm)
                    results += collectGlob(
                        root: subdir,
                        patterns: [
                            "*.idfw.json", "*.iddv.json", "*.iddg.json", "*.iddc.json",
                            "*.idda.json", "*.idfpj.json", "*.idpc.json", "*.idpg.json",
                        ],
                        type: .idea, fm: fm
                    )
                }
            }
        }

        // Deduplicate by path (diagrams under docs/diagrams and top-level could overlap).
        var seen = Set<String>()
        return results.filter { seen.insert($0.path).inserted }
    }

    // MARK: - Helpers

    private func collectGlob(root: String, patterns: [String], type: ProjectDocumentType, fm: FileManager) -> [ProjectDocument] {
        var results: [ProjectDocument] = []
        guard let contents = try? fm.contentsOfDirectory(atPath: root) else { return results }
        for item in contents {
            for pattern in patterns {
                if matchesGlob(item, pattern: pattern) {
                    let fullPath = (root as NSString).appendingPathComponent(item)
                    if let doc = documentAt(path: fullPath, type: type, fm: fm) {
                        results.append(doc)
                    }
                }
            }
        }
        return results
    }

    private func collectRecursive(directory: String, ext: String, type: ProjectDocumentType, fm: FileManager) -> [ProjectDocument] {
        var results: [ProjectDocument] = []
        guard let enumerator = fm.enumerator(atPath: directory) else { return results }
        while let item = enumerator.nextObject() as? String {
            if (item as NSString).pathExtension == ext {
                let fullPath = (directory as NSString).appendingPathComponent(item)
                if let doc = documentAt(path: fullPath, type: type, fm: fm) {
                    results.append(doc)
                }
            }
        }
        return results
    }

    private func documentAt(path: String, type: ProjectDocumentType, fm: FileManager) -> ProjectDocument? {
        guard fm.fileExists(atPath: path),
              let attrs = try? fm.attributesOfItem(atPath: path) else { return nil }
        let size = (attrs[.size] as? Int64) ?? 0
        let modified = (attrs[.modificationDate] as? Date) ?? Date.distantPast
        let name = (path as NSString).lastPathComponent
        return ProjectDocument(id: UUID(), name: name, path: path, type: type, size: size, modifiedDate: modified)
    }

    private func matchesGlob(_ filename: String, pattern: String) -> Bool {
        // Simple *.ext matching
        if pattern.hasPrefix("*") {
            let suffix = String(pattern.dropFirst())
            return filename.hasSuffix(suffix)
        }
        return filename == pattern
    }
}
