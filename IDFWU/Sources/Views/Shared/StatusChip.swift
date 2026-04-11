import SwiftUI

struct StatusChip: View {
    let label: String
    let color: Color

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 6, height: 6)

            Text(label)
                .font(.caption2.weight(.medium))
                .foregroundStyle(.primary)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(color.opacity(0.12), in: Capsule())
    }

    // MARK: - Preset States

    static var pass: StatusChip { StatusChip(label: "Pass", color: .green) }
    static var fail: StatusChip { StatusChip(label: "Fail", color: .red) }
    static var pending: StatusChip { StatusChip(label: "Pending", color: .orange) }
    static var draft: StatusChip { StatusChip(label: "Draft", color: .secondary) }
}

#Preview {
    HStack(spacing: 8) {
        StatusChip.pass
        StatusChip.fail
        StatusChip.pending
        StatusChip.draft
        StatusChip(label: "Custom", color: .purple)
    }
    .padding()
}
