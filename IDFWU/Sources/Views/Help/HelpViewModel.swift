import Foundation
import Observation

@Observable
@MainActor
final class HelpViewModel {
    var selected: HelpSection = .gettingStarted {
        didSet {
            if selected != oldValue {
                load()
            }
        }
    }

    var content: AttributedString = AttributedString("")

    func load() {
        guard let url = Bundle.module.url(forResource: selected.fileName, withExtension: "md") else {
            content = AttributedString("Failed to load \(selected.displayName)")
            return
        }

        do {
            let raw = try String(contentsOf: url, encoding: .utf8)
            content = try AttributedString(
                markdown: raw,
                options: AttributedString.MarkdownParsingOptions(
                    interpretedSyntax: .inlineOnlyPreservingWhitespace
                )
            )
        } catch {
            content = AttributedString("Failed to load \(selected.displayName)")
        }
    }
}
