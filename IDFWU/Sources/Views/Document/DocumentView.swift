import SwiftUI

struct DocumentView: View {
    let markdown: String

    var body: some View {
        ScrollView {
            if let attributed = try? AttributedString(markdown: markdown) {
                Text(attributed)
                    .font(.body)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
            } else {
                Text(markdown)
                    .font(.body)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
            }
        }
        .accessibilityIdentifier(AccessibilityIdentifiers.Document.container)
    }
}
