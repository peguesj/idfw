import SwiftUI

// MARK: - Workspace pane (460px right panel)

struct WorkspacePane: View {
    let project: BuilderProject
    var activeGate: DecisionGate.Full?
    @State private var selectedTab: WorkspaceTab = .artifact
    @State private var showGateModal = false

    var body: some View {
        VStack(spacing: 0) {
            // Compact stepper at top
            IDEAStepperView(
                currentPhase: project.phase,
                gateStatuses: project.gateStatuses,
                variant: .compact
            )
            .padding(.horizontal, 14)
            .padding(.vertical, 8)
            .background(DesignTokens.Background.sunken)
            .overlay(alignment: .bottom) {
                Rectangle().fill(DesignTokens.Hairline.soft).frame(height: 0.5)
            }

            // Sticky gate banner (when gate is pending)
            if let gate = activeGate, gate.status == .pending {
                GateStickyBanner(gate: gate, onExpand: { showGateModal = true })
            }

            // Tab strip
            tabStrip

            // Tab content
            tabContent
        }
        .frame(width: DesignTokens.Layout.workspaceWidth)
        .background(DesignTokens.Background.surface)
        .overlay(alignment: .leading) {
            Rectangle().fill(DesignTokens.Hairline.soft).frame(width: 0.5)
        }
        .sheet(isPresented: $showGateModal) {
            if let gate = activeGate {
                GateModal(gate: gate) { showGateModal = false }
            }
        }
    }

    // MARK: Tab strip

    private var tabStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 0) {
                ForEach(WorkspaceTab.allCases) { tab in
                    tabButton(tab)
                }
            }
            .padding(.horizontal, 8)
        }
        .frame(height: 38)
        .background(DesignTokens.Background.sunken)
        .overlay(alignment: .bottom) {
            Rectangle().fill(DesignTokens.Hairline.soft).frame(height: 0.5)
        }
    }

    private func tabButton(_ tab: WorkspaceTab) -> some View {
        let active = selectedTab == tab
        return Button(action: { selectedTab = tab }) {
            HStack(spacing: 5) {
                Image(systemName: tab.symbol)
                    .font(.system(size: 10, weight: active ? .semibold : .regular))
                Text(tab.rawValue)
                    .font(.system(size: 11, weight: active ? .semibold : .regular))
            }
            .foregroundStyle(active ? DesignTokens.Foreground.primary : DesignTokens.Foreground.tertiary)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .overlay(alignment: .bottom) {
                if active {
                    Rectangle()
                        .fill(project.phase.color)
                        .frame(height: 2)
                        .matchedGeometryEffect(id: "tab-indicator", in: tabNamespace)
                }
            }
        }
        .buttonStyle(.plain)
    }

    @Namespace private var tabNamespace

    // MARK: Tab content

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case .artifact:
            ArtifactTabView(markdownContent: SampleData.activePRD)
        case .files:
            FilesTabView(tree: SampleData.fileTree)
        case .diagram:
            DiagramTabView(
                source: "graph LR\n    A[Explorer] --> B{Wayfinder AI}\n    B --> C[Route Engine]\n    B --> D[Context Memory]\n    C --> E[Map Data]\n    D --> F[User Prefs]",
                kind: .mermaid
            )
        case .plan:
            PlanTabView(milestones: SampleData.milestones, risks: SampleData.risks)
        case .hyperplot:
            HyperPlotTabView(axes: SampleData.hyperPlotAxes)
        case .telemetry:
            TelemetryTabView(
                nodes: SampleData.graphNodes,
                edges: SampleData.graphEdges,
                events: SampleData.events
            )
        }
    }
}

// MARK: - Artifact tab

struct ArtifactTabView: View {
    let markdownContent: String
    @State private var mode: ViewMode = .preview

    enum ViewMode: String, CaseIterable { case preview = "Preview", source = "Source", split = "Split" }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Spacer()
                SegmentedControl(
                    options: ViewMode.allCases.map { ($0, $0.rawValue) },
                    selection: $mode
                )
                .padding(.trailing, 14)
                Spacer()
            }
            .padding(.vertical, 8)
            .background(DesignTokens.Background.sunken)
            .overlay(alignment: .bottom) {
                Rectangle().fill(DesignTokens.Hairline.soft).frame(height: 0.5)
            }

            ScrollView {
                switch mode {
                case .preview:
                    MarkdownLiteView(content: markdownContent)
                        .padding(16)
                case .source:
                    Text(markdownContent)
                        .font(.system(size: 11, design: .monospaced))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                        .textSelection(.enabled)
                        .padding(16)
                        .frame(maxWidth: .infinity, alignment: .leading)
                case .split:
                    HStack(alignment: .top, spacing: 0) {
                        Text(markdownContent)
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundStyle(DesignTokens.Foreground.secondary)
                            .textSelection(.enabled)
                            .padding(12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Divider().background(DesignTokens.Hairline.soft)
                        MarkdownLiteView(content: markdownContent)
                            .padding(12)
                    }
                }
            }
        }
    }
}

// MARK: - Markdown lite renderer

struct MarkdownLiteView: View {
    let content: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(Array(lines.enumerated()), id: \.offset) { _, line in
                lineView(line)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var lines: [String] { content.components(separatedBy: "\n") }

    @ViewBuilder
    private func lineView(_ line: String) -> some View {
        if line.hasPrefix("# ") {
            Text(line.dropFirst(2))
                .font(.system(size: 18, weight: .bold))
                .foregroundStyle(DesignTokens.Foreground.primary)
        } else if line.hasPrefix("## ") {
            Text(line.dropFirst(3))
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(DesignTokens.Foreground.primary)
                .padding(.top, 8)
        } else if line.hasPrefix("### ") {
            Text(line.dropFirst(4))
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(DesignTokens.Foreground.secondary)
                .padding(.top, 4)
        } else if line.hasPrefix("- ") {
            HStack(alignment: .top, spacing: 6) {
                Text("·")
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
                Text(line.dropFirst(2))
                    .font(.system(size: 12))
                    .foregroundStyle(DesignTokens.Foreground.primary)
            }
        } else if line.isEmpty {
            Spacer().frame(height: 4)
        } else {
            Text(line)
                .font(.system(size: 12))
                .foregroundStyle(DesignTokens.Foreground.primary)
        }
    }
}

// MARK: - Files tab

struct FilesTabView: View {
    let tree: [FileEntry]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 1) {
                ForEach(tree) { entry in
                    FileEntryRow(entry: entry, depth: 0)
                }
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
        }
    }
}

private struct FileEntryRow: View {
    let entry: FileEntry
    let depth: Int
    @State private var expanded = true

    var body: some View {
        VStack(alignment: .leading, spacing: 1) {
            Button(action: {
                if entry.isDirectory { withAnimation { expanded.toggle() } }
            }) {
                HStack(spacing: 6) {
                    Color.clear.frame(width: CGFloat(depth) * 14)
                    Image(systemName: entry.isDirectory
                        ? (expanded ? "chevron.down" : "chevron.right")
                        : "doc.fill")
                        .font(.system(size: 10))
                        .foregroundStyle(entry.phase?.color ?? DesignTokens.Foreground.tertiary)
                        .frame(width: 12)
                    Text(entry.name)
                        .font(.system(size: 11, design: entry.isDirectory ? .default : .monospaced))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                    Spacer(minLength: 0)
                    if let size = entry.size, !entry.isDirectory {
                        Text(formatSize(size))
                            .font(.system(size: 9))
                            .foregroundStyle(DesignTokens.Foreground.quaternary)
                    }
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            if expanded, let children = entry.children {
                ForEach(children) { child in
                    FileEntryRow(entry: child, depth: depth + 1)
                }
            }
        }
    }

    private func formatSize(_ bytes: Int) -> String {
        if bytes < 1024 { return "\(bytes)B" }
        return "\(bytes / 1024)KB"
    }
}

// MARK: - Plan tab

struct PlanTabView: View {
    let milestones: [Milestone]
    let risks: [RiskItem]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                // Milestones
                VStack(alignment: .leading, spacing: 6) {
                    OverlineLabel(text: "Milestones")
                        .padding(.bottom, 4)
                    ForEach(milestones) { milestone in
                        MilestoneRow(milestone: milestone)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 14)
                .padding(.bottom, 14)

                Divider().background(DesignTokens.Hairline.soft)

                // Risk matrix
                VStack(alignment: .leading, spacing: 6) {
                    OverlineLabel(text: "Risk Matrix")
                        .padding(.bottom, 4)
                    RiskMatrix(risks: risks)
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 14)
            }
        }
    }
}

private struct MilestoneRow: View {
    let milestone: Milestone

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: milestone.status.symbol)
                .font(.system(size: 13))
                .foregroundStyle(milestone.status.color)
                .frame(width: 16)
            Text(milestone.title)
                .font(.system(size: 12))
                .foregroundStyle(DesignTokens.Foreground.primary)
            Spacer(minLength: 0)
            if let due = milestone.dueDate {
                Text(due)
                    .font(.system(size: 10))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
            }
            PhaseChip(phase: milestone.phase)
        }
        .padding(.vertical, 6)
    }
}

extension Milestone.MilestoneStatus {
    var symbol: String {
        switch self {
        case .done:       return "checkmark.circle.fill"
        case .inProgress: return "circle.fill"
        case .blocked:    return "exclamationmark.circle.fill"
        case .todo:       return "circle"
        }
    }
    var color: Color {
        switch self {
        case .done:       return DesignTokens.Gate.passed
        case .inProgress: return DesignTokens.Gate.pending
        case .blocked:    return DesignTokens.Gate.failed
        case .todo:       return DesignTokens.Foreground.quaternary
        }
    }
}

private struct RiskMatrix: View {
    let risks: [RiskItem]

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Header
            HStack(spacing: 0) {
                Text("Risk")
                    .frame(maxWidth: .infinity, alignment: .leading)
                Text("L")
                    .frame(width: 28, alignment: .center)
                Text("I")
                    .frame(width: 28, alignment: .center)
                Text("Score")
                    .frame(width: 40, alignment: .center)
            }
            .font(.system(size: 9, weight: .semibold))
            .foregroundStyle(DesignTokens.Foreground.tertiary)
            .padding(.horizontal, 8)
            .padding(.bottom, 2)

            ForEach(risks.sorted { $0.score > $1.score }) { risk in
                RiskRow(risk: risk)
            }
        }
    }
}

private struct RiskRow: View {
    let risk: RiskItem

    private var scoreColor: Color {
        switch risk.score {
        case 7...: return DesignTokens.Gate.failed
        case 4...: return DesignTokens.Gate.pending
        default:   return DesignTokens.Gate.passed
        }
    }

    var body: some View {
        HStack(spacing: 0) {
            Text(risk.label)
                .font(.system(size: 11))
                .foregroundStyle(DesignTokens.Foreground.secondary)
                .lineLimit(1)
                .frame(maxWidth: .infinity, alignment: .leading)
            Text("\(risk.likelihood)")
                .font(.system(size: 11, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
                .frame(width: 28, alignment: .center)
            Text("\(risk.impact)")
                .font(.system(size: 11, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
                .frame(width: 28, alignment: .center)
            Text("\(risk.score)")
                .font(.system(size: 11, weight: .semibold, design: .monospaced))
                .foregroundStyle(scoreColor)
                .frame(width: 40, alignment: .center)
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 5)
        .background(
            RoundedRectangle(cornerRadius: 5)
                .fill(scoreColor.opacity(0.06))
        )
    }
}

