import Foundation

struct DiagramPayload: Identifiable {
    let id: UUID
    var mermaidSource: String
    var title: String?
    var theme: MermaidTheme

    init(id: UUID = UUID(), mermaidSource: String, title: String? = nil, theme: MermaidTheme = .default_) {
        self.id = id
        self.mermaidSource = mermaidSource
        self.title = title
        self.theme = theme
    }

    enum MermaidTheme: String, Codable, CaseIterable {
        case default_ = "default"
        case dark
        case forest
        case neutral
    }
}
