import Foundation
import SwiftData

@Model
final class Project {
    @Attribute(.unique) var id: UUID
    var name: String
    var connectorConfigData: Data
    var lastSynced: Date?

    @Relationship(deleteRule: .cascade, inverse: \SchemaDocument.project)
    var documents: [SchemaDocument]

    var connectorConfig: SourceConnectorConfig? {
        get {
            try? JSONDecoder().decode(SourceConnectorConfig.self, from: connectorConfigData)
        }
        set {
            if let value = newValue, let encoded = try? JSONEncoder().encode(value) {
                connectorConfigData = encoded
            }
        }
    }

    init(
        id: UUID = UUID(),
        name: String,
        connectorConfig: SourceConnectorConfig,
        lastSynced: Date? = nil,
        documents: [SchemaDocument] = []
    ) {
        self.id = id
        self.name = name
        self.connectorConfigData = (try? JSONEncoder().encode(connectorConfig)) ?? Data()
        self.lastSynced = lastSynced
        self.documents = documents
    }
}
