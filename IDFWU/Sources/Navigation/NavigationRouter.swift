import SwiftUI

@Observable
final class NavigationRouter {
    var selectedProjectID: String?
    var selectedDocumentID: UUID?
    var selectedDocument: ProjectDocument?
    var isEventStreamPanelVisible: Bool = false
    var columnVisibility: NavigationSplitViewVisibility = .all

    var hasProjectSelection: Bool { selectedProjectID != nil }
    var hasDocumentSelection: Bool { selectedDocumentID != nil }

    func clearSelection() {
        selectedDocument = nil
        selectedDocumentID = nil
        selectedProjectID = nil
    }

    func selectProject(_ id: String) {
        selectedProjectID = id
        selectedDocumentID = nil
        selectedDocument = nil
    }

    /// Project-aware overload that also records the selection in
    /// `RecentProjectsStore` so the menubar's "Recent Projects" section can
    /// surface it later.
    @MainActor
    func selectProject(_ project: DiscoveredProject) {
        selectProject(project.id)
        RecentProjectsStore.shared.record(
            id: project.id,
            name: project.name,
            path: project.path
        )
    }

    func selectDocument(_ id: UUID) {
        selectedDocumentID = id
    }

    func selectDocument(_ document: ProjectDocument) {
        selectedDocumentID = document.id
        selectedDocument = document
    }
}
