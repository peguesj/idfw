import SwiftUI

// MARK: - Phase Letter Badge

struct IDEAPhaseLetter: View {
    let phase: IDEAPhase
    var size: LetterSize = .md
    var state: LetterState = .active

    enum LetterSize {
        case sm, md, lg, xl
        var dimension: CGFloat {
            switch self { case .sm: 20; case .md: 28; case .lg: 36; case .xl: 56 }
        }
        var fontSize: CGFloat {
            switch self { case .sm: 11; case .md: 13; case .lg: 17; case .xl: 24 }
        }
        var radius: CGFloat {
            switch self { case .sm: 6; case .md: 8; case .lg: 10; case .xl: 14 }
        }
    }

    enum LetterState { case active, done, todo }

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: size.radius)
                .fill(bgFill)
                .overlay(
                    RoundedRectangle(cornerRadius: size.radius)
                        .strokeBorder(borderColor, lineWidth: 1)
                )
            if state == .done {
                Image(systemName: "checkmark")
                    .font(.system(size: size.fontSize * 0.9, weight: .bold))
                    .foregroundStyle(phase.color)
            } else {
                Text(phase.letter)
                    .font(.system(size: size.fontSize, weight: .bold, design: .rounded))
                    .foregroundStyle(textColor)
            }
        }
        .frame(width: size.dimension, height: size.dimension)
    }

    private var bgFill: Color {
        switch state {
        case .active: phase.color
        case .done:   phase.color.opacity(0.28)
        case .todo:   DesignTokens.Background.surface
        }
    }

    private var textColor: Color {
        switch state {
        case .active: Color(red: 0.08, green: 0.09, blue: 0.12)
        case .done:   phase.color
        case .todo:   DesignTokens.Foreground.tertiary
        }
    }

    private var borderColor: Color {
        state == .todo ? DesignTokens.Hairline.soft : phase.color.opacity(0.30)
    }
}

// MARK: - Status Pill

struct StatusPill: View {
    let label: String
    var color: PillColor = .neutral

    enum PillColor {
        case neutral, pending, passed, failed, waived, live
        var fg: Color {
            switch self {
            case .neutral:  return DesignTokens.Foreground.tertiary
            case .pending:  return DesignTokens.Gate.pending
            case .passed:   return DesignTokens.Gate.passed
            case .failed:   return DesignTokens.Gate.failed
            case .waived:   return DesignTokens.Gate.waived
            case .live:     return Color(red: 0.4, green: 0.87, blue: 0.56)
            }
        }
        var bg: Color { fg.opacity(0.14) }
    }

    var body: some View {
        Text(label)
            .font(.system(size: 10, weight: .semibold))
            .foregroundStyle(color.fg)
            .padding(.horizontal, 7)
            .padding(.vertical, 2)
            .background(
                Capsule().fill(color.bg)
                    .overlay(Capsule().strokeBorder(color.fg.opacity(0.25), lineWidth: 0.5))
            )
    }
}

extension DecisionGate.GateStatus {
    var pillColor: StatusPill.PillColor {
        switch self {
        case .pending: return .pending
        case .passed:  return .passed
        case .failed:  return .failed
        case .waived:  return .waived
        }
    }
}

// MARK: - Status Dot

struct StatusDot: View {
    let color: Color
    var live: Bool = false
    var size: CGFloat = 6

    @State private var pulse = false

    var body: some View {
        Circle()
            .fill(color)
            .frame(width: size, height: size)
            .shadow(color: color.opacity(0.6), radius: live ? 4 : 0)
            .scaleEffect(live && pulse ? 1.25 : 1.0)
            .onAppear {
                guard live else { return }
                withAnimation(.easeInOut(duration: 1.2).repeatForever(autoreverses: true)) {
                    pulse = true
                }
            }
    }
}

// MARK: - Provider glyph

struct ProviderGlyph: View {
    let kind: AIProviderKind
    var size: CGFloat = 16

    var body: some View {
        switch kind {
        case .claude:
            ClaudeGlyph(size: size)
        case .codex:
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: size))
                .foregroundStyle(DesignTokens.Provider.codex)
        case .gemini:
            Image(systemName: "sparkle")
                .font(.system(size: size))
                .foregroundStyle(DesignTokens.Provider.gemini)
        case .copilot:
            Image(systemName: "figure.stand")
                .font(.system(size: size))
                .foregroundStyle(DesignTokens.Provider.copilot)
        }
    }
}

private struct ClaudeGlyph: View {
    let size: CGFloat
    var body: some View {
        Canvas { ctx, sz in
            let mid = CGPoint(x: sz.width / 2, y: sz.height / 2)
            let r = min(sz.width, sz.height) / 2 * 0.82
            var tri = Path()
            tri.move(to: CGPoint(x: mid.x, y: mid.y - r))
            tri.addLine(to: CGPoint(x: mid.x + r * 0.866, y: mid.y + r * 0.5))
            tri.addLine(to: CGPoint(x: mid.x - r * 0.866, y: mid.y + r * 0.5))
            tri.closeSubpath()
            ctx.fill(tri, with: .color(DesignTokens.Provider.claude))
        }
        .frame(width: size, height: size)
    }
}

// MARK: - Provider chip (button)

struct ProviderChip: View {
    let kind: AIProviderKind
    var active: Bool = false
    var action: (() -> Void)?

    var body: some View {
        Button(action: { action?() }) {
            HStack(spacing: 5) {
                ProviderGlyph(kind: kind, size: 13)
                Text(kind.displayName)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(DesignTokens.Foreground.secondary)
                StatusDot(color: kind.color, live: active)
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill(kind.color.opacity(0.10))
                    .overlay(Capsule().strokeBorder(kind.color.opacity(0.25), lineWidth: 0.5))
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Phase Chip

struct PhaseChip: View {
    let phase: IDEAPhase
    var label: String? = nil

    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(phase.color)
                .frame(width: 5, height: 5)
            Text(label ?? phase.builderTitle)
                .font(.system(size: 10, weight: .semibold))
                .foregroundStyle(phase.color)
        }
        .padding(.horizontal, 7)
        .padding(.vertical, 2)
        .background(Capsule().fill(phase.color.opacity(0.12)))
    }
}

// MARK: - Overline label

struct OverlineLabel: View {
    let text: String
    var body: some View {
        Text(text.uppercased())
            .font(.system(size: 10, weight: .semibold))
            .foregroundStyle(DesignTokens.Foreground.tertiary)
            .tracking(0.6)
    }
}

// MARK: - Avatar

struct MessageAvatar: View {
    var isBot: Bool = false
    var name: String = "Y"
    var providerKind: AIProviderKind? = nil

    var body: some View {
        Group {
            if let kind = providerKind {
                ZStack {
                    RoundedRectangle(cornerRadius: isBot ? 8 : 14)
                        .fill(kind.color.opacity(0.14))
                        .overlay(
                            RoundedRectangle(cornerRadius: isBot ? 8 : 14)
                                .strokeBorder(kind.color.opacity(0.25), lineWidth: 0.5)
                        )
                    ProviderGlyph(kind: kind, size: 14)
                }
            } else {
                ZStack {
                    Circle()
                        .fill(DesignTokens.Foreground.tertiary.opacity(0.14))
                    Text(String(name.prefix(1)).uppercased())
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                }
            }
        }
        .frame(width: 28, height: 28)
    }
}

// MARK: - Icon button (small square button)

struct SquareIconButton: View {
    let symbol: String
    var size: CGFloat = 28
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            Image(systemName: symbol)
                .font(.system(size: 12, weight: .medium))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
                .frame(width: size, height: size)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .fill(DesignTokens.Glass.thin)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                        )
                )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Brand mark

struct BrandMark: View {
    var size: CGFloat = 26

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: size * 0.28)
                .fill(
                    LinearGradient(
                        stops: [
                            .init(color: DesignTokens.Phase.definition, location: 0),
                            .init(color: DesignTokens.Phase.ideation, location: 1),
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .shadow(color: DesignTokens.Phase.definition.opacity(0.35), radius: 8)
            Image(systemName: "cube.fill")
                .font(.system(size: size * 0.40, weight: .bold))
                .foregroundStyle(Color(red: 0.08, green: 0.09, blue: 0.12))
        }
        .frame(width: size, height: size)
    }
}

// MARK: - Segmented control

struct SegmentedControl<T: Hashable>: View {
    let options: [(T, String)]
    @Binding var selection: T

    var body: some View {
        HStack(spacing: 2) {
            ForEach(options, id: \.0) { value, label in
                Button(action: { selection = value }) {
                    Text(label)
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(
                            selection == value
                            ? DesignTokens.Foreground.primary
                            : DesignTokens.Foreground.tertiary
                        )
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(
                            RoundedRectangle(cornerRadius: 5)
                                .fill(selection == value
                                      ? DesignTokens.Background.raised
                                      : Color.clear)
                        )
                }
                .buttonStyle(.plain)
            }
        }
        .padding(3)
        .background(
            RoundedRectangle(cornerRadius: 7)
                .fill(DesignTokens.Background.sunken)
                .overlay(
                    RoundedRectangle(cornerRadius: 7)
                        .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                )
        )
    }
}

// MARK: - Phase-colored primary button

struct PhaseButton: View {
    let label: String
    var symbol: String? = nil
    let phase: IDEAPhase
    var disabled: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 5) {
                if let sym = symbol {
                    Image(systemName: sym)
                        .font(.system(size: 12, weight: .semibold))
                }
                Text(label)
                    .font(.system(size: 13, weight: .semibold))
            }
            .foregroundStyle(disabled
                ? DesignTokens.Foreground.quaternary
                : Color(red: 0.08, green: 0.09, blue: 0.12)
            )
            .padding(.horizontal, 14)
            .padding(.vertical, 7)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                    .fill(disabled ? DesignTokens.Background.raised : phase.color)
            )
        }
        .buttonStyle(.plain)
        .disabled(disabled)
    }
}

// MARK: - Daemon status row (sidebar footer)

struct DaemonStatusRow: View {
    var port: Int = 4040
    var latencyMs: Int = 12
    var isLive: Bool = true

    var body: some View {
        HStack(spacing: 8) {
            StatusDot(color: DesignTokens.Phase.application, live: isLive, size: 6)
            Text("daemon · :\(port)")
                .font(.system(size: 10))
                .foregroundStyle(DesignTokens.Foreground.secondary)
            Spacer(minLength: 0)
            Text("\(latencyMs)ms")
                .font(.system(size: 10, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 6)
        .background(
            RoundedRectangle(cornerRadius: 7)
                .fill(DesignTokens.Glass.thin)
                .overlay(
                    RoundedRectangle(cornerRadius: 7)
                        .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                )
        )
    }
}
