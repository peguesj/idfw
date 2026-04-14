import SwiftUI

struct EventRowView: View {
    let event: AGUIEvent

    private static let timeFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "HH:mm:ss.SSS"
        return f
    }()

    var body: some View {
        HStack(spacing: 8) {
            Text(Self.timeFormatter.string(from: event.timestamp))
                .font(.system(.caption2, design: .monospaced))
                .foregroundStyle(.tertiary)

            typeBadge

            Text(payloadText.prefix(120))
                .font(.caption)
                .lineLimit(1)
                .truncationMode(.tail)
                .foregroundStyle(.secondary)
        }
        .accessibilityIdentifier(AccessibilityIdentifiers.EventStream.row)
    }

    private var payloadText: String {
        guard let value = event.value else { return "" }
        return value.map { "\($0.key): \($0.value)" }.joined(separator: ", ")
    }

    private var typeBadge: some View {
        Text(event.eventType.rawValue)
            .font(.system(.caption2, design: .monospaced).weight(.medium))
            .padding(.horizontal, 5)
            .padding(.vertical, 1)
            .background(badgeColor.opacity(0.15), in: Capsule())
            .foregroundStyle(badgeColor)
    }

    private var badgeColor: Color {
        switch event.eventType {
        case .runStarted:     return .cyan
        case .runFinished:    return .mint
        case .stateSnapshot:  return .blue
        case .stateDelta:     return .orange
        case .custom:         return .purple
        case .error:          return .red
        }
    }
}
