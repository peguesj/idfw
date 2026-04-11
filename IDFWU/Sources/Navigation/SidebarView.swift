import AppKit
import SwiftUI

struct SidebarView: View {
    @Environment(NavigationRouter.self) private var router
    @Environment(ProjectDiscoveryManager.self) private var discoveryManager
    @State private var favorites = FavoritesStore.shared
    @State private var searchText = ""
    @State private var revEngProjectID: String?
    @State private var isRevEngLoading = false
    @State private var ideaStatuses: [String: IDEAFrameworkStatus] = [:]
    private let ideaDetector = IDEAFrameworkDetector()

    private var filteredProjects: [DiscoveredProject] {
        if searchText.isEmpty { return discoveryManager.projects }
        return discoveryManager.projects.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }

    var body: some View {
        @Bindable var router = router

        VStack(spacing: 0) {
            List(selection: Binding(
                get: { router.selectedProjectID },
                set: { newValue in
                    if let id = newValue {
                        if let project = discoveryManager.projects.first(where: { $0.id == id }) {
                            router.selectProject(project)
                        } else {
                            router.selectProject(id)
                        }
                    }
                }
            )) {
                Section("Projects") {
                    ForEach(filteredProjects) { project in
                        VStack(alignment: .leading, spacing: 2) {
                            HStack(spacing: 4) {
                                Label(project.name, systemImage: iconForSource(project.source))
                                if favorites.isFavorite(project.id) {
                                    Image(systemName: "star.fill")
                                        .font(.caption2)
                                        .foregroundStyle(Color(red: 0.95, green: 0.77, blue: 0.20))
                                        .accessibilityLabel("Favorite")
                                }
                                Spacer(minLength: 0)
                                ideaStatusBadge(for: project.id)
                            }
                            HStack(spacing: 4) {
                                Text(project.source)
                                    .font(.caption2)
                                    .padding(.horizontal, 4)
                                    .padding(.vertical, 1)
                                    .background(.quaternary)
                                    .clipShape(RoundedRectangle(cornerRadius: 3))
                                if let desc = project.description {
                                    Text(desc)
                                        .font(.caption2)
                                        .foregroundStyle(.secondary)
                                        .lineLimit(1)
                                }
                            }
                        }
                        .tag(project.id)
                        .task(id: project.id) {
                            await detectIDEAStatus(for: project)
                        }
                        .contextMenu {
                            contextMenu(for: project)
                        }
                    }
                }
            }
            .searchable(text: $searchText, prompt: "Filter projects")
            .navigationTitle("Inception Glass")
            .overlay {
                if discoveryManager.isLoading && discoveryManager.projects.isEmpty {
                    ProgressView("Discovering projects...")
                        .font(.caption)
                }
            }

            Divider()

            HStack {
                EventStreamStatusBar()
                Spacer()
                if let date = discoveryManager.lastRefresh {
                    Text(date, style: .relative)
                        .font(.caption2)
                        .foregroundStyle(.quaternary)
                }
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
        }
        .task {
            await discoveryManager.refresh()
            discoveryManager.startAutoRefresh(interval: 30)
        }
    }

    private func iconForSource(_ source: String) -> String {
        switch source {
        case "daemon": "server.rack"
        case "filesystem": "folder.fill"
        default: "cube.fill"
        }
    }

    // MARK: - IDEA Framework status badge

    @ViewBuilder
    private func ideaStatusBadge(for projectID: String) -> some View {
        switch ideaStatuses[projectID] {
        case .initialized(let inventory):
            HStack(spacing: 2) {
                Image(systemName: "sparkles")
                    .font(.caption2)
                Text("IDEA")
                    .font(.caption2.weight(.medium))
                if inventory.documentCount + inventory.schemaCount + inventory.diagramCount > 0 {
                    Text("·\(inventory.documentCount + inventory.schemaCount + inventory.diagramCount)")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            .foregroundStyle(.tint)
            .padding(.horizontal, 4)
            .padding(.vertical, 1)
            .background(Color.accentColor.opacity(0.12))
            .clipShape(RoundedRectangle(cornerRadius: 3))
            .accessibilityLabel("IDEA framework initialized")
        case .uninitialized, .unknown, .none:
            EmptyView()
        }
    }

    private func detectIDEAStatus(for project: DiscoveredProject) async {
        guard let path = project.path, ideaStatuses[project.id] == nil else { return }
        let status = await ideaDetector.detect(projectPath: path)
        await MainActor.run {
            ideaStatuses[project.id] = status
        }
    }

    @MainActor
    private func sendRevEng(project: DiscoveredProject) async {
        guard !isRevEngLoading else { return }
        isRevEngLoading = true
        defer { isRevEngLoading = false }

        await RevEngClient.send(projectName: project.name, projectPath: project.path ?? "")
    }

    // MARK: - Context menu

    @ViewBuilder
    private func contextMenu(for project: DiscoveredProject) -> some View {
        // Finder / Terminal
        Button {
            if let path = project.path {
                ProjectRowContextActions.revealInFinder(path: path)
            }
        } label: {
            Label("Open in Finder", systemImage: "folder")
        }
        .disabled(project.path == nil)

        Button {
            if let path = project.path {
                ProjectRowContextActions.revealInTerminal(path: path)
            }
        } label: {
            Label("Reveal in Terminal", systemImage: "terminal")
        }
        .disabled(project.path == nil)

        Divider()

        // Rescan (preserves the prior "Reverse Engineer" side effect).
        Button {
            Task { await sendRevEng(project: project) }
        } label: {
            Label("Rescan", systemImage: "wand.and.stars")
        }

        Divider()

        // Remove from Scope / Copy Path / Open in IDFWU
        Button(role: .destructive) {
            removeFromScope(project: project)
        } label: {
            Label("Remove from Scope", systemImage: "minus.circle")
        }

        Button {
            if let path = project.path {
                ProjectRowContextActions.copyPath(path)
            }
        } label: {
            Label("Copy Path", systemImage: "doc.on.doc")
        }
        .disabled(project.path == nil)

        Button {
            ProjectRowContextActions.openInIDFWU(project)
        } label: {
            Label("Open in IDFWU", systemImage: "arrow.up.forward.app")
        }

        Divider()

        // Favorites toggle
        Button {
            favorites.toggle(project.id)
        } label: {
            if favorites.isFavorite(project.id) {
                Label("Remove from Favorites", systemImage: "star.fill")
            } else {
                Label("Add to Favorites", systemImage: "star")
            }
        }
    }

    @MainActor
    private func removeFromScope(project: DiscoveredProject) {
        let store = ScanRootStore.shared
        guard let projectPath = project.path else {
            presentNotAScanRootAlert()
            return
        }

        let normalizedProject = normalize(projectPath)
        let matchingRoot = store.roots.first { root in
            normalize(root.path) == normalizedProject
        }

        if let root = matchingRoot {
            store.remove(id: root.id)
        } else {
            presentNotAScanRootAlert()
        }
    }

    private func normalize(_ path: String) -> String {
        let expanded = (path as NSString).expandingTildeInPath
        let trimmed = expanded.hasSuffix("/") && expanded.count > 1
            ? String(expanded.dropLast())
            : expanded
        return trimmed
    }

    @MainActor
    private func presentNotAScanRootAlert() {
        let alert = NSAlert()
        alert.messageText = "Not a scan root"
        alert.informativeText = "This project was discovered inside a scan root but isn't itself one, so it cannot be removed from scope."
        alert.alertStyle = .warning
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }
}

#Preview {
    SidebarView()
        .environment(NavigationRouter())
        .environment(ProjectDiscoveryManager())
        .environment(\.eventStreamState, EventStreamState())
        .frame(width: 260, height: 500)
}
