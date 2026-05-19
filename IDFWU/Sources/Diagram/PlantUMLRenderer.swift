import Foundation

/// Renders PlantUML / WebSequenceDiagrams source to SVG by shelling out to
/// the host `plantuml` binary (`-tsvg -pipe`). DRTW L1: `plantuml` (+ Java +
/// Graphviz) is installed; `.puml`, `.plantuml` and the repo's `@startuml`-
/// wrapped `.wsd` all render through the same pipe — no server, no library,
/// no custom deflate encoder.
///
/// `actor` for Sendable-safe `Process` use; read-before-wait ordering avoids
/// the classic pipe-buffer deadlock on large SVGs.
actor PlantUMLRenderer {
    enum RenderError: LocalizedError {
        case binaryNotFound
        case processFailed(String)
        case emptyOutput

        var errorDescription: String? {
            switch self {
            case .binaryNotFound:
                return "PlantUML is not installed (brew install plantuml). Showing source."
            case .processFailed(let detail):
                return "PlantUML failed: \(detail)"
            case .emptyOutput:
                return "PlantUML produced no SVG output."
            }
        }
    }

    private static let candidatePaths = [
        "/opt/homebrew/bin/plantuml",
        "/usr/local/bin/plantuml",
        "/usr/bin/plantuml"
    ]

    static func isAvailable() -> Bool { resolveBinary() != nil }

    private static func resolveBinary() -> URL? {
        let fm = FileManager.default
        for path in candidatePaths where fm.isExecutableFile(atPath: path) {
            return URL(fileURLWithPath: path)
        }
        let env = ProcessInfo.processInfo.environment
        let dirs = (env["PATH"] ?? "").split(separator: ":").map(String.init)
            + ["/opt/homebrew/bin", "/usr/local/bin"]
        for dir in dirs {
            let candidate = (dir as NSString).appendingPathComponent("plantuml")
            if fm.isExecutableFile(atPath: candidate) {
                return URL(fileURLWithPath: candidate)
            }
        }
        return nil
    }

    func renderSVG(source: String) async throws -> String {
        guard let bin = Self.resolveBinary() else { throw RenderError.binaryNotFound }

        let process = Process()
        process.executableURL = bin
        process.arguments = ["-tsvg", "-pipe", "-charset", "UTF-8"]

        let stdin = Pipe(), stdout = Pipe(), stderr = Pipe()
        process.standardInput = stdin
        process.standardOutput = stdout
        process.standardError = stderr

        try process.run()
        stdin.fileHandleForWriting.write(Data(source.utf8))
        try? stdin.fileHandleForWriting.close()

        // Read fully BEFORE waitUntilExit — large SVGs exceed the pipe buffer.
        let outData = stdout.fileHandleForReading.readDataToEndOfFile()
        let errData = stderr.fileHandleForReading.readDataToEndOfFile()
        process.waitUntilExit()

        guard process.terminationStatus == 0 else {
            let detail = String(decoding: errData, as: UTF8.self)
                .trimmingCharacters(in: .whitespacesAndNewlines)
            throw RenderError.processFailed(detail.isEmpty ? "exit \(process.terminationStatus)" : detail)
        }
        let svg = String(decoding: outData, as: UTF8.self)
        guard svg.contains("<svg") else { throw RenderError.emptyOutput }
        return svg
    }
}
