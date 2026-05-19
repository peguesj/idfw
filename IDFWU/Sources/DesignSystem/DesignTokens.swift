import SwiftUI

// MARK: - Phase color system (OKLCH → sRGB approximations)

extension IDEAPhase {
    /// Primary phase accent — the main "phase color" used for glows, fills, and tints.
    var color: Color {
        switch self {
        case .ideation:    return DesignTokens.Phase.ideation
        case .definition:  return DesignTokens.Phase.definition
        case .evaluation:  return DesignTokens.Phase.evaluation
        case .application: return DesignTokens.Phase.application
        }
    }

    /// Glow shadow color (lower opacity).
    var glowColor: Color { color.opacity(0.35) }

    /// Tinted surface fill — phase color at 14% opacity.
    func tint(_ opacity: Double = 0.14) -> Color { color.opacity(opacity) }

    /// Builder-display labels (match storyboard).
    var builderTitle: String {
        switch self {
        case .ideation:    return "Discover"
        case .definition:  return "Define"
        case .evaluation:  return "Plan"
        case .application: return "Execute"
        }
    }

    var builderSubtitle: String {
        switch self {
        case .ideation:    return "Capture the concept"
        case .definition:  return "Docs, schemas, diagrams"
        case .evaluation:  return "Constraints, risk, milestones"
        case .application: return "Build, deploy, deliver"
        }
    }

    /// Gate metadata for this phase.
    var gateTitle: String {
        switch self {
        case .ideation:    return "Discovery Gate"
        case .definition:  return "Definition Gate"
        case .evaluation:  return "Planning Gate"
        case .application: return "Deployment Readiness"
        }
    }

    var gateTagline: String {
        switch self {
        case .ideation:    return "Confirm the problem is well-formed before defining the solution."
        case .definition:  return "Approve the PRD and architecture before planning."
        case .evaluation:  return "Validate the plan before execution starts."
        case .application: return "Final approval before shipping to production."
        }
    }
}

// MARK: - Design Token Namespace

enum DesignTokens {

    // MARK: Phase (OKLCH approximations)
    enum Phase {
        /// oklch(80% 0.14 65) — warm peach
        static let ideation    = Color(red: 0.985, green: 0.800, blue: 0.560)
        /// oklch(70% 0.18 250) — electric blue
        static let definition  = Color(red: 0.380, green: 0.660, blue: 0.970)
        /// oklch(76% 0.16 55) — warm orange
        static let evaluation  = Color(red: 0.980, green: 0.760, blue: 0.420)
        /// oklch(75% 0.18 145) — vibrant green
        static let application = Color(red: 0.400, green: 0.870, blue: 0.560)
    }

    // MARK: Background
    enum Background {
        /// oklch(11% 0.008 250) — very dark navy
        static let base    = Color(red: 0.052, green: 0.059, blue: 0.078)
        /// oklch(14% 0.010 250)
        static let surface = Color(red: 0.075, green: 0.086, blue: 0.114)
        /// oklch(17% 0.012 250)
        static let raised  = Color(red: 0.095, green: 0.110, blue: 0.148)
        /// oklch(9% 0.006 250) — darkest, sidebar
        static let sunken  = Color(red: 0.038, green: 0.043, blue: 0.058)
        /// 88% opacity overlay
        static let overlay = Color(red: 0.028, green: 0.032, blue: 0.044).opacity(0.88)
    }

    // MARK: Foreground
    enum Foreground {
        /// oklch(92% 0.008 250) — near white
        static let primary   = Color(red: 0.920, green: 0.924, blue: 0.940)
        /// oklch(70% 0.010 250)
        static let secondary = Color(red: 0.640, green: 0.648, blue: 0.680)
        /// oklch(50% 0.010 250)
        static let tertiary  = Color(red: 0.430, green: 0.436, blue: 0.460)
        /// oklch(33% 0.010 250)
        static let quaternary = Color(red: 0.260, green: 0.264, blue: 0.280)
    }

    // MARK: Gate status
    enum Gate {
        /// oklch(72% 0.19 145) — green
        static let passed  = Color(red: 0.296, green: 0.847, blue: 0.478)
        /// oklch(82% 0.17 85) — amber
        static let pending = Color(red: 0.945, green: 0.798, blue: 0.290)
        /// oklch(67% 0.22 25) — red
        static let failed  = Color(red: 0.940, green: 0.318, blue: 0.230)
        /// oklch(60% 0.04 250) — slate
        static let waived  = Color(red: 0.490, green: 0.556, blue: 0.666)
    }

    // MARK: Providers
    enum Provider {
        /// oklch(72% 0.15 40) — copper
        static let claude  = Color(red: 0.815, green: 0.476, blue: 0.314)
        /// oklch(75% 0.14 155) — pale green
        static let codex   = Color(red: 0.376, green: 0.800, blue: 0.540)
        /// oklch(68% 0.20 265) — blue
        static let gemini  = Color(red: 0.294, green: 0.510, blue: 0.940)
        /// oklch(65% 0.06 245) — slate
        static let copilot = Color(red: 0.440, green: 0.565, blue: 0.722)
    }

    // MARK: Schema types
    enum Schema {
        static let idfw  = Color(red: 0.296, green: 0.522, blue: 0.940)
        static let iddv  = Color(red: 0.565, green: 0.376, blue: 0.910)
        static let iddg  = Color(red: 0.847, green: 0.627, blue: 0.314)
        static let iddc  = Color(red: 0.314, green: 0.784, blue: 0.471)
        static let idda  = Color(red: 0.910, green: 0.314, blue: 0.251)
        static let idfpj = Color(red: 0.188, green: 0.784, blue: 0.784)
        static let ddd   = Color(red: 0.376, green: 0.376, blue: 0.847)
        static let idpc  = Color(red: 0.910, green: 0.816, blue: 0.251)
        static let idpg  = Color(red: 0.376, green: 0.847, blue: 0.659)
    }

    // MARK: Hairline borders
    enum Hairline {
        static let soft  = Color.white.opacity(0.06)
        static let bold  = Color.white.opacity(0.10)
        static let phase = Color.white.opacity(0.14)
    }

    // MARK: Glass surfaces
    enum Glass {
        static let thin  = Color.white.opacity(0.04)
        static let tint  = Color.white.opacity(0.06)
        static let thick = Color.white.opacity(0.08)
    }

    // MARK: Typography
    enum Font {
        static func display(_ size: CGFloat, weight: SwiftUI.Font.Weight = .bold) -> SwiftUI.Font {
            .system(size: size, weight: weight, design: .default)
        }
        static func mono(_ size: CGFloat, weight: SwiftUI.Font.Weight = .regular) -> SwiftUI.Font {
            .system(size: size, weight: weight, design: .monospaced)
        }
        static func overline(_ size: CGFloat = 10) -> SwiftUI.Font {
            .system(size: size, weight: .semibold, design: .default)
                .uppercaseSmallCaps()
        }
    }

    // MARK: Radius
    enum Radius {
        static let xs: CGFloat = 4
        static let sm: CGFloat = 6
        static let md: CGFloat = 8
        static let lg: CGFloat = 12
        static let xl: CGFloat = 16
        static let full: CGFloat = 999
    }

    // MARK: Spacing (4pt grid)
    enum Space {
        static let s1: CGFloat = 4
        static let s2: CGFloat = 8
        static let s3: CGFloat = 12
        static let s4: CGFloat = 16
        static let s5: CGFloat = 20
        static let s6: CGFloat = 24
        static let s8: CGFloat = 32
        static let s10: CGFloat = 40
        static let s12: CGFloat = 48
    }

    // MARK: Layout
    enum Layout {
        static let navWidth: CGFloat = 232
        static let workspaceWidth: CGFloat = 460
        static let minWindowWidth: CGFloat = 1080
        static let minWindowHeight: CGFloat = 680
    }
}

// MARK: - Gate status extensions

extension DecisionGate.GateStatus {
    var color: Color {
        switch self {
        case .pending: return DesignTokens.Gate.pending
        case .passed:  return DesignTokens.Gate.passed
        case .failed:  return DesignTokens.Gate.failed
        case .waived:  return DesignTokens.Gate.waived
        }
    }

    var label: String {
        switch self {
        case .pending: return "pending"
        case .passed:  return "passed"
        case .failed:  return "failed"
        case .waived:  return "waived"
        }
    }

    var symbol: String {
        switch self {
        case .pending: return "circle.fill"
        case .passed:  return "checkmark.circle.fill"
        case .failed:  return "xmark.circle.fill"
        case .waived:  return "minus.circle.fill"
        }
    }
}

// MARK: - View modifiers

struct GlassCard: ViewModifier {
    var elevated: Bool = false
    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                    .fill(elevated ? DesignTokens.Background.raised : DesignTokens.Background.surface)
                    .overlay(
                        RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                            .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 1)
                    )
            )
    }
}

struct PhaseGlow: ViewModifier {
    let phase: IDEAPhase
    let intensity: Double

    func body(content: Content) -> some View {
        content
            .shadow(color: phase.glowColor.opacity(intensity), radius: 24, x: 0, y: 0)
            .shadow(color: phase.glowColor.opacity(intensity * 0.5), radius: 48, x: 0, y: 8)
    }
}

extension View {
    func glassCard(elevated: Bool = false) -> some View {
        modifier(GlassCard(elevated: elevated))
    }

    func phaseGlow(_ phase: IDEAPhase, intensity: Double = 0.6) -> some View {
        modifier(PhaseGlow(phase: phase, intensity: intensity))
    }
}
