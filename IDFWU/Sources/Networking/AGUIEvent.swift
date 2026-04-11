import Foundation

enum AnyCodableValue: Codable, Sendable, Equatable, Hashable {
    case string(String)
    case int(Int)
    case double(Double)
    case bool(Bool)
    case array([AnyCodableValue])
    case object([String: AnyCodableValue])

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(Int.self) {
            self = .int(value)
        } else if let value = try? container.decode(Double.self) {
            self = .double(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([AnyCodableValue].self) {
            self = .array(value)
        } else if let value = try? container.decode([String: AnyCodableValue].self) {
            self = .object(value)
        } else {
            throw DecodingError.typeMismatch(
                AnyCodableValue.self,
                .init(codingPath: decoder.codingPath, debugDescription: "Unsupported type")
            )
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .string(let v):  try container.encode(v)
        case .int(let v):     try container.encode(v)
        case .double(let v):  try container.encode(v)
        case .bool(let v):    try container.encode(v)
        case .array(let v):   try container.encode(v)
        case .object(let v):  try container.encode(v)
        }
    }
}

enum AGUIEventType: String, Codable, Sendable, Hashable {
    case runStarted = "run_started"
    case runFinished = "run_finished"
    case stateSnapshot = "state_snapshot"
    case stateDelta = "state_delta"
    case custom
    case error
}

struct AGUIEvent: Codable, Identifiable, Sendable {
    let id: UUID
    let eventType: AGUIEventType
    let threadId: String?
    let name: String?
    let value: [String: AnyCodableValue]?
    let sequence: Int?
    let timestamp: Date

    init(
        id: UUID = UUID(),
        eventType: AGUIEventType,
        threadId: String? = nil,
        name: String? = nil,
        value: [String: AnyCodableValue]? = nil,
        sequence: Int? = nil,
        timestamp: Date = Date()
    ) {
        self.id = id
        self.eventType = eventType
        self.threadId = threadId
        self.name = name
        self.value = value
        self.sequence = sequence
        self.timestamp = timestamp
    }
}
