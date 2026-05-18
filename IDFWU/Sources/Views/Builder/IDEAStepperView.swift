import SwiftUI

// MARK: - IDEA Lifecycle Stepper

struct IDEAStepperView: View {
    var currentPhase: IDEAPhase = .ideation
    var gateStatuses: [String: DecisionGate.GateStatus] = [:]
    var onSelectPhase: ((IDEAPhase) -> Void)? = nil
    var variant: StepperVariant = .full

    enum StepperVariant { case full, compact, mini }

    private let phases = IDEAPhase.allCases

    var body: some View {
        switch variant {
        case .mini:   miniStepper
        case .compact: fullStepper(compact: true)
        case .full:   fullStepper(compact: false)
        }
    }

    // MARK: Mini (4-dot progress bar)

    private var miniStepper: some View {
        HStack(spacing: 3) {
            ForEach(phases, id: \.self) { phase in
                let idx = phases.firstIndex(of: phase)!
                let curIdx = phases.firstIndex(of: currentPhase)!
                let isActive = phase == currentPhase
                let isDone = idx < curIdx

                Capsule()
                    .fill(isDone || isActive ? phase.color : DesignTokens.Hairline.bold)
                    .frame(width: isActive ? 18 : 4, height: 4)
                    .animation(.easeOut(duration: 0.32), value: currentPhase)
            }
        }
    }

    // MARK: Full / Compact

    private func fullStepper(compact: Bool) -> some View {
        HStack(spacing: 0) {
            ForEach(Array(phases.enumerated()), id: \.element) { idx, phase in
                let curIdx = phases.firstIndex(of: currentPhase)!
                let state: NodeState = idx < curIdx ? .done : (idx == curIdx ? .active : .todo)

                PhaseNodeButton(
                    phase: phase,
                    state: state,
                    compact: compact
                ) {
                    onSelectPhase?(phase)
                }

                if idx < phases.count - 1 {
                    let gateState = resolveGateState(for: phase, curIdx: curIdx, phaseIdx: idx)
                    GateDiamond(phase: phase, state: gateState, compact: compact)
                }
            }
        }
    }

    private func resolveGateState(for phase: IDEAPhase, curIdx: Int, phaseIdx: Int) -> GateState {
        if let status = gateStatuses[phase.rawValue] {
            switch status {
            case .passed:  return .passed
            case .pending: return .pending
            case .failed:  return .failed
            case .waived:  return .waived
            }
        }
        if phaseIdx < curIdx { return .passed }
        if phaseIdx == curIdx { return .pending }
        return .upcoming
    }
}

// MARK: - Node state

private enum NodeState { case active, done, todo }
private enum GateState { case passed, pending, failed, waived, upcoming }

// MARK: - Phase node button

private struct PhaseNodeButton: View {
    let phase: IDEAPhase
    let state: NodeState
    let compact: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: compact ? 5 : 8) {
                IDEAPhaseLetter(
                    phase: phase,
                    size: compact ? .sm : .md,
                    state: letterState
                )
                if !compact {
                    VStack(alignment: .leading, spacing: 1) {
                        Text(phase.builderTitle)
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(titleColor)
                        if state == .active {
                            Text(phase.builderSubtitle)
                                .font(.system(size: 9))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                        }
                    }
                }
            }
            .padding(.horizontal, compact ? 8 : 12)
            .padding(.vertical, compact ? 4 : 6)
            .background(
                Capsule()
                    .fill(bgFill)
                    .overlay(Capsule().strokeBorder(borderColor, lineWidth: 0.5))
            )
        }
        .buttonStyle(.plain)
        .shadow(color: state == .active ? phase.glowColor : .clear, radius: 14)
    }

    private var letterState: IDEAPhaseLetter.LetterState {
        switch state {
        case .active: .active
        case .done:   .done
        case .todo:   .todo
        }
    }

    private var bgFill: Color {
        switch state {
        case .active: phase.color.opacity(0.14)
        case .done:   phase.color.opacity(0.08)
        case .todo:   Color.clear
        }
    }

    private var borderColor: Color {
        state == .active ? phase.color.opacity(0.38) : Color.clear
    }

    private var titleColor: Color {
        switch state {
        case .active: phase.color
        case .done:   phase.color
        case .todo:   DesignTokens.Foreground.tertiary
        }
    }
}

// MARK: - Gate diamond connector

private struct GateDiamond: View {
    let phase: IDEAPhase
    let state: GateState
    let compact: Bool

    private var sz: CGFloat { compact ? 14 : 18 }

    var body: some View {
        HStack(spacing: 0) {
            // Left line
            Rectangle()
                .fill(leftLineColor)
                .frame(height: 1)

            // Diamond
            ZStack {
                RoundedRectangle(cornerRadius: 2)
                    .fill(diamondFill)
                    .overlay(
                        RoundedRectangle(cornerRadius: 2)
                            .strokeBorder(diamondBorder, lineWidth: 0.5)
                    )
                    .frame(width: sz, height: sz)
                    .rotationEffect(.degrees(45))
                    .shadow(color: state == .pending ? DesignTokens.Gate.pending.opacity(0.35) : .clear, radius: 10)

                gateIcon
                    .font(.system(size: sz * 0.55, weight: .bold))
                    .foregroundStyle(iconColor)
            }
            .frame(width: sz + 4, height: sz + 4)

            // Right line
            Rectangle()
                .fill(rightLineColor)
                .frame(height: 1)
        }
        .frame(minWidth: 48)
    }

    @ViewBuilder
    private var gateIcon: some View {
        switch state {
        case .passed:
            Image(systemName: "checkmark")
        case .pending:
            PendingDot()
        case .failed:
            Image(systemName: "xmark")
        case .waived:
            Image(systemName: "minus")
        case .upcoming:
            EmptyView()
        }
    }

    private var diamondFill: Color {
        switch state {
        case .passed:  return DesignTokens.Gate.passed.opacity(0.22)
        case .pending: return DesignTokens.Gate.pending.opacity(0.28)
        case .failed:  return DesignTokens.Gate.failed.opacity(0.22)
        case .waived:  return DesignTokens.Gate.waived.opacity(0.22)
        case .upcoming: return DesignTokens.Background.surface
        }
    }

    private var diamondBorder: Color {
        switch state {
        case .passed:  return DesignTokens.Gate.passed.opacity(0.50)
        case .pending: return DesignTokens.Gate.pending.opacity(0.60)
        case .failed:  return DesignTokens.Gate.failed.opacity(0.60)
        case .waived:  return DesignTokens.Gate.waived.opacity(0.60)
        case .upcoming: return DesignTokens.Hairline.soft
        }
    }

    private var iconColor: Color {
        switch state {
        case .passed:  return DesignTokens.Gate.passed
        case .pending: return DesignTokens.Gate.pending
        case .failed:  return DesignTokens.Gate.failed
        case .waived:  return DesignTokens.Gate.waived
        case .upcoming: return DesignTokens.Foreground.quaternary
        }
    }

    private var leftLineColor: Color {
        state == .passed ? phase.color.opacity(0.5) : DesignTokens.Hairline.bold
    }
    private var rightLineColor: Color { DesignTokens.Hairline.bold }
}

private struct PendingDot: View {
    @State private var pulse = false
    var body: some View {
        Circle()
            .fill(DesignTokens.Gate.pending)
            .frame(width: 5, height: 5)
            .scaleEffect(pulse ? 1.3 : 1.0)
            .onAppear {
                withAnimation(.easeInOut(duration: 0.9).repeatForever(autoreverses: true)) {
                    pulse = true
                }
            }
    }
}

// MARK: - Phase header

struct PhaseHeaderBar: View {
    let phase: IDEAPhase
    var eyebrow: String? = nil
    var title: String
    var subtitle: String? = nil
    var actions: AnyView? = nil
    var dense: Bool = false

    var body: some View {
        HStack(spacing: dense ? 10 : 14) {
            IDEAPhaseLetter(phase: phase, size: dense ? .md : .lg)
            VStack(alignment: .leading, spacing: 2) {
                if let eyebrow {
                    OverlineLabel(text: eyebrow)
                        .foregroundStyle(phase.color)
                }
                Text(title)
                    .font(dense
                        ? .system(size: 14, weight: .semibold)
                        : .system(size: 17, weight: .bold)
                    )
                    .foregroundStyle(DesignTokens.Foreground.primary)
                if let subtitle {
                    Text(subtitle)
                        .font(.system(size: 12))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                }
            }
            Spacer(minLength: 0)
            if let actions { actions }
        }
        .padding(.horizontal, dense ? 16 : 22)
        .padding(.vertical, dense ? 10 : 16)
    }
}

// MARK: - Previews

#Preview("Stepper Full") {
    VStack(spacing: 24) {
        IDEAStepperView(currentPhase: .definition,
                        gateStatuses: ["ideation": .passed, "definition": .pending])
        IDEAStepperView(currentPhase: .evaluation, variant: .compact)
        IDEAStepperView(currentPhase: .application, variant: .mini)
    }
    .padding(24)
    .background(DesignTokens.Background.base)
    .preferredColorScheme(.dark)
}
