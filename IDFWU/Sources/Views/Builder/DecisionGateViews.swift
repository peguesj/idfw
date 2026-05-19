import SwiftUI

// MARK: - Gate Core body (shared by all variants)

struct GateCore: View {
    let gate: DecisionGate.Full
    var compact: Bool = false
    var includeWaive: Bool = true

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            gateHeader
            criteriaSection
            if !gate.artifacts.isEmpty { artifactsSection }
            actionsRow
        }
    }

    // MARK: Header

    private var gateHeader: some View {
        HStack(alignment: .top, spacing: 12) {
            // Phase icon square
            ZStack {
                RoundedRectangle(cornerRadius: 10)
                    .fill(gate.phase.color.opacity(0.16))
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .strokeBorder(gate.phase.color.opacity(0.30), lineWidth: 0.5)
                    )
                Image(systemName: "diamond.fill")
                    .font(.system(size: compact ? 16 : 20))
                    .foregroundStyle(gate.phase.color)
            }
            .frame(width: compact ? 34 : 42, height: compact ? 34 : 42)
            .shadow(color: gate.status == .pending ? gate.phase.glowColor : .clear, radius: 16)

            VStack(alignment: .leading, spacing: 3) {
                HStack(spacing: 6) {
                    OverlineLabel(text: "Decision required")
                    StatusPill(label: gate.status.label, color: gate.status.pillColor)
                }
                Text(gate.phase.gateTitle)
                    .font(.system(size: compact ? 15 : 18, weight: .bold))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                Text(gate.phase.gateTagline)
                    .font(.system(size: 12))
                    .foregroundStyle(DesignTokens.Foreground.secondary)
                    .lineLimit(2)
            }
        }
        .padding(.bottom, 16)
    }

    // MARK: Criteria

    private var criteriaSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            OverlineLabel(text: "Pass criteria")
                .padding(.bottom, 2)
            ForEach(gate.criteria) { criterion in
                CriterionRow(criterion: criterion)
            }
        }
    }

    // MARK: Artifacts

    private var artifactsSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            OverlineLabel(text: "Artifacts produced")
                .padding(.top, 14)
                .padding(.bottom, 2)
            FlowLayout(spacing: 6) {
                ForEach(gate.artifacts) { artifact in
                    HStack(spacing: 4) {
                        Image(systemName: artifact.icon ?? "doc")
                            .font(.system(size: 10))
                        Text(artifact.name)
                            .font(.system(size: 11))
                    }
                    .foregroundStyle(DesignTokens.Foreground.secondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(
                        RoundedRectangle(cornerRadius: 5)
                            .fill(DesignTokens.Glass.thin)
                            .overlay(
                                RoundedRectangle(cornerRadius: 5)
                                    .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                            )
                    )
                }
            }
        }
    }

    // MARK: Actions

    private var actionsRow: some View {
        let isPending = gate.status == .pending
        return HStack(spacing: 8) {
            PhaseButton(label: "Approve", symbol: "checkmark",
                        phase: gate.phase, disabled: !isPending) {
                gate.onResolve?(.approve)
            }
            Button(action: { gate.onResolve?(.requestChanges) }) {
                HStack(spacing: 4) {
                    Image(systemName: "pencil")
                        .font(.system(size: 11))
                    Text("Request changes")
                        .font(.system(size: 12, weight: .medium))
                }
                .foregroundStyle(isPending ? DesignTokens.Foreground.primary : DesignTokens.Foreground.tertiary)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 7)
                        .fill(DesignTokens.Background.raised)
                        .overlay(
                            RoundedRectangle(cornerRadius: 7)
                                .strokeBorder(DesignTokens.Hairline.bold, lineWidth: 0.5)
                        )
                )
            }
            .buttonStyle(.plain)
            .disabled(!isPending)

            if includeWaive {
                Button("Waive") { gate.onResolve?(.waive) }
                    .font(.system(size: 12))
                    .foregroundStyle(isPending ? DesignTokens.Foreground.secondary : DesignTokens.Foreground.quaternary)
                    .buttonStyle(.plain)
                    .disabled(!isPending)
            }

            Spacer(minLength: 0)

            Button(action: { gate.onResolve?(.reject) }) {
                HStack(spacing: 4) {
                    Image(systemName: "xmark")
                        .font(.system(size: 11))
                    Text("Reject")
                        .font(.system(size: 12, weight: .medium))
                }
                .foregroundStyle(isPending ? DesignTokens.Gate.failed : DesignTokens.Foreground.quaternary)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 7)
                        .fill(DesignTokens.Gate.failed.opacity(0.10))
                        .overlay(
                            RoundedRectangle(cornerRadius: 7)
                                .strokeBorder(DesignTokens.Gate.failed.opacity(0.25), lineWidth: 0.5)
                        )
                )
            }
            .buttonStyle(.plain)
            .disabled(!isPending)
        }
        .padding(.top, 18)
    }
}

// MARK: - Criterion row

struct CriterionRow: View {
    let criterion: DecisionGate.Criterion

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: criterion.status.symbol)
                .font(.system(size: 13))
                .foregroundStyle(criterion.status.color)
                .frame(width: 14)

            VStack(alignment: .leading, spacing: 2) {
                Text(criterion.label)
                    .font(.system(size: 12))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                if let detail = criterion.detail {
                    Text(detail)
                        .font(.system(size: 10))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                }
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 7)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 7)
                .fill(DesignTokens.Glass.tint)
                .overlay(
                    RoundedRectangle(cornerRadius: 7)
                        .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                )
        )
    }
}

extension DecisionGate.Criterion.CriterionStatus {
    var symbol: String {
        switch self {
        case .pass:    return "checkmark.circle.fill"
        case .fail:    return "xmark.circle.fill"
        case .pending: return "exclamationmark.circle.fill"
        case .info:    return "info.circle.fill"
        }
    }

    var color: Color {
        switch self {
        case .pass:    return DesignTokens.Gate.passed
        case .fail:    return DesignTokens.Gate.failed
        case .pending: return DesignTokens.Gate.pending
        case .info:    return DesignTokens.Foreground.tertiary
        }
    }
}

// MARK: - Gate inline (in chat)

struct GateInlineCard: View {
    let gate: DecisionGate.Full
    var onPin: (() -> Void)? = nil
    var onExpand: (() -> Void)? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Ambient glow strip at top
            LinearGradient(
                colors: [gate.phase.color.opacity(0.5), .clear],
                startPoint: .leading,
                endPoint: .trailing
            )
            .frame(height: 1)

            VStack(alignment: .leading, spacing: 0) {
                GateCore(gate: gate, compact: false)
                    .padding(.horizontal, 20)
                    .padding(.top, 18)
                    .padding(.bottom, 12)

                HStack {
                    Spacer()
                    SquareIconButton(symbol: "pin") { onPin?() }
                    SquareIconButton(symbol: "arrow.up.right.square") { onExpand?() }
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 14)
            }
        }
        .background(
            RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                .fill(
                    LinearGradient(
                        stops: [
                            .init(color: gate.phase.color.opacity(0.06).blended(with: DesignTokens.Background.raised), location: 0),
                            .init(color: DesignTokens.Background.raised, location: 0.5),
                        ],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                        .strokeBorder(gate.phase.color.opacity(0.22), lineWidth: 0.5)
                )
        )
        .phaseGlow(gate.phase, intensity: gate.status == .pending ? 0.4 : 0.1)
    }
}

// MARK: - Gate sticky banner (workspace top)

struct GateStickyBanner: View {
    let gate: DecisionGate.Full
    var onExpand: (() -> Void)? = nil
    var onDismiss: (() -> Void)? = nil

    private var passedCount: Int {
        gate.criteria.filter { $0.status == .pass }.count
    }

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: "diamond.fill")
                .font(.system(size: 14))
                .foregroundStyle(gate.phase.color)

            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(gate.phase.gateTitle)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                    StatusPill(label: gate.status.label, color: gate.status.pillColor)
                }
                Text("\(passedCount)/\(gate.criteria.count) criteria met · awaiting your approval")
                    .font(.system(size: 10))
                    .foregroundStyle(DesignTokens.Foreground.secondary)
            }

            Spacer(minLength: 0)

            PhaseButton(label: "Review", phase: gate.phase) { onExpand?() }

            if onDismiss != nil {
                SquareIconButton(symbol: "xmark", size: 24) { onDismiss?() }
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(
            gate.phase.color.opacity(0.10)
                .shadow(.inner(color: gate.phase.color.opacity(0.20), radius: 1, y: -1))
        )
        .overlay(
            Rectangle()
                .fill(gate.phase.color.opacity(0.26))
                .frame(height: 1),
            alignment: .bottom
        )
    }
}

// MARK: - Gate modal (full-screen overlay)

struct GateModal: View {
    let gate: DecisionGate.Full
    var onClose: () -> Void

    var body: some View {
        ZStack {
            DesignTokens.Background.overlay
                .ignoresSafeArea()
                .onTapGesture { onClose() }

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    GateCore(gate: gate, compact: false)
                        .padding(28)
                }
                .frame(width: 620)
            }
            .frame(maxWidth: 620, maxHeight: min(NSScreen.main?.frame.height ?? 800 * 0.88, 700))
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.Radius.xl)
                    .fill(DesignTokens.Background.raised)
                    .overlay(
                        RoundedRectangle(cornerRadius: DesignTokens.Radius.xl)
                            .strokeBorder(gate.phase.color.opacity(0.24), lineWidth: 0.5)
                    )
                    .shadow(color: .black.opacity(0.7), radius: 40, y: 20)
                    .shadow(color: gate.phase.glowColor.opacity(0.14), radius: 80)
            )
            .overlay(alignment: .topTrailing) {
                SquareIconButton(symbol: "xmark") { onClose() }
                    .padding(14)
            }
        }
        .animation(.easeOut(duration: 0.22), value: true)
    }
}

// MARK: - Flow layout (wrapping HStack)

private struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(width: proposal.replacingUnspecifiedDimensions().width,
                                spacing: spacing, subviews: subviews)
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(width: bounds.width, spacing: spacing, subviews: subviews)
        for (idx, frame) in result.frames.enumerated() {
            subviews[idx].place(at: CGPoint(x: bounds.minX + frame.minX,
                                            y: bounds.minY + frame.minY),
                               proposal: ProposedViewSize(frame.size))
        }
    }

    private struct FlowResult {
        var size: CGSize = .zero
        var frames: [CGRect] = []

        init(width: CGFloat, spacing: CGFloat, subviews: Subviews) {
            var x: CGFloat = 0, y: CGFloat = 0, rowHeight: CGFloat = 0

            for subview in subviews {
                let sz = subview.sizeThatFits(.unspecified)
                if x + sz.width > width && x > 0 {
                    x = 0; y += rowHeight + spacing; rowHeight = 0
                }
                frames.append(CGRect(origin: CGPoint(x: x, y: y), size: sz))
                x += sz.width + spacing
                rowHeight = max(rowHeight, sz.height)
            }
            size = CGSize(width: width, height: y + rowHeight)
        }
    }
}

// MARK: - Color blend helper

extension Color {
    func blended(with other: Color, by fraction: Double = 0.5) -> Color {
        self.opacity(1 - fraction)
    }
}

#Preview("Gate Card") {
    ScrollView {
        GateInlineCard(gate: SampleData.activeGate)
            .padding(20)
    }
    .background(DesignTokens.Background.base)
    .frame(width: 560)
    .preferredColorScheme(.dark)
}
