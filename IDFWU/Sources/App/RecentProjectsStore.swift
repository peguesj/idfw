import Foundation
import Observation

/// Lightweight stub representation of a recently selected project.
///
/// Stored independently of the SwiftData `@Model` so the menubar / recent-list
/// UI can surface recently selected projects without needing to load the full
/// discovery manager or the persistent store.
struct RecentProjectStub: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let path: String?
    let recordedAt: Date
}

/// Persists the most-recently-selected projects as lightweight stubs in
/// `UserDefaults`. Up to `max` entries are retained, de-duplicated by id,
/// newest-first.
///
/// Call sites:
///  - `NavigationRouter.selectProject(_:)` records on selection
///  - `MenuBarView` reads `recent` to render the recent-projects section
@MainActor
@Observable
final class RecentProjectsStore {
    static let shared = RecentProjectsStore()

    private(set) var recent: [RecentProjectStub] = []
    private let key = "idfwu.recentProjects.v1"
    private let max = 5

    private init() {
        if let data = UserDefaults.standard.data(forKey: key),
           let decoded = try? JSONDecoder().decode([RecentProjectStub].self, from: data) {
            self.recent = decoded
        }
    }

    /// Record a project as most-recently used. Existing entries with the same
    /// id are removed before insertion so the list is de-duplicated.
    func record(id: String, name: String, path: String?) {
        recent.removeAll { $0.id == id }
        recent.insert(
            RecentProjectStub(id: id, name: name, path: path, recordedAt: Date()),
            at: 0
        )
        if recent.count > max {
            recent = Array(recent.prefix(max))
        }
        persist()
    }

    /// Clear all recent projects.
    func clear() {
        recent = []
        persist()
    }

    private func persist() {
        if let data = try? JSONEncoder().encode(recent) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }
}
