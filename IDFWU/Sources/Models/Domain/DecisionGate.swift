import Foundation

struct DecisionGate: Identifiable, Codable {
    let id: String
    var title: String
    var criteria: String
    var status: GateStatus
    var options: [String]
    var description: String?

    enum GateStatus: String, Codable, CaseIterable {
        case pending
        case passed
        case failed
        case waived
    }
}
