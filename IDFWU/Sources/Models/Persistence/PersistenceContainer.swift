import Foundation
import SwiftData

enum PersistenceContainer {
    nonisolated(unsafe) static var shared: ModelContainer = {
        let schema = Schema([Project.self, SchemaDocument.self])
        let configuration = ModelConfiguration("IDFWU", isStoredInMemoryOnly: false)
        do {
            return try ModelContainer(for: schema, configurations: [configuration])
        } catch {
            fatalError("Failed to create ModelContainer: \(error)")
        }
    }()

    static func inMemory() -> ModelContainer {
        let schema = Schema([Project.self, SchemaDocument.self])
        let configuration = ModelConfiguration("IDFWUInMemory", isStoredInMemoryOnly: true)
        do {
            return try ModelContainer(for: schema, configurations: [configuration])
        } catch {
            fatalError("Failed to create in-memory ModelContainer: \(error)")
        }
    }
}
