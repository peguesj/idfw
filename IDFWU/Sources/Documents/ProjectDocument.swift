import Foundation

enum ProjectDocumentType: String, CaseIterable, Sendable {
    case schema = "Schemas"
    case force = "FORCE"
    case config = "Config"
    case doc = "Docs"
}

struct ProjectDocument: Identifiable, Hashable, Sendable {
    let id: UUID
    let name: String
    let path: String
    let type: ProjectDocumentType
    let size: Int64
    let modifiedDate: Date

    var relativePath: String {
        // Show path relative to project root for display
        if let range = path.range(of: "/", options: .backwards) {
            return String(path[range.lowerBound...])
        }
        return name
    }
}
