import SwiftUI

// MARK: - Workspace pane (460px right panel)

struct WorkspacePane: View {
    let project: BuilderProject
    var activeGate: DecisionGate.Full?
    @Environment(BuilderOrchestrator.self) private var orchestrator
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
            ArtifactTabView(markdownContent: orchestrator.artifactMarkdown.isEmpty
                ? "Submit an idea above to generate the discovery artifact."
                : orchestrator.artifactMarkdown)
        case .files:
            FilesTabView(tree: orchestrator.files)
        case .diagram:
            DiagramTabView(
                source: buildDiagramSource(),
                kind: .mermaid
            )
        case .plan:
            PlanTabView(milestones: orchestrator.milestones, risks: orchestrator.risks)
        case .constraints:
            ConstraintsTabView(constraints: orchestrator.constraints)
        case .actions:
            ActionsTabView(actions: orchestrator.actions)
        case .hyperplot:
            HyperPlotTabView(axes: orchestrator.hyperPlotAxes)
        case .telemetry:
            TelemetryTabView(
                nodes: orchestrator.graphNodes,
                edges: orchestrator.graphEdges,
                events: orchestrator.events
            )
        }
    }

    private func buildDiagramSource() -> String {
        guard !orchestrator.actions.isEmpty else {
            return "graph LR\n    A[Submit an idea to generate the action graph]"
        }
        var lines = ["graph LR"]
        for action in orchestrator.actions.prefix(12) {
            let safeId = action.artifactId.replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: ".", with: "_")
            for ref in action.inputRefs.prefix(3) {
                let safeRef = ref.replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: ".", with: "_")
                lines.append("    \(safeRef) --> \(safeId)")
            }
        }
        return lines.joined(separator: "\n")
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

// MARK: - Constraints tab (IDPC)

struct ConstraintsTabView: View {
    let constraints: [ConstraintItem]
    @State private var filter: FilterKind = .all

    enum FilterKind: String, CaseIterable { case all = "All", passing = "Passing", attention = "Attention", waived = "Waived" }

    private var filtered: [ConstraintItem] {
        switch filter {
        case .all:       return constraints
        case .passing:   return constraints.filter { $0.status == .passing }
        case .attention: return constraints.filter { $0.status == .violated || $0.status == .pending }
        case .waived:    return constraints.filter { $0.status == .waived }
        }
    }

    var body: some View {
        VStack(spacing: 0) {
            // Header
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("IDPC · Project Constraints")
                            .font(.system(size: 13, weight: .semibold))
                            .foregroundStyle(DesignTokens.Foreground.primary)
                        Text("Rules that govern what the agent can ship.")
                            .font(.system(size: 11))
                            .foregroundStyle(DesignTokens.Foreground.tertiary)
                    }
                    Spacer(minLength: 8)
                    SquareIconButton(symbol: "plus", action: {})
                }

                // Filter pills
                HStack(spacing: 6) {
                    ForEach(FilterKind.allCases, id: \.self) { kind in
                        filterPill(kind)
                    }
                }
            }
            .padding(14)
            .background(DesignTokens.Background.base)
            .overlay(alignment: .bottom) {
                Rectangle().fill(DesignTokens.Hairline.soft).frame(height: 0.5)
            }

            // List
            ScrollView {
                LazyVStack(spacing: 6) {
                    ForEach(filtered) { c in
                        ConstraintRow(item: c)
                    }
                    if filtered.isEmpty {
                        Text("Nothing here. Try a different filter.")
                            .font(.system(size: 12))
                            .foregroundStyle(DesignTokens.Foreground.tertiary)
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding(.top, 40)
                    }
                }
                .padding(12)
            }
        }
    }

    private func filterPill(_ kind: FilterKind) -> some View {
        let active = filter == kind
        let count: Int = {
            switch kind {
            case .all:       return constraints.count
            case .passing:   return constraints.filter { $0.status == .passing }.count
            case .attention: return constraints.filter { $0.status == .violated || $0.status == .pending }.count
            case .waived:    return constraints.filter { $0.status == .waived }.count
            }
        }()
        return Button(action: { filter = kind }) {
            HStack(spacing: 5) {
                if kind == .attention {
                    Circle().fill(DesignTokens.Gate.failed).frame(width: 5, height: 5)
                } else if kind == .passing {
                    Circle().fill(DesignTokens.Gate.passed).frame(width: 5, height: 5)
                } else if kind == .waived {
                    Circle().fill(DesignTokens.Gate.waived).frame(width: 5, height: 5)
                }
                Text(kind.rawValue)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(active ? DesignTokens.Foreground.primary : DesignTokens.Foreground.secondary)
                Text("\(count)")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundStyle(DesignTokens.Foreground.quaternary)
                    .padding(.horizontal, 5)
                    .background(Capsule().fill(DesignTokens.Glass.thin))
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill(active ? DesignTokens.Glass.thick : Color.clear)
                    .overlay(Capsule().strokeBorder(
                        active ? DesignTokens.Hairline.bold : Color.clear, lineWidth: 0.5))
            )
        }
        .buttonStyle(.plain)
    }
}

private struct ConstraintRow: View {
    let item: ConstraintItem
    @State private var expanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Button(action: { withAnimation(.spring(response: 0.28, dampingFraction: 0.88)) { expanded.toggle() } }) {
                HStack(spacing: 10) {
                    // Status icon
                    ZStack {
                        RoundedRectangle(cornerRadius: 7)
                            .fill(item.status.color.opacity(0.16))
                        Image(systemName: item.status.symbol)
                            .font(.system(size: 11))
                            .foregroundStyle(item.status.color)
                    }
                    .frame(width: 26, height: 26)

                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 6) {
                            Text(item.id)
                                .font(.system(size: 10, weight: .semibold, design: .monospaced))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                            Text(item.title)
                                .font(.system(size: 12, weight: .medium))
                                .foregroundStyle(DesignTokens.Foreground.primary)
                                .lineLimit(1)
                        }
                        HStack(spacing: 5) {
                            StatusPill(label: item.status.label, color: item.status.pillColor)
                            Text(item.severity.label)
                                .font(.system(size: 9, weight: .semibold))
                                .foregroundStyle(item.severity.color)
                                .padding(.horizontal, 5)
                                .padding(.vertical, 2)
                                .background(RoundedRectangle(cornerRadius: 4).fill(item.severity.color.opacity(0.12)))
                            Text(item.source)
                                .font(.system(size: 9, design: .monospaced))
                                .foregroundStyle(DesignTokens.Foreground.quaternary)
                                .lineLimit(1)
                            Spacer(minLength: 0)
                            ForEach(item.axisDelta.sorted { $0.key < $1.key }, id: \.key) { axis, delta in
                                AxisDeltaChip(axis: axis, delta: delta)
                            }
                        }
                    }

                    Image(systemName: expanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 10))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                }
                .padding(10)
            }
            .buttonStyle(.plain)

            if expanded {
                VStack(alignment: .leading, spacing: 8) {
                    Text(item.evidence)
                        .font(.system(size: 11))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                        .fixedSize(horizontal: false, vertical: true)

                    HStack(spacing: 6) {
                        if item.status == .violated {
                            PhaseButton(label: "Auto-fix", symbol: "wrench", phase: .definition, action: {})
                        }
                        if item.status == .pending {
                            PhaseButton(label: "Mark resolved", symbol: "checkmark", phase: .application, action: {})
                        }
                        Button("Waive") {}
                            .font(.system(size: 11))
                            .foregroundStyle(DesignTokens.Foreground.tertiary)
                        Spacer(minLength: 0)
                        Button("Source ↗") {}
                            .font(.system(size: 11))
                            .foregroundStyle(DesignTokens.Phase.definition)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.bottom, 10)
                .background(DesignTokens.Background.base)
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 9)
                .fill(DesignTokens.Background.raised)
                .overlay(
                    RoundedRectangle(cornerRadius: 9)
                        .strokeBorder(
                            item.status == .violated
                                ? DesignTokens.Gate.failed.opacity(0.28)
                                : DesignTokens.Hairline.soft,
                            lineWidth: 0.5)
                )
        )
    }
}

// MARK: - Axis delta chip

private struct AxisDeltaChip: View {
    let axis: String
    let delta: Double

    private var isPositive: Bool { delta > 0 }
    private var color: Color { isPositive ? DesignTokens.Phase.application : DesignTokens.Gate.failed }
    private var abbreviation: String { String(axis.prefix(4)) }

    var body: some View {
        HStack(spacing: 2) {
            Text(abbreviation)
            Text(isPositive ? "↑" : "↓")
            Text(String(format: "%.1f", abs(delta)))
        }
        .font(.system(size: 9, weight: .semibold, design: .monospaced))
        .foregroundStyle(color)
        .padding(.horizontal, 5)
        .padding(.vertical, 2)
        .background(RoundedRectangle(cornerRadius: 4).fill(color.opacity(0.12)))
    }
}

extension ConstraintItem.ConstraintStatus {
    var pillColor: StatusPill.PillColor {
        switch self {
        case .passing:  return .passed
        case .violated: return .failed
        case .pending:  return .pending
        case .waived:   return .waived
        }
    }
}

// MARK: - Actions tab (IDDA)

struct ActionsTabView: View {
    let actions: [ActionItem]

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text("IDDA · Project Actions")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                    Text("The pipeline. Each row is a generate / update / remove action.")
                        .font(.system(size: 11))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                }
                Spacer(minLength: 8)
                HStack(spacing: 6) {
                    StatusPill(label: "\(actions.filter { $0.status == .running }.count) running", color: .live)
                    StatusPill(label: "\(actions.filter { $0.status == .done }.count) done", color: .passed)
                    StatusPill(label: "\(actions.filter { $0.status == .queued }.count) queued")
                }
            }
            .padding(14)
            .background(DesignTokens.Background.base)
            .overlay(alignment: .bottom) {
                Rectangle().fill(DesignTokens.Hairline.soft).frame(height: 0.5)
            }

            // Pipeline list
            ScrollView {
                LazyVStack(spacing: 4) {
                    ForEach(Array(actions.enumerated()), id: \.element.id) { index, action in
                        ActionRow(action: action, stepNumber: index + 1)
                    }
                }
                .padding(10)
            }
        }
    }
}

private struct ActionRow: View {
    let action: ActionItem
    let stepNumber: Int

    @State private var showDetails = false

    private var statusColor: Color {
        switch action.status {
        case .done:    return DesignTokens.Gate.passed
        case .running: return DesignTokens.Gate.pending
        case .failed:  return DesignTokens.Gate.failed
        case .queued:  return DesignTokens.Foreground.tertiary
        }
    }

    private var statusSymbol: String {
        switch action.status {
        case .done:    return "checkmark.circle.fill"
        case .running: return "circle.fill"
        case .failed:  return "xmark.circle.fill"
        case .queued:  return "clock"
        }
    }

    private var isRunning: Bool { action.status == .running }

    var body: some View {
        HStack(spacing: 8) {
            // Step number
            Text("\(stepNumber)")
                .font(.system(size: 9, weight: .bold, design: .monospaced))
                .foregroundStyle(action.phase.color)
                .frame(width: 20, height: 20)
                .background(
                    RoundedRectangle(cornerRadius: 5)
                        .fill(action.phase.color.opacity(0.14))
                )

            // Kind chip
            HStack(spacing: 4) {
                Image(systemName: action.actionType.symbol)
                    .font(.system(size: 9))
                Text(action.actionType.rawValue)
                    .font(.system(size: 10, weight: .semibold))
            }
            .foregroundStyle(action.actionType.color)
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .background(
                Capsule().fill(action.actionType.color.opacity(0.12))
            )
            .fixedSize()

            // Status icon
            ZStack {
                RoundedRectangle(cornerRadius: 5)
                    .fill(statusColor.opacity(0.16))
                Image(systemName: statusSymbol)
                    .font(.system(size: 9))
                    .foregroundStyle(statusColor)
            }
            .frame(width: 20, height: 20)
            .overlay {
                if isRunning {
                    StatusDot(color: statusColor, live: true, size: 5)
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topTrailing)
                        .offset(x: 3, y: -3)
                }
            }

            // Artifact + inputs
            VStack(alignment: .leading, spacing: 2) {
                Text(action.artifactId)
                    .font(.system(size: 11, weight: .medium, design: .monospaced))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                    .lineLimit(1)
                if !action.inputRefs.isEmpty {
                    HStack(spacing: 3) {
                        Image(systemName: "arrow.right")
                            .font(.system(size: 8))
                            .foregroundStyle(DesignTokens.Foreground.quaternary)
                        Text(action.inputRefs.map { URL(fileURLWithPath: $0).lastPathComponent }.joined(separator: ", "))
                            .font(.system(size: 10))
                            .foregroundStyle(DesignTokens.Foreground.tertiary)
                            .lineLimit(1)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .layoutPriority(1)

            // Duration
            if let dur = action.duration {
                Text(String(format: "%.1fs", dur))
                    .font(.system(size: 9, design: .monospaced))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
            } else if action.status == .queued {
                Text("—")
                    .font(.system(size: 9, design: .monospaced))
                    .foregroundStyle(DesignTokens.Foreground.quaternary)
            }

            // Action button
            Group {
                switch action.status {
                case .queued:
                    Button("Run") {}
                        .font(.system(size: 10, weight: .medium))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(
                            RoundedRectangle(cornerRadius: 5)
                                .fill(DesignTokens.Glass.thin)
                                .overlay(RoundedRectangle(cornerRadius: 5).strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5))
                        )
                case .running:
                    HStack(spacing: 3) {
                        ForEach(0..<3, id: \.self) { _ in
                            Circle().fill(statusColor).frame(width: 3, height: 3)
                        }
                    }
                case .done:
                    SquareIconButton(symbol: "arrow.up.right.square", size: 22, action: {})
                case .failed:
                    Button("Retry") {}
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundStyle(DesignTokens.Gate.failed)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(
                            RoundedRectangle(cornerRadius: 5)
                                .fill(DesignTokens.Gate.failed.opacity(0.10))
                                .overlay(RoundedRectangle(cornerRadius: 5).strokeBorder(DesignTokens.Gate.failed.opacity(0.3), lineWidth: 0.5))
                        )
                }
            }
            .fixedSize()
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 7)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(isRunning
                      ? DesignTokens.Gate.pending.opacity(0.08)
                      : DesignTokens.Background.raised)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .strokeBorder(
                            isRunning
                                ? DesignTokens.Gate.pending.opacity(0.25)
                                : DesignTokens.Hairline.soft,
                            lineWidth: 0.5)
                )
        )
    }
}

