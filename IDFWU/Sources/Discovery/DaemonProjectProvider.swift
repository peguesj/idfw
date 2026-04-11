import Foundation

struct DaemonProjectProvider: ProjectProvider {
    let name = "daemon"
    let baseURL: URL

    init(baseURL: URL = URL(string: "http://localhost:4040")!) {
        self.baseURL = baseURL
    }

    func discover() async throws -> [DiscoveredProject] {
        let url = baseURL.appendingPathComponent("api/v3/projects")
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse,
              (200...299).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        let decoder = JSONDecoder()
        return try decoder.decode([DiscoveredProject].self, from: data)
    }

    func isAvailable() async -> Bool {
        let url = baseURL.appendingPathComponent("api/v3/health")
        do {
            let (_, response) = try await URLSession.shared.data(from: url)
            guard let http = response as? HTTPURLResponse else { return false }
            return (200...299).contains(http.statusCode)
        } catch {
            return false
        }
    }
}
