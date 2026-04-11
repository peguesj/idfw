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
                .navigationSplitViewColumnWidth(min: 280, ideal: 320)
        } detail: {
            DetailView(document: router.selectedDocument)
        }
        .frame(minWidth: 900, minHeight: 600)
        .progressToast(notifier: toastNotifier)
    }
}

// MARK: - Document List

struct DocumentListView: View {
    let projectID: String?

    @Environment(NavigationRouter.self) private var router
    @Environment(ProjectDiscoveryManager.self) private var discoveryManager
    @State private var documents: [ProjectDocument] = []
    @State private var isScanning = false
    @State private var isRevEngLoading = false
    @State private var ideaStatus: IDEAFrameworkStatus = .unknown
    private let ideaDetector = IDEAFrameworkDetector()

    private var selectedProject: DiscoveredProject? {
        guard let projectID else { return nil }
        return discoveryManager.projects.first { $0.id == projectID }
    }

    private var groupedDocuments: [(ProjectDocumentType, [ProjectDocument])] {
        let grouped = Dictionary(grouping: documents, by: \.type)
        return ProjectDocumentType.allCases.compactMap { type in
            guard let docs = grouped[type], !docs.isEmpty else { return nil }
            return (type, docs.sorted { $0.name < $1.name })
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
                        ForEach(groupedDocuments, id: \.0) { type, docs in
                            Section(type.rawValue) {
                                ForEach(docs) { doc in
                                    DocumentRow(document: doc)
                                        .tag(doc.id)
                                }
                            }
                        }
                    }
                }
                .navigationTitle("Documents")
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
                    subtitle: "Select a project from the sidebar to view its documents."
                )
            }
        }
    }

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
        VStack(alignment: .leading, spacing: 2) {
            Label(document.name, systemImage: iconForType(document.type))
                .lineLimit(1)
            HStack(spacing: 6) {
                Text(formattedSize(document.size))
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
                Text(document.modifiedDate, style: .relative)
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
        }
        .padding(.vertical, 1)
    }

    private func iconForType(_ type: ProjectDocumentType) -> String {
        switch type {
        case .schema: "doc.badge.gearshape"
        case .force: "shield.lefthalf.filled"
        case .config: "gearshape"
        case .doc: "doc.text"
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
