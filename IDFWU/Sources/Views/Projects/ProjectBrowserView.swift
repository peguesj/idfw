import SwiftUI

// MARK: - Project browser grid

struct ProjectBrowserView: View {
    var projects: [BuilderProject] = SampleData.projects
    var onSelectProject: ((BuilderProject) -> Void)? = nil

    private let columns = [
        GridItem(.adaptive(minimum: 220, maximum: 320), spacing: 14)
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Header
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Projects")
                            .font(.system(size: 20, weight: .bold))
                            .foregroundStyle(DesignTokens.Foreground.primary)
                        Text("\(projects.count) projects · \(activeCount) active")
                            .font(.system(size: 12))
                            .foregroundStyle(DesignTokens.Foreground.tertiary)
                    }
                    Spacer()
                    Button(action: {}) {
                        HStack(spacing: 5) {
                            Image(systemName: "plus")
                                .font(.system(size: 11, weight: .bold))
                            Text("New project")
                                .font(.system(size: 12, weight: .medium))
                        }
                        .foregroundStyle(Color(red: 0.08, green: 0.09, blue: 0.12))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(
                            Capsule().fill(DesignTokens.Phase.definition)
                        )
                    }
                    .buttonStyle(.plain)
                }
                .padding(.horizontal, 24)
                .padding(.top, 20)

                // Grid
                LazyVGrid(columns: columns, spacing: 14) {
                    ForEach(projects) { project in
                        ProjectCard(project: project) {
                            onSelectProject?(project)
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 24)
            }
        }
        .background(DesignTokens.Background.base)
    }

    private var activeCount: Int {
        projects.filter { $0.phase == .application || $0.phase == .evaluation }.count
    }
}

// MARK: - Project card

private struct ProjectCard: View {
    let project: BuilderProject
    let action: () -> Void

    @State private var hovered = false

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 0) {
                // Phase glow top strip
                LinearGradient(
                    colors: [project.phase.color.opacity(0.7), .clear],
                    startPoint: .leading,
                    endPoint: .trailing
                )
                .frame(height: 2)

                VStack(alignment: .leading, spacing: 12) {
                    // Header row
                    HStack(spacing: 10) {
                        IDEAPhaseLetter(phase: project.phase, size: .md, state: .active)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(project.name)
                                .font(.system(size: 13, weight: .semibold))
                                .foregroundStyle(DesignTokens.Foreground.primary)
                                .lineLimit(1)
                            PhaseChip(phase: project.phase)
                        }
                        Spacer(minLength: 0)
                        ProviderGlyph(kind: project.provider, size: 14)
                    }

                    // Description
                    Text(project.description)
                        .font(.system(size: 11))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)

                    // Mini stepper
                    IDEAStepperView(
                        currentPhase: project.phase,
                        gateStatuses: project.gateStatuses,
                        variant: .mini
                    )

                    // Footer
                    HStack {
                        Text(relativeTime(project.updatedAt))
                            .font(.system(size: 9))
                            .foregroundStyle(DesignTokens.Foreground.quaternary)
                        Spacer()
                        gateStatusBadge
                    }
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 12)
            }
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                    .fill(hovered ? DesignTokens.Background.raised : DesignTokens.Background.surface)
                    .overlay(
                        RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                            .strokeBorder(
                                hovered
                                ? project.phase.color.opacity(0.30)
                                : DesignTokens.Hairline.soft,
                                lineWidth: 0.5
                            )
                    )
            )
            .shadow(color: hovered ? project.phase.glowColor.opacity(0.15) : .clear, radius: 16)
        }
        .buttonStyle(.plain)
        .onHover { hovered = $0 }
        .animation(.easeOut(duration: 0.15), value: hovered)
    }

    @ViewBuilder
    private var gateStatusBadge: some View {
        let pendingGate = project.gateStatuses
            .first(where: { $0.value == .pending })
        if let gate = pendingGate {
            HStack(spacing: 3) {
                Image(systemName: "diamond.fill")
                    .font(.system(size: 7))
                Text("gate pending")
                    .font(.system(size: 9))
            }
            .foregroundStyle(DesignTokens.Gate.pending)
        }
    }

    private func relativeTime(_ date: Date) -> String {
        let diff = Date().timeIntervalSince(date)
        if diff < 60 { return "just now" }
        if diff < 3600 { return "\(Int(diff / 60))m ago" }
        if diff < 86400 { return "\(Int(diff / 3600))h ago" }
        return "\(Int(diff / 86400))d ago"
    }
}
