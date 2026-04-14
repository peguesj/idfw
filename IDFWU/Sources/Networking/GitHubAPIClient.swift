import Foundation

struct GitHubTreeEntry: Codable, Sendable {
    let path: String
    let type: String
    let size: Int?
}

struct GitHubAPIClient: Sendable {
    private let session: URLSession
    private let token: String?

    init(token: String? = nil) {
        self.session = URLSession.shared
        self.token = token
    }

    func tree(owner: String, repo: String, ref: String) async throws -> [GitHubTreeEntry] {
        guard let url = URL(string: "https://api.github.com/repos/\(owner)/\(repo)/git/trees/\(ref)?recursive=1") else {
            throw NetworkError.invalidURL
        }

        var request = URLRequest(url: url)
        request.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        applyAuth(&request)

        let (data, response) = try await session.data(for: request)
        try checkResponse(response, data: data)

        struct TreeResponse: Codable {
            let tree: [GitHubTreeEntry]
        }

        do {
            let decoded = try JSONDecoder().decode(TreeResponse.self, from: data)
            return decoded.tree
        } catch {
            throw NetworkError.decodingFailed(underlying: error)
        }
    }

    func rawContent(owner: String, repo: String, path: String, ref: String) async throws -> Data {
        guard let url = URL(string: "https://raw.githubusercontent.com/\(owner)/\(repo)/\(ref)/\(path)") else {
            throw NetworkError.invalidURL
        }

        var request = URLRequest(url: url)
        applyAuth(&request)

        let (data, response) = try await session.data(for: request)
        try checkResponse(response, data: data)
        return data
    }

    private func applyAuth(_ request: inout URLRequest) {
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
    }

    private func checkResponse(_ response: URLResponse, data: Data) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidURL
        }

        if httpResponse.statusCode == 429 {
            let resetTimestamp = httpResponse.value(forHTTPHeaderField: "X-RateLimit-Reset")
                .flatMap(TimeInterval.init)
                .map { Date(timeIntervalSince1970: $0) }
                ?? Date(timeIntervalSinceNow: 60)
            throw NetworkError.rateLimited(resetAt: resetTimestamp)
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            let body = String(data: data, encoding: .utf8)
            throw NetworkError.httpError(statusCode: httpResponse.statusCode, body: body)
        }

        if let remaining = httpResponse.value(forHTTPHeaderField: "X-RateLimit-Remaining"),
           let count = Int(remaining), count < 10 {
            let resetTimestamp = httpResponse.value(forHTTPHeaderField: "X-RateLimit-Reset")
                .flatMap(TimeInterval.init)
                .map { Date(timeIntervalSince1970: $0) }
                ?? Date(timeIntervalSinceNow: 60)
            if count == 0 {
                throw NetworkError.rateLimited(resetAt: resetTimestamp)
            }
        }
    }
}
