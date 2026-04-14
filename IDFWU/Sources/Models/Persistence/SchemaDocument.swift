import Foundation
import SwiftData

@Model
final class SchemaDocument {
    @Attribute(.unique) var id: UUID
    var docId: String
    var schemaType: String
    var jsonPayload: Data
    var fetchedAt: Date
    var title: String?

    var project: Project?

    var type: IDEASchemaType? {
        IDEASchemaType(rawValue: schemaType)
    }

    init(
        id: UUID = UUID(),
        docId: String,
        schemaType: IDEASchemaType,
        jsonPayload: Data,
        fetchedAt: Date = .now,
        title: String? = nil
    ) {
        self.id = id
        self.docId = docId
        self.schemaType = schemaType.rawValue
        self.jsonPayload = jsonPayload
        self.fetchedAt = fetchedAt
        self.title = title
    }
}
