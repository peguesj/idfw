import Foundation

protocol ProjectProvider: Sendable {
    var name: String { get }
    func discover() async throws -> [DiscoveredProject]
    func isAvailable() async -> Bool
}
