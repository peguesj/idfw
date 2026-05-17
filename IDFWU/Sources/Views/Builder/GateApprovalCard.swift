import SwiftUI

/// The IDFW decision gate, surfaced after a phase run completes. The user
/// must explicitly govern progression — this is the core differentiator vs.
/// a free-running Lovable/Replit build.
struct GateApprovalCard: View {
    let gate: DecisionGate
    let phase: IDEAPhase
    let onDecision: (BuilderOrchestrator.GateDecision) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 8) {
                Image(systemName: "checkmark.shield.fill")
                    .foregroundStyle(phase.accentColor)
                Text(gate.title)
                    .font(.headline)
                Spacer()
                statusBadge
            }

            Text(gate.criteria)
                .font(.callout)
                .foregroundStyle(.secondary)

            if let description = gate.description {
                Text(description)
                    .font(.caption)
                    .foregroundStyle(.tertiary)
            }

            if gate.status == .pending {
                HStack(spacing: 8) {
                    Button {
                        onDecision(.approve)
                    } label: {
                        Label("Approve", systemImage: "checkmark.circle.fill")
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(phase.accentColor)

                    Button("Request Changes") { onDecision(.requestChanges) }
                        .buttonStyle(.bordered)

                    Button("Waive") { onDecision(.waive) }
                        .buttonStyle(.bordered)

                    Button(role: .destructive) {
                        onDecision(.reject)
                    } label: {
                        Text("Reject")
                    }
                    .buttonStyle(.bordered)
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(phase.accentColor.opacity(0.10))
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .strokeBorder(phase.accentColor.opacity(0.35), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }

    private var statusBadge: some View {
        Text(gate.status.rawValue.capitalized)
            .font(.caption2.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(statusColor.opacity(0.2))
            .foregroundStyle(statusColor)
            .clipShape(Capsule())
    }

    private var statusColor: Color {
        switch gate.status {
        case .pending: return .orange
        case .passed:  return .green
        case .failed:  return .red
        case .waived:  return .gray
        }
    }
}
