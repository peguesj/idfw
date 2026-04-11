import Foundation
import Observation

@MainActor
@Observable
final class EventStreamViewModel {
    var connectionState: SSEConnectionState = .disconnected
    var events: [AGUIEvent] = []

    private static let maxEvents = 200
    private var streamTask: Task<Void, Never>?

    func connect(to url: URL) {
        disconnect()
        connectionState = .connecting

        streamTask = Task {
            do {
                let (bytes, response) = try await URLSession.shared.bytes(from: url)
                guard let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 else {
                    connectionState = .error("Bad response")
                    return
                }
                connectionState = .connected

                for try await line in bytes.lines {
                    guard !Task.isCancelled else { break }
                    if line.hasPrefix("data:") {
                        let payload = String(line.dropFirst(5)).trimmingCharacters(in: .whitespaces)
                        let event = AGUIEvent(eventType: .stateDelta, name: "sse", value: ["data": .string(payload)])
                        appendEvent(event)
                    }
                }
            } catch {
                connectionState = .error(error.localizedDescription)
            }
        }
    }

    func disconnect() {
        streamTask?.cancel()
        streamTask = nil
        connectionState = .disconnected
    }

    func send(event: AGUIEvent) {
        appendEvent(event)
    }

    private func appendEvent(_ event: AGUIEvent) {
        events.append(event)
        if events.count > Self.maxEvents {
            events.removeFirst(events.count - Self.maxEvents)
        }
    }
}
