import Foundation

enum SchemaTypeResolver {
    /// Detect IDEASchemaType from raw JSON data by inspecting docId prefix and top-level keys.
    static func resolve(from data: Data) -> IDEASchemaType? {
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        return resolve(from: json)
    }

    static func resolve(from json: [String: Any]) -> IDEASchemaType? {
        // Strategy 1: Match docId prefix
        if let docId = (json["docId"] as? String) ?? (json["id"] as? String) {
            let upper = docId.uppercased()
            for schemaType in IDEASchemaType.allCases {
                if upper.hasPrefix(schemaType.docIdPrefix) {
                    return schemaType
                }
            }
        }

        // Strategy 2: Match distinctive top-level keys
        let keys = Set(json.keys)

        if keys.contains("variables") && keys.contains("immutable") {
            return .iddv
        }
        if keys.contains("diagrams") || keys.contains("mermaid") {
            return .iddg
        }
        if keys.contains("contracts") || keys.contains("contractId") {
            return .iddc
        }
        if keys.contains("actions") || keys.contains("actionId") {
            return .idda
        }
        if keys.contains("projectType") || keys.contains("idfpj") {
            return .idfpj
        }
        if keys.contains("boundedContexts") || keys.contains("aggregates") {
            return .ddd
        }
        if keys.contains("constraints") || keys.contains("constraintId") {
            return .idpc
        }
        if keys.contains("governance") || keys.contains("policies") {
            return .idpg
        }
        if keys.contains("framework") || keys.contains("idfw") {
            return .idfw
        }

        return nil
    }
}
