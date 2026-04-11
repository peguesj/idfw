import SwiftUI

struct GateRowView: View {
    let gate: DecisionGate
    var onStatusChange: (DecisionGate.GateStatus) -> Void

    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(gate.title)
                    .font(.headline)

                Text(gate.criteria)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            Spacer()

            if !gate.options.isEmpty {
                Text("\(gate.options.count) reviewers")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }

            Menu {
                ForEach(DecisionGate.GateStatus.allCases, id: \.self) { status in
                    Button(status.rawValue.capitalized) {
                        onStatusChange(status)
                    }
                }
            } label: {
                statusBadge
            }
            .menuStyle(.borderlessButton)
            .fixedSize()
        }
        .padding(.vertical, 4)
        .accessibilityIdentifier(AccessibilityIdentifiers.Gate.row)
    }

    private var statusBadge: some View {
        Text(gate.status.rawValue.capitalized)
            .font(.caption.weight(.medium))
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(badgeColor.opacity(0.15), in: Capsule())
            .foregroundStyle(badgeColor)
    }

    private var badgeColor: Color {
        switch gate.status {
        case .pending: return .yellow
        case .passed:  return .green
        case .failed:  return .red
        case .waived:  return .gray
        }
    }
}
