import Foundation

enum IDEADocument {
    case idfw([String: Any])
    case iddv([String: Any])
    case iddg([String: Any])
    case iddc([String: Any])
    case idda([String: Any])
    case idfpj([String: Any])
    case ddd([String: Any])
    case idpc([String: Any])
    case idpg([String: Any])

    var schemaType: IDEASchemaType {
        switch self {
        case .idfw:  return .idfw
        case .iddv:  return .iddv
        case .iddg:  return .iddg
        case .iddc:  return .iddc
        case .idda:  return .idda
        case .idfpj: return .idfpj
        case .ddd:   return .ddd
        case .idpc:  return .idpc
        case .idpg:  return .idpg
        }
    }

    var payload: [String: Any] {
        switch self {
        case .idfw(let d), .iddv(let d), .iddg(let d), .iddc(let d),
             .idda(let d), .idfpj(let d), .ddd(let d), .idpc(let d), .idpg(let d):
            return d
        }
    }

    var docId: String {
        (payload["docId"] as? String)
            ?? (payload["id"] as? String)
            ?? UUID().uuidString
    }

    var title: String? {
        (payload["title"] as? String)
            ?? (payload["name"] as? String)
    }

    static func from(type: IDEASchemaType, payload: [String: Any]) -> IDEADocument {
        switch type {
        case .idfw:  return .idfw(payload)
        case .iddv:  return .iddv(payload)
        case .iddg:  return .iddg(payload)
        case .iddc:  return .iddc(payload)
        case .idda:  return .idda(payload)
        case .idfpj: return .idfpj(payload)
        case .ddd:   return .ddd(payload)
        case .idpc:  return .idpc(payload)
        case .idpg:  return .idpg(payload)
        }
    }
}
