import SwiftUI

enum IDEASchemaType: String, CaseIterable, Codable {
    case idfw
    case iddv
    case iddg
    case iddc
    case idda
    case idfpj
    case ddd
    case idpc
    case idpg

    var displayName: String {
        switch self {
        case .idfw:  return "IDEA Framework"
        case .iddv:  return "IDEA Document Variables"
        case .iddg:  return "IDEA Document Diagrams"
        case .iddc:  return "IDEA Document Contracts"
        case .idda:  return "IDEA Document Actions"
        case .idfpj: return "IDEA Framework Project"
        case .ddd:   return "Domain-Driven Design"
        case .idpc:  return "IDEA Project Constraints"
        case .idpg:  return "IDEA Project Governance"
        }
    }

    var accentColor: Color {
        switch self {
        case .idfw:  return .blue
        case .iddv:  return .purple
        case .iddg:  return .orange
        case .iddc:  return .green
        case .idda:  return .red
        case .idfpj: return .cyan
        case .ddd:   return .indigo
        case .idpc:  return .yellow
        case .idpg:  return .mint
        }
    }

    var docIdPrefix: String {
        rawValue.uppercased() + "-"
    }
}
