import Foundation
import Observation

@Observable
final class SchemaDetailViewModel {
    var document: IDEADocument?
    var gates: [DecisionGate] = []
    var diagrams: [DiagramPayload] = []

    func load(from schemaDocument: SchemaDocument) {
        guard let json = try? JSONSerialization.jsonObject(with: schemaDocument.jsonPayload) as? [String: Any],
              let type = schemaDocument.type else {
            document = nil
            return
        }

        let doc = IDEADocument.from(type: type, payload: json)
        document = doc

        if let gateArray = json["gates"] as? [[String: Any]] {
            gates = gateArray.compactMap { dict in
                guard let id = dict["id"] as? String,
                      let title = dict["title"] as? String,
                      let criteria = dict["criteria"] as? String,
                      let statusRaw = dict["status"] as? String,
                      let status = DecisionGate.GateStatus(rawValue: statusRaw) else { return nil }
                return DecisionGate(
                    id: id,
                    title: title,
                    criteria: criteria,
                    status: status,
                    options: (dict["options"] as? [String]) ?? []
                )
            }
        } else {
            gates = []
        }

        if let diagramArray = json["diagrams"] as? [[String: Any]] {
            diagrams = diagramArray.compactMap { dict in
                guard let source = dict["mermaidSource"] as? String else { return nil }
                let theme = (dict["theme"] as? String).flatMap { DiagramPayload.MermaidTheme(rawValue: $0) } ?? .default_
                return DiagramPayload(mermaidSource: source, title: dict["title"] as? String, theme: theme)
            }
        } else {
            diagrams = []
        }
    }

    func markGate(_ gate: DecisionGate, status: DecisionGate.GateStatus) {
        guard let index = gates.firstIndex(where: { $0.id == gate.id }) else { return }
        gates[index].status = status
    }
}
