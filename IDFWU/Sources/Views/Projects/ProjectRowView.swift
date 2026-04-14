import SwiftUI

struct ProjectRowView: View {
    let project: Project

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(project.name)
                    .font(.headline)

                HStack(spacing: 8) {
                    connectorBadge
                    Text("\(project.documents.count) documents")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()

            if let lastSynced = project.lastSynced {
                Text(lastSynced, style: .relative)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
        }
        .padding(.vertical, 4)
        .accessibilityIdentifier(AccessibilityIdentifiers.Projects.row)
    }

    @ViewBuilder
    private var connectorBadge: some View {
        let kind = project.connectorConfig?.kind ?? .local
        Label(
            kind == .local ? "Local" : "GitHub",
            systemImage: kind == .local ? "folder" : "network"
        )
        .font(.caption)
        .padding(.horizontal, 6)
        .padding(.vertical, 2)
        .background(.quaternary, in: Capsule())
    }
}
