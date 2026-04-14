import SwiftUI

struct RootView: View {
    @Environment(NavigationRouter.self) private var router
    @Environment(ToastNotifier.self) private var toastNotifier

    var body: some View {
        @Bindable var router = router

        NavigationSplitView(columnVisibility: $router.columnVisibility) {
            SidebarView()
                .navigationSplitViewColumnWidth(min: 220, ideal: 260)
        } content: {
            DocumentListView(projectID: router.selectedProjectID)
                .navigationSplitViewColumnWidth(min: 300, ideal: 360)
        } detail: {
            DetailView(document: router.selectedDocument)
        }
        .frame(minWidth: 960, minHeight: 640)
        .progressToast(notifier: toastNotifier)
    }
}

// MARK: - Document List (IDEA phase-grouped)

struct DocumentListView: View {
    let projectID: String?

    @Environment(NavigationRouter.self) private var router
    @Environment(ProjectDiscoveryManager.self) private var discoveryManager
    @State private var documents: [ProjectDocument] = []
    @State private var isScanning = false
    @State private var isRevEngLoading = false
    @State private var ideaStatus: IDEAFrameworkStatus = .unknown
    @State private var expandedPhases: Set<IDEAPhase> = Set(IDEAPhase.allCases)
    private let ideaDetector = IDEAFrameworkDetector()

    private var selectedProject: DiscoveredProject? {
        guard let projectID else { return nil }
        return discoveryManager.projects.first { $0.id == projectID }
    }

    /// Documents grouped by IDEA phase, preserving phase order (I → D → E → A).
    private var groupedByPhase: [(IDEAPhase, [ProjectDocument])] {
        let grouped = Dictionary(grouping: documents, by: \.phase)
        return IDEAPhase.allCases.map { phase in
            let docs = (grouped[phase] ?? []).sorted { lhs, rhs in
                if lhs.type != rhs.type { return lhs.type.rawValue < rhs.type.rawValue }
                return lhs.name < rhs.name
            }
            return (phase, docs)
        }
    }

    var body: some View {
        @Bindable var router = router

        Group {
            if let project = selectedProject {
                List(selection: Binding(
                    get: { router.selectedDocumentID },
                    set: { newValue in
                        if let id = newValue,
                           let doc = documents.first(where: { $0.id == id }) {
                            router.selectDocument(doc)
                        }
                    }
                )) {
                    Section {
                        IDEAFrameworkStatusCard(status: ideaStatus, project: project) {
                            Task { await sendRevEng(project: project) }
                        }
                        .listRowInsets(EdgeInsets(top: 4, leading: 0, bottom: 8, trailing: 0))
                        .listRowBackground(Color.clear)
                    }

                    if isScanning {
                        HStack {
                            ProgressView()
                                .controlSize(.small)
                            Text("Scanning...")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    } else if documents.isEmpty {
                        Text("No IDFW documents found")
                            .foregroundStyle(.secondary)
                            .font(.callout)
                    } else {
                        ForEach(groupedByPhase, id: \.0) { phase, docs in
                            phaseSection(phase: phase, docs: docs)
                        }
                    }
                }
                .navigationTitle("IDEA Lifecycle")
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        Button {
                            Task { await sendRevEng(project: project) }
                        } label: {
                            if isRevEngLoading {
                                ProgressView()
                                    .controlSize(.small)
                            } else {
                                Label("Reverse Engineer", systemImage: "wand.and.stars")
                            }
                        }
                        .disabled(isRevEngLoading)
                        .help("Reverse engineer this project with /idea rev-eng")
                    }

                    ToolbarItem(placement: .automatic) {
                        Button {
                            Task { await scanProject(path: project.path) }
                        } label: {
                            Label("Refresh", systemImage: "arrow.clockwise")
                        }
                        .disabled(isScanning)
                    }
                }
                .task(id: projectID) {
                    await scanProject(path: project.path)
                    await detectIDEAStatus(path: project.path)
                }
            } else {
                EmptyStateView(
                    symbol: "doc.on.doc",
                    title: "No Project Selected",
                    subtitle: "Select a project from the sidebar to view its IDEA lifecycle."
                )
            }
        }
    }

    // MARK: - Phase section builder

    @ViewBuilder
    private func phaseSection(phase: IDEAPhase, docs: [ProjectDocument]) -> some View {
        Section {
            if expandedPhases.contains(phase) {
                if docs.isEmpty {
                    Text("No artifacts in this phase yet")
                        .font(.caption)
                        .foregroundStyle(.tertiary)
                        .italic()
                        .listRowBackground(Color.clear)
                } else {
                    ForEach(docs) { doc in
                        DocumentRow(document: doc)
                            .tag(doc.id)
                    }
                }
            }
        } header: {
            PhaseSectionHeader(
                phase: phase,
                count: docs.count,
                isExpanded: expandedPhases.contains(phase)
            ) {
                togglePhase(phase)
            }
        }
    }

    private func togglePhase(_ phase: IDEAPhase) {
        if expandedPhases.contains(phase) {
            expandedPhases.remove(phase)
        } else {
            expandedPhases.insert(phase)
        }
    }

    // MARK: - Data loading

    private func scanProject(path: String?) async {
        guard let path else {
            documents = []
            return
        }
        isScanning = true
        let scanner = ProjectDocumentScanner()
        let results = await scanner.scan(projectPath: path)
        documents = results
        isScanning = false
        // Clear document selection when switching projects
        router.selectedDocumentID = nil
        router.selectedDocument = nil
    }

    @MainActor
    private func sendRevEng(project: DiscoveredProject) async {
        guard !isRevEngLoading else { return }
        isRevEngLoading = true
        defer { isRevEngLoading = false }
        await RevEngClient.send(projectName: project.name, projectPath: project.path ?? "")
    }

    private func detectIDEAStatus(path: String?) async {
        guard let path else {
            ideaStatus = .unknown
            return
        }
        let status = await ideaDetector.detect(projectPath: path)
        await MainActor.run { ideaStatus = status }
    }
}

// MARK: - Phase Section Header

private struct PhaseSectionHeader: View {
    let phase: IDEAPhase
    let count: Int
    let isExpanded: Bool
    let onToggle: () -> Void

    var body: some View {
        Button(action: onToggle) {
            HStack(spacing: 8) {
                // Big letter badge
                ZStack {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(phase.accentColor.opacity(0.18))
                        .frame(width: 24, height: 24)
                    Text(phase.letter)
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundStyle(phase.accentColor)
                }

                VStack(alignment: .leading, spacing: 1) {
                    HStack(spacing: 4) {
                        Text(phase.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.primary)
                        Text("·")
                            .foregroundStyle(.tertiary)
                        Text("\(count)")
                            .font(.caption.weight(.medium))
                            .foregroundStyle(.secondary)
                    }
                    Text(phase.tagline)
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                }

                Spacer(minLength: 0)

                Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(.secondary)
            }
            .padding(.vertical, 4)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}

// MARK: - IDEA Framework Status Card

private struct IDEAFrameworkStatusCard: View {
    let status: IDEAFrameworkStatus
    let project: DiscoveredProject
    let onInitialize: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            switch status {
            case .initialized(let inventory):
                HStack(spacing: 6) {
                    Image(systemName: "sparkles")
                        .foregroundStyle(.tint)
                    Text("IDEA Framework Initialized")
                        .font(.subheadline.weight(.semibold))
                }
                inventoryRow(inventory)
            case .uninitialized:
                HStack(spacing: 6) {
                    Image(systemName: "circle.dashed")
                        .foregroundStyle(.secondary)
                    Text("Not IDEA-Initialized")
                        .font(.subheadline.weight(.semibold))
                    Spacer()
                    Button("Reverse Engineer") { onInitialize() }
                        .buttonStyle(.borderless)
                        .font(.caption)
                }
                Text("Run `/idea new` or reverse-engineer to bootstrap documents and diagrams.")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            case .unknown:
                HStack(spacing: 6) {
                    ProgressView().controlSize(.small)
                    Text("Detecting IDEA framework…")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(backgroundColor)
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    @ViewBuilder
    private func inventoryRow(_ inventory: IDEAFrameworkInventory) -> some View {
        HStack(spacing: 10) {
            if inventory.schemaCount > 0 {
                counterChip(symbol: "doc.badge.gearshape", count: inventory.schemaCount, label: "Schemas")
            }
            if inventory.documentCount > 0 {
                counterChip(symbol: "doc.text.fill", count: inventory.documentCount, label: "Docs")
            }
            if inventory.diagramCount > 0 {
                counterChip(symbol: "chart.bar.doc.horizontal", count: inventory.diagramCount, label: "Diagrams")
            }
            if inventory.forcePresent {
                counterChip(symbol: "shield.lefthalf.filled", count: nil, label: "FORCE")
            }
            Spacer()
        }
    }

    private func counterChip(symbol: String, count: Int?, label: String) -> some View {
        HStack(spacing: 3) {
            Image(systemName: symbol)
                .font(.caption2)
            if let count {
                Text("\(count)")
                    .font(.caption2.weight(.semibold))
            }
            Text(label)
                .font(.caption2)
        }
        .foregroundStyle(.secondary)
    }

    private var backgroundColor: Color {
        switch status {
        case .initialized: Color.accentColor.opacity(0.10)
        case .uninitialized: Color.gray.opacity(0.10)
        case .unknown: Color.gray.opacity(0.06)
        }
    }
}

// MARK: - Document Row

private struct DocumentRow: View {
    let document: ProjectDocument

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: iconForType(document.type))
                .font(.caption)
                .foregroundStyle(document.phase.accentColor)
                .frame(width: 14)
            VStack(alignment: .leading, spacing: 2) {
                Text(document.name)
                    .font(.callout)
                    .lineLimit(1)
                HStack(spacing: 6) {
                    Text(document.type.rawValue)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    Text("·")
                        .foregroundStyle(.tertiary)
                    Text(formattedSize(document.size))
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                    Text("·")
                        .foregroundStyle(.tertiary)
                    Text(document.modifiedDate, style: .relative)
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                }
            }
        }
        .padding(.vertical, 1)
    }

    private func iconForType(_ type: ProjectDocumentType) -> String {
        switch type {
        case .schema:  "doc.badge.gearshape"
        case .force:   "shield.lefthalf.filled"
        case .config:  "gearshape"
        case .doc:     "doc.text"
        case .diagram: "chart.bar.doc.horizontal"
        case .idea:    "sparkles"
        }
    }

    private func formattedSize(_ bytes: Int64) -> String {
        if bytes < 1024 { return "\(bytes) B" }
        if bytes < 1024 * 1024 { return "\(bytes / 1024) KB" }
        return String(format: "%.1f MB", Double(bytes) / 1_048_576)
    }
}

#Preview {
    RootView()
        .environment(NavigationRouter())
        .environment(ProjectDiscoveryManager())
        .environment(ToastNotifier())
        .environment(\.eventStreamState, EventStreamState())
}
