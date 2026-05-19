import SwiftUI

/// Horizontal I → D → E → A progress rail with gate diamonds between phases.
/// Communicates the IDFW lifecycle position at a glance (Replit/Lovable show
/// a build progress bar; IDFWU shows a *governed* lifecycle).
struct IDEALifecycleStepper: View {
    let currentPhase: IDEAPhase
    let completedPhases: Set<IDEAPhase>

    private let phases = IDEAPhase.allCases

    var body: some View {
        HStack(spacing: 0) {
            ForEach(Array(phases.enumerated()), id: \.element) { index, phase in
                phaseNode(phase)
                if index < phases.count - 1 {
                    connector(after: phase)
                }
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(.bar)
    }

    @ViewBuilder
    private func phaseNode(_ phase: IDEAPhase) -> some View {
        let isDone = completedPhases.contains(phase)
        let isCurrent = phase == currentPhase
        VStack(spacing: 4) {
            ZStack {
                Circle()
                    .fill(isDone ? phase.accentColor
                          : isCurrent ? phase.accentColor.opacity(0.22)
                          : Color.secondary.opacity(0.12))
                    .frame(width: 30, height: 30)
                if isDone {
                    Image(systemName: "checkmark")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundStyle(.white)
                } else {
                    Text(phase.letter)
                        .font(.system(size: 14, weight: .bold, design: .rounded))
                        .foregroundStyle(isCurrent ? phase.accentColor : .secondary)
                }
            }
            .overlay(
                Circle().strokeBorder(
                    isCurrent ? phase.accentColor : .clear, lineWidth: 2)
            )
            Text(phase.title)
                .font(.caption2.weight(isCurrent ? .semibold : .regular))
                .foregroundStyle(isCurrent ? .primary : .secondary)
        }
    }

    private func connector(after phase: IDEAPhase) -> some View {
        let passed = completedPhases.contains(phase)
        return Image(systemName: "diamond.fill")
            .font(.system(size: 7))
            .foregroundStyle(passed ? phase.accentColor : Color.secondary.opacity(0.3))
            .frame(maxWidth: .infinity)
            .overlay(alignment: .center) {
                Rectangle()
                    .fill(passed ? phase.accentColor.opacity(0.5)
                          : Color.secondary.opacity(0.2))
                    .frame(height: 2)
                    .padding(.horizontal, 10)
            }
            .padding(.bottom, 16)
    }
}
