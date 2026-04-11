import Foundation

enum SSEConnectionState: Equatable {
    case disconnected
    case connecting
    case connected
    case error(String)
}
