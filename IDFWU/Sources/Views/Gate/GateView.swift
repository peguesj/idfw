import SwiftUI

struct GateView: View {
    @Binding var gates: [DecisionGate]
    var onStatusChange: (DecisionGate, DecisionGate.GateStatus) -> Void

    var body: some View {
        VStack(spacing: 0) {
            aggregateBar
                .padding()

            List($gates) { $gate in
                GateRowView(gate: gate) { newStatus in
                    onStatusChange(gate, newStatus)
                }
            }
        }
        .accessibilityIdentifier(AccessibilityIdentifiers.Gate.container)
    }

    private var aggregateBar: some View {
        HStack(spacing: 16) {
            ForEach(DecisionGate.GateStatus.allCases, id: \.self) { status in
                let count = gates.filter { $0.status == status }.count
                HStack(spacing: 4) {
                    Circle()
                        .fill(color(for: status))
                        .frame(width: 8, height: 8)
                    Text("\(count) \(status.rawValue)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            Spacer()
        }
        .liquidGlassCard()
    }

    private func color(for status: DecisionGate.GateStatus) -> Color {
        switch status {
        case .pending: return .yellow
        case .passed:  return .green
        case .failed:  return .red
        case .waived:  return .gray
        }
    }
}
