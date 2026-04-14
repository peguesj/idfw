import Foundation

enum ProjectDocumentType: String, CaseIterable, Sendable {
    case schema  = "Schemas"
    case force   = "FORCE"
    case config  = "Config"
    case doc     = "Docs"
    case diagram = "Diagrams"
    case idea    = "IDEA"
}

struct ProjectDocument: Identifiable, Hashable, Sendable {
    let id: UUID
    let name: String
    let path: String
    let type: ProjectDocumentType
    let size: Int64
    let modifiedDate: Date

    /// The IDEA phase (I/D/E/A) this artifact belongs to. Derived from the
    /// filename and type via `IDEAPhaseClassifier` so grouping logic in the UI
    /// can rely on a single, pre-computed value.
    var phase: IDEAPhase { IDEAPhaseClassifier.phase(for: self) }

    var relativePath: String {
        // Show path relative to project root for display
        if let range = path.range(of: "/", options: .backwards) {
            return String(path[range.lowerBound...])
        }
        return name
    }
}
