import Foundation

struct LocalFileConnector: SourceConnector {
    let config: SourceConnectorConfig
    let allowedExtensions: Set<String>

    init(rootURL: URL, allowedExtensions: Set<String> = [".json", ".jsonc"]) {
        self.config = SourceConnectorConfig(kind: .local, localPath: rootURL)
        self.allowedExtensions = allowedExtensions
    }

    func validate() async throws {
        guard let rootURL = config.localPath else {
            throw NetworkError.invalidURL
        }
        var isDir: ObjCBool = false
        guard FileManager.default.fileExists(atPath: rootURL.path(percentEncoded: false), isDirectory: &isDir),
              isDir.boolValue else {
            throw NetworkError.invalidURL
        }
    }

    func documents() -> AsyncThrowingStream<RawDocument, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    try await validate()
                } catch {
                    continuation.finish(throwing: error)
                    return
                }

                guard let rootURL = config.localPath else {
                    continuation.finish(throwing: NetworkError.invalidURL)
                    return
                }

                let manager = FileManager.default
                guard let enumerator = manager.enumerator(
                    at: rootURL,
                    includingPropertiesForKeys: [.isRegularFileKey],
                    options: [.skipsHiddenFiles]
                ) else {
                    continuation.finish()
                    return
                }

                let allFiles = enumerator.compactMap { $0 as? URL }
                for fileURL in allFiles {
                    if Task.isCancelled { break }

                    let ext = "." + fileURL.pathExtension.lowercased()
                    guard allowedExtensions.contains(ext) else { continue }

                    guard let resourceValues = try? fileURL.resourceValues(forKeys: [.isRegularFileKey]),
                          resourceValues.isRegularFile == true else { continue }

                    do {
                        let data = try Data(contentsOf: fileURL)
                        let relative = fileURL.path(percentEncoded: false)
                            .replacingOccurrences(of: rootURL.path(percentEncoded: false), with: "")
                            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))

                        let doc = RawDocument(
                            sourceURL: fileURL,
                            relativePath: relative,
                            data: data,
                            connectorKind: .local
                        )
                        continuation.yield(doc)
                    } catch {
                        continue
                    }
                }

                continuation.finish()
            }
        }
    }
}
