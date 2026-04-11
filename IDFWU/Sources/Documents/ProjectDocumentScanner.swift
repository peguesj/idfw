import Foundation

actor ProjectDocumentScanner {

    func scan(projectPath: String) async -> [ProjectDocument] {
        let fm = FileManager.default
        let root = (projectPath as NSString).standardizingPath
        var results: [ProjectDocument] = []

        // Schema files
        results += collectGlob(root: root, patterns: ["*.schema.json", "*.schemas.json"], type: .schema, fm: fm)

        // FORCE framework
        let forcePath = (root as NSString).appendingPathComponent(".force")
        if fm.fileExists(atPath: forcePath) {
            results += collectRecursive(directory: forcePath, ext: "json", type: .force, fm: fm)
        }
        let forcePackagePath = (root as NSString).appendingPathComponent("force")
        if fm.fileExists(atPath: forcePackagePath) {
            results += collectRecursive(directory: forcePackagePath, ext: "json", type: .force, fm: fm)
        }

        // Config files
        let configNames = ["pyproject.toml", "Package.swift", "mix.exs", "package.json", "Cargo.toml"]
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

        // Documentation
        let docNames = ["README.md", "CHANGELOG.md", "CLAUDE.md", "LICENSE", "CONTRIBUTING.md"]
        for name in docNames {
            let fullPath = (root as NSString).appendingPathComponent(name)
            if let doc = documentAt(path: fullPath, type: .doc, fm: fm) {
                results.append(doc)
            }
        }

        // Also scan for schema files in subdirectories (1 level deep)
        if let topLevel = try? fm.contentsOfDirectory(atPath: root) {
            for dir in topLevel where !dir.hasPrefix(".") {
                let subdir = (root as NSString).appendingPathComponent(dir)
                var isDir: ObjCBool = false
                if fm.fileExists(atPath: subdir, isDirectory: &isDir), isDir.boolValue {
                    results += collectGlob(root: subdir, patterns: ["*.schema.json", "*.schemas.json"], type: .schema, fm: fm)
                }
            }
        }

        return results
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
