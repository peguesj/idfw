import Foundation

struct RawDocument: Identifiable, Sendable {
    let id: UUID
    let sourceURL: URL
    let relativePath: String
    let data: Data
    let connectorKind: SourceConnectorConfig.ConnectorKind
    let detectedType: IDEASchemaType?
    let fetchedAt: Date

    init(
        id: UUID = UUID(),
        sourceURL: URL,
        relativePath: String = "",
        data: Data,
        connectorKind: SourceConnectorConfig.ConnectorKind = .local,
        detectedType: IDEASchemaType? = nil,
        fetchedAt: Date = .now
    ) {
        self.id = id
        self.sourceURL = sourceURL
        self.relativePath = relativePath
        self.data = data
        self.connectorKind = connectorKind
        self.detectedType = detectedType
        self.fetchedAt = fetchedAt
    }
}
