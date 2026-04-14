import Foundation

final class EventStreamClient: NSObject, Sendable {
    private let session: URLSession
    private let decoder: JSONDecoder

    override init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 300
        configuration.timeoutIntervalForResource = 600
        self.session = URLSession(configuration: configuration)

        let dec = JSONDecoder()
        dec.dateDecodingStrategy = .iso8601
        self.decoder = dec

        super.init()
    }

    func connect(to url: URL) -> AsyncThrowingStream<AGUIEvent, Error> {
        AsyncThrowingStream { continuation in
            Task { [weak self] in
                guard let self else {
                    continuation.finish()
                    return
                }
                var attempt = 0
                let maxBackoff: TimeInterval = 8

                while !Task.isCancelled {
                    do {
                        var request = URLRequest(url: url)
                        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
                        request.setValue("no-cache", forHTTPHeaderField: "Cache-Control")

                        let (bytes, response) = try await self.session.bytes(for: request)

                        if let httpResponse = response as? HTTPURLResponse,
                           !(200...299).contains(httpResponse.statusCode) {
                            let body = String(data: try await Data(collecting: bytes), encoding: .utf8)
                            throw NetworkError.httpError(statusCode: httpResponse.statusCode, body: body)
                        }

                        attempt = 0
                        var buffer = ""

                        for try await line in bytes.lines {
                            if Task.isCancelled { break }

                            if line.isEmpty {
                                let dataPayload = self.extractDataLines(from: buffer)
                                buffer = ""

                                guard !dataPayload.isEmpty,
                                      let jsonData = dataPayload.data(using: .utf8) else {
                                    continue
                                }

                                do {
                                    let event = try self.decoder.decode(AGUIEvent.self, from: jsonData)
                                    continuation.yield(event)
                                } catch {
                                    continuation.yield(with: .failure(NetworkError.sseParseFailure))
                                    return
                                }
                            } else {
                                buffer += line + "\n"
                            }
                        }

                        if Task.isCancelled {
                            continuation.finish()
                            return
                        }

                        throw NetworkError.sseConnectionLost

                    } catch is CancellationError {
                        continuation.finish()
                        return
                    } catch let error as NetworkError where error.isFatal {
                        continuation.finish(throwing: error)
                        return
                    } catch {
                        attempt += 1
                        let delay = min(pow(2.0, Double(attempt - 1)), maxBackoff)
                        try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                    }
                }

                continuation.finish()
            }
        }
    }

    func send(_ payload: [String: Any], to url: URL) async throws {
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidURL
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            let body = String(data: data, encoding: .utf8)
            throw NetworkError.httpError(statusCode: httpResponse.statusCode, body: body)
        }
    }

    private func extractDataLines(from buffer: String) -> String {
        buffer
            .split(separator: "\n", omittingEmptySubsequences: false)
            .compactMap { line -> String? in
                let s = String(line)
                guard s.hasPrefix("data:") else { return nil }
                return String(s.dropFirst(5)).trimmingCharacters(in: .whitespaces)
            }
            .joined(separator: "\n")
    }
}

private extension NetworkError {
    var isFatal: Bool {
        switch self {
        case .sseParseFailure, .invalidURL, .decodingFailed:
            return true
        case .httpError(let code, _) where code == 401 || code == 403 || code == 404:
            return true
        default:
            return false
        }
    }
}

private extension Data {
    init(collecting bytes: URLSession.AsyncBytes) async throws {
        var accumulated = Data()
        for try await byte in bytes {
            accumulated.append(byte)
        }
        self = accumulated
    }
}
