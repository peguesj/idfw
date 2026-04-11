import Foundation

@MainActor
final class AGUIEventDispatcher {
    typealias Handler = @MainActor (AGUIEvent) -> Void

    private var handlers: [AGUIEventType: [UUID: Handler]] = [:]

    @discardableResult
    func register(for eventType: AGUIEventType, handler: @escaping Handler) -> UUID {
        let token = UUID()
        handlers[eventType, default: [:]][token] = handler
        return token
    }

    func deregister(token: UUID, for eventType: AGUIEventType) {
        handlers[eventType]?.removeValue(forKey: token)
    }

    func deregisterAll(for eventType: AGUIEventType) {
        handlers[eventType] = nil
    }

    func dispatch(_ event: AGUIEvent) {
        guard let bucket = handlers[event.eventType] else { return }
        for handler in bucket.values {
            handler(event)
        }
    }
}
