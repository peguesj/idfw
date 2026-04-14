import Foundation
import Observation

/// Tracks user-favorited project IDs, persisted in UserDefaults as a
/// JSON-encoded `[String]` under the key `"favoriteProjectIds"`.
@MainActor
@Observable
final class FavoritesStore {
    private static let defaultsKey = "favoriteProjectIds"

    /// Shared instance used by SidebarView and row-level context actions.
    static let shared = FavoritesStore()

    private var favoriteIds: Set<String> = []

    init() {
        load()
    }

    // MARK: - Queries

    func isFavorite(_ id: String) -> Bool {
        favoriteIds.contains(id)
    }

    // MARK: - Mutations

    func toggle(_ id: String) {
        if favoriteIds.contains(id) {
            favoriteIds.remove(id)
        } else {
            favoriteIds.insert(id)
        }
        save()
    }

    func add(_ id: String) {
        guard !favoriteIds.contains(id) else { return }
        favoriteIds.insert(id)
        save()
    }

    func remove(_ id: String) {
        guard favoriteIds.contains(id) else { return }
        favoriteIds.remove(id)
        save()
    }

    // MARK: - Persistence

    private func load() {
        let defaults = UserDefaults.standard
        guard
            let data = defaults.data(forKey: Self.defaultsKey),
            let decoded = try? JSONDecoder().decode([String].self, from: data)
        else {
            favoriteIds = []
            return
        }
        favoriteIds = Set(decoded)
    }

    private func save() {
        let array = Array(favoriteIds).sorted()
        guard let data = try? JSONEncoder().encode(array) else { return }
        UserDefaults.standard.set(data, forKey: Self.defaultsKey)
    }
}
