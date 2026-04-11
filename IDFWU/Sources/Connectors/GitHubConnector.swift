import Foundation

struct GitHubConnector: SourceConnector {
    let config: SourceConnectorConfig
    let owner: String
    let repo: String
    let allowedExtensions: Set<String>
    private let client: GitHubAPIClient

    init(
        owner: String,
        repo: String,
        ref: String = "main",
        token: String? = nil,
        allowedExtensions: Set<String> = [".json", ".jsonc"]
    ) {
        self.owner = owner
        self.repo = repo
        self.allowedExtensions = allowedExtensions
        self.client = GitHubAPIClient(token: token)
        self.config = SourceConnectorConfig(
            kind: .github,
            githubRepoURL: URL(string: "https://github.com/\(owner)/\(repo)"),
            githubRef: ref,
            authToken: token
        )
    }

    func validate() async throws {
        _ = try await client.tree(owner: owner, repo: repo, ref: config.githubRef)
    }

    func documents() -> AsyncThrowingStream<RawDocument, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    let entries = try await client.tree(owner: owner, repo: repo, ref: config.githubRef)

                    let schemaFiles = entries.filter { entry in
                        guard entry.type == "blob" else { return false }
                        let ext = "." + (entry.path as NSString).pathExtension.lowercased()
                        return allowedExtensions.contains(ext)
                    }

                    for entry in schemaFiles {
                        if Task.isCancelled { break }

                        do {
                            let data = try await client.rawContent(
                                owner: owner,
                                repo: repo,
                                path: entry.path,
                                ref: config.githubRef
                            )

                            let sourceURL = URL(string: "https://github.com/\(owner)/\(repo)/blob/\(config.githubRef)/\(entry.path)")
                                ?? URL(string: "https://github.com")!

                            let doc = RawDocument(
                                sourceURL: sourceURL,
                                relativePath: entry.path,
                                data: data,
                                connectorKind: .github
                            )
                            continuation.yield(doc)
                        } catch {
                            continue
                        }
                    }

                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
        }
    }
}
