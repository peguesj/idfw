import Foundation
import SwiftData
import Observation

@Observable
final class ProjectListViewModel {
    var projects: [Project] = []
    var isLoading = false
    var syncError: String?

    func fetch(context: ModelContext) {
        let descriptor = FetchDescriptor<Project>(sortBy: [SortDescriptor(\.name)])
        projects = (try? context.fetch(descriptor)) ?? []
    }

    func addProject(name: String, config: SourceConnectorConfig, context: ModelContext) {
        let project = Project(name: name, connectorConfig: config)
        context.insert(project)
        try? context.save()
        fetch(context: context)
    }

    func removeProject(_ project: Project, context: ModelContext) {
        context.delete(project)
        try? context.save()
        fetch(context: context)
    }

    func syncProject(_ project: Project, connector: SourceConnector, context: ModelContext) async {
        isLoading = true
        syncError = nil
        defer { isLoading = false }

        do {
            for try await raw in connector.documents() {
                let ideaDoc = try IDEADocumentParser.parse(raw)
                let docId = ideaDoc.docId
                let schemaType = ideaDoc.schemaType

                let existing = project.documents.first { $0.docId == docId }
                if let existing {
                    existing.schemaType = schemaType.rawValue
                    existing.jsonPayload = raw.data
                    existing.fetchedAt = .now
                    existing.title = ideaDoc.title
                } else {
                    let doc = SchemaDocument(
                        docId: docId,
                        schemaType: schemaType,
                        jsonPayload: raw.data,
                        title: ideaDoc.title
                    )
                    doc.project = project
                    context.insert(doc)
                }
            }
            project.lastSynced = .now
            try? context.save()
            fetch(context: context)
        } catch {
            syncError = error.localizedDescription
        }
    }
}
