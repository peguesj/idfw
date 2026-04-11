import Foundation

enum HelpSection: String, CaseIterable, Identifiable {
    case gettingStarted
    case managingScanRoots
    case contextMenus
    case keyboardShortcuts
    case troubleshooting

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .gettingStarted: return "Getting Started"
        case .managingScanRoots: return "Managing Scan Roots"
        case .contextMenus: return "Context Menus"
        case .keyboardShortcuts: return "Keyboard Shortcuts"
        case .troubleshooting: return "Troubleshooting"
        }
    }

    var fileName: String {
        switch self {
        case .gettingStarted: return "GettingStarted"
        case .managingScanRoots: return "ManagingScanRoots"
        case .contextMenus: return "ContextMenus"
        case .keyboardShortcuts: return "KeyboardShortcuts"
        case .troubleshooting: return "Troubleshooting"
        }
    }

    var systemImage: String {
        switch self {
        case .gettingStarted: return "sparkles"
        case .managingScanRoots: return "folder.badge.gearshape"
        case .contextMenus: return "contextualmenu.and.cursorarrow"
        case .keyboardShortcuts: return "keyboard"
        case .troubleshooting: return "wrench.and.screwdriver"
        }
    }
}
