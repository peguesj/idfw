import SwiftUI

// MARK: - NavigationRouter Environment

extension EnvironmentValues {
    @Entry var navigationRouter: NavigationRouter = NavigationRouter()
}

// MARK: - EventStreamClient Environment

@Observable
final class EventStreamState {
    enum ConnectionState: Equatable {
        case disconnected
        case connecting
        case connected
        case reconnecting
    }

    var connectionState: ConnectionState = .disconnected
    var lastEventTimestamp: Date?

    var isConnected: Bool { connectionState == .connected }
}

extension EnvironmentValues {
    @Entry var eventStreamState: EventStreamState = EventStreamState()
}
