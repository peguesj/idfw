import Foundation

struct DiscoveredProject: Codable, Identifiable, Hashable, Sendable {
    let id: String
    let name: String
    let path: String?
    let source: String
    let identifier: String?
    let planeId: String?
    let planeUrl: String?
    let apmPort: Int?
    let description: String?
    let stack: [String]?
    let lastActive: String?
    let metadata: [String: AnyCodableValue]?

    enum CodingKeys: String, CodingKey {
        case id, name, path, source, identifier
        case planeId = "plane_id"
        case planeUrl = "plane_url"
        case apmPort = "apm_port"
        case description, stack
        case lastActive = "last_active"
        case metadata
    }
}

// AnyCodableValue is defined in Networking/AGUIEvent.swift
