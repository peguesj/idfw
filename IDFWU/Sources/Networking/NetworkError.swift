import Foundation

enum NetworkError: LocalizedError {
    case invalidURL
    case httpError(statusCode: Int, body: String?)
    case decodingFailed(underlying: Error)
    case rateLimited(resetAt: Date)
    case sseConnectionLost
    case sseParseFailure

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "The URL is invalid."
        case .httpError(let statusCode, let body):
            let detail = body.map { " - \($0)" } ?? ""
            return "HTTP \(statusCode)\(detail)"
        case .decodingFailed(let underlying):
            return "Decoding failed: \(underlying.localizedDescription)"
        case .rateLimited(let resetAt):
            let formatter = DateFormatter()
            formatter.dateStyle = .none
            formatter.timeStyle = .medium
            return "Rate limited. Resets at \(formatter.string(from: resetAt))."
        case .sseConnectionLost:
            return "SSE connection lost."
        case .sseParseFailure:
            return "Failed to parse SSE frame."
        }
    }
}
