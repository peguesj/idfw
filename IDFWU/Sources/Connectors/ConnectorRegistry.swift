import Foundation
import Observation

@Observable
final class ConnectorRegistry {
    private(set) var connectors: [SourceConnectorConfig.ConnectorKind: any SourceConnector] = [:]

    func register(_ connector: any SourceConnector) {
        connectors[connector.config.kind] = connector
    }

    func deregister(_ kind: SourceConnectorConfig.ConnectorKind) {
        connectors.removeValue(forKey: kind)
    }

    func connector(for kind: SourceConnectorConfig.ConnectorKind) -> (any SourceConnector)? {
        connectors[kind]
    }

    var registeredKinds: [SourceConnectorConfig.ConnectorKind] {
        Array(connectors.keys)
    }
}
