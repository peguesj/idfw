import SwiftUI

// MARK: - Left navigation sidebar (232px)

struct LeftNavigation: View {
    @Binding var activeView: BuilderTopView
    var activeProject: BuilderProject?
    var projects: [BuilderProject] = []
    var onOpenSettings: () -> Void
    var onOpenCommandK: () -> Void

    var body: some View {
        VStack(spacing: 14) {
            brandHeader
            searchTrigger
            workspaceGroup
            skillsGroup
            Spacer(minLength: 0)
            if let project = activeProject { activeProjectFooter(project) }
            DaemonStatusRow()
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 12)
        .frame(width: DesignTokens.Layout.navWidth)
        .background(DesignTokens.Background.sunken)
        .overlay(alignment: .trailing) {
            Rectangle()
                .fill(DesignTokens.Hairline.soft)
                .frame(width: 0.5)
        }
    }

    // MARK: Brand

    private var brandHeader: some View {
        HStack(spacing: 10) {
            BrandMark(size: 26)
            VStack(alignment: .leading, spacing: 1) {
                Text("IDFWU")
                    .font(.system(size: 13, weight: .bold))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                Text("Inception Builder")
                    .font(.system(size: 10))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
            }
            Spacer(minLength: 0)
            SquareIconButton(symbol: "gearshape", size: 26) { onOpenSettings() }
        }
        .padding(.horizontal, 6)
    }

    // MARK: Command-K search

    private var searchTrigger: some View {
        Button(action: onOpenCommandK) {
            HStack(spacing: 7) {
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 11))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
                Text("Search · run skill")
                    .font(.system(size: 11))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
                Spacer(minLength: 0)
                Text("⌘K")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundStyle(DesignTokens.Foreground.quaternary)
                    .padding(.horizontal, 4)
                    .padding(.vertical, 2)
                    .background(RoundedRectangle(cornerRadius: 4).fill(DesignTokens.Glass.thin))
            }
            .padding(.horizontal, 10)
            .frame(height: 30)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.Radius.sm)
                    .fill(DesignTokens.Background.surface)
                    .overlay(
                        RoundedRectangle(cornerRadius: DesignTokens.Radius.sm)
                            .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                    )
            )
        }
        .buttonStyle(.plain)
    }

    // MARK: Workspace nav group

    private var workspaceGroup: some View {
        NavGroup(title: "Workspace") {
            NavRow(icon: "sparkles", label: "Builder",
                   active: activeView == .builder, phase: .definition) {
                activeView = .builder
            }
            NavRow(icon: "square.grid.2x2", label: "Projects",
                   badge: projects.count, active: activeView == .browser) {
                activeView = .browser
            }
            NavRow(icon: "antenna.radiowaves.left.and.right", label: "Inspector",
                   active: activeView == .inspector) {
                activeView = .inspector
            }
            NavRow(icon: "point.3.connected.trianglepath.dotted", label: "Agent graph",
                   active: activeView == .graph) {
                activeView = .graph
            }
            NavRow(icon: "chart.xyaxis.line", label: "HyperPlot",
                   active: activeView == .hyperplot) {
                activeView = .hyperplot
            }
        }
    }

    // MARK: Skills group

    private var skillsGroup: some View {
        NavGroup(title: "Skills", trailing: AnyView(
            SquareIconButton(symbol: "ellipsis", size: 22) {}
        )) {
            ForEach(SampleData.skills.prefix(8)) { skill in
                NavRow(icon: "bolt", label: skill.title, phase: skill.phase,
                       mono: true, small: true) {}
            }
        }
    }

    // MARK: Active project footer

    @ViewBuilder
    private func activeProjectFooter(_ project: BuilderProject) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                StatusDot(color: project.phase.color,
                          live: true, size: 7)
                    .shadow(color: project.phase.glowColor, radius: 4)
                Text(project.name)
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                    .lineLimit(1)
                Spacer(minLength: 0)
                StatusPill(label: "live", color: .live)
            }
            Text(project.description)
                .font(.system(size: 9))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
                .lineLimit(2)
            IDEAStepperView(
                currentPhase: project.phase,
                gateStatuses: project.gateStatuses,
                variant: .mini
            )
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 10)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(DesignTokens.Glass.thin)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                )
        )
    }
}

// MARK: - Nav group

private struct NavGroup<Content: View>: View {
    let title: String
    var trailing: AnyView? = nil
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 1) {
            HStack(spacing: 6) {
                OverlineLabel(text: title)
                Spacer(minLength: 0)
                if let t = trailing { t }
            }
            .padding(.horizontal, 8)
            .padding(.top, 6)
            .padding(.bottom, 3)

            content()
        }
    }
}

// MARK: - Nav row

private struct NavRow: View {
    let icon: String
    let label: String
    var badge: Int? = nil
    var active: Bool = false
    var phase: IDEAPhase? = nil
    var mono: Bool = false
    var small: Bool = false
    let action: () -> Void

    @State private var hovered = false

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.system(size: small ? 11 : 13))
                    .foregroundStyle(iconColor)
                    .frame(width: 14)

                Text(label)
                    .font(small
                          ? .system(size: 11, weight: active ? .semibold : .medium, design: mono ? .monospaced : .default)
                          : .system(size: 12, weight: active ? .semibold : .medium))
                    .foregroundStyle(textColor)
                    .lineLimit(1)

                Spacer(minLength: 0)

                if let badge {
                    Text("\(badge)")
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                        .padding(.horizontal, 5)
                        .padding(.vertical, 1)
                        .background(Capsule().fill(DesignTokens.Glass.thin))
                }
            }
            .padding(.horizontal, 8)
            .padding(.vertical, small ? 4 : 6)
            .background(
                RoundedRectangle(cornerRadius: 6)
                    .fill(rowBg)
            )
        }
        .buttonStyle(.plain)
        .onHover { hovered = $0 }
    }

    private var rowBg: Color {
        if active {
            return (phase ?? .definition).color.opacity(0.14)
        }
        return hovered ? DesignTokens.Glass.thin : .clear
    }

    private var textColor: Color {
        active ? (phase ?? .definition).color : DesignTokens.Foreground.secondary
    }

    private var iconColor: Color {
        active ? (phase ?? .definition).color : (phase?.color ?? DesignTokens.Foreground.tertiary)
    }
}

// MARK: - Top-level view enum

enum BuilderTopView: String {
    case builder
    case browser
    case inspector
    case graph
    case hyperplot
}
