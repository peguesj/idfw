import Foundation

struct SourceConnectorConfig: Codable, Sendable {
    var kind: ConnectorKind
    var localPath: URL?
    var githubRepoURL: URL?
    var githubRef: String = "main"
    var authToken: String?

    enum ConnectorKind: String, Codable, CaseIterable, Sendable {
        case local
        case github
    }
}
