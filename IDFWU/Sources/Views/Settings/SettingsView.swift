import SwiftUI
import AppKit
import UniformTypeIdentifiers

struct SettingsView: View {
    enum Tab: String, CaseIterable, Identifiable {
        case general = "General"
        case scanRoots = "Scan Roots"
        case markers = "Markers"
        case appearance = "Appearance"
        case scan = "Scan"
        case connectors = "Connectors"
        case advanced = "Advanced"
        var id: String { rawValue }
        var systemImage: String {
            switch self {
            case .general: "gearshape"
            case .scanRoots: "folder"
            case .markers: "doc.badge.gearshape"
            case .appearance: "paintbrush"
            case .scan: "arrow.clockwise"
            case .connectors: "link"
            case .advanced: "wrench.and.screwdriver"
            }
        }
    }

    @State private var selectedTab: Tab = .scanRoots

    var body: some View {
        TabView(selection: $selectedTab) {
            GeneralSettingsView()
                .tabItem { Label(Tab.general.rawValue, systemImage: Tab.general.systemImage) }
                .tag(Tab.general)

            ScanRootsSettingsView()
                .tabItem { Label(Tab.scanRoots.rawValue, systemImage: Tab.scanRoots.systemImage) }
                .tag(Tab.scanRoots)

            MarkersSettingsView()
                .tabItem { Label(Tab.markers.rawValue, systemImage: Tab.markers.systemImage) }
                .tag(Tab.markers)

            AppearanceSettingsView()
                .tabItem { Label(Tab.appearance.rawValue, systemImage: Tab.appearance.systemImage) }
                .tag(Tab.appearance)

            ScanSettingsView()
                .tabItem { Label(Tab.scan.rawValue, systemImage: Tab.scan.systemImage) }
                .tag(Tab.scan)

            ConnectorsSettingsView()
                .tabItem { Label(Tab.connectors.rawValue, systemImage: Tab.connectors.systemImage) }
                .tag(Tab.connectors)

            AdvancedSettingsView()
                .tabItem { Label(Tab.advanced.rawValue, systemImage: Tab.advanced.systemImage) }
                .tag(Tab.advanced)
        }
        .frame(minWidth: 720, minHeight: 520)
    }
}

// MARK: - General

private struct GeneralSettingsView: View {
    @Environment(ScanRootStore.self) private var store
    @Environment(ProjectDiscoveryManager.self) private var discovery

    var body: some View {
        Form {
            Section("Discovery") {
                Stepper(
                    "Max scan depth: \(store.maxDepth)",
                    value: Binding(
                        get: { store.maxDepth },
                        set: { store.setMaxDepth($0) }
                    ),
                    in: 1...5
                )
                .help("How many levels deep to recurse from each scan root.")

                HStack {
                    Text("Active provider")
                    Spacer()
                    Text(discovery.activeProviderName)
                        .foregroundStyle(.secondary)
                        .monospaced()
                }

                HStack {
                    Text("Last refresh")
                    Spacer()
                    Text(discovery.lastRefresh?.formatted(date: .omitted, time: .standard) ?? "never")
                        .foregroundStyle(.secondary)
                }

                Button {
                    Task { await discovery.refresh() }
                } label: {
                    Label("Refresh now", systemImage: "arrow.clockwise")
                }
                .disabled(discovery.isLoading)
            }
        }
        .formStyle(.grouped)
        .padding()
    }
}

// MARK: - Scan Roots

private struct ScanRootsSettingsView: View {
    @Environment(ScanRootStore.self) private var store
    @Environment(ProjectDiscoveryManager.self) private var discovery

    @State private var pendingDelete: ScanRoot?
    @State private var transferError: String?
    @State private var isTransferring: Bool = false

    private let transferHandler = ScopeTransferHandler()

    var body: some View {
        VStack(spacing: 0) {
            header

            List {
                ForEach(store.roots) { root in
                    EditableScanRootRow(
                        root: root,
                        onRequestDelete: { pendingDelete = $0 }
                    )
                }
                .onMove { indices, newOffset in
                    store.move(fromOffsets: indices, toOffsets: newOffset)
                    Task { await discovery.refresh() }
                }
            }
            .listStyle(.inset(alternatesRowBackgrounds: true))

            Divider()
            footer
        }
        .padding()
        .confirmationDialog(
            "Remove this scan root?",
            isPresented: Binding(
                get: { pendingDelete != nil },
                set: { if !$0 { pendingDelete = nil } }
            ),
            presenting: pendingDelete
        ) { root in
            Button("Remove \(root.label)", role: .destructive) {
                store.remove(id: root.id)
                pendingDelete = nil
                Task { await discovery.refresh() }
            }
            Button("Cancel", role: .cancel) { pendingDelete = nil }
        } message: { root in
            Text("This will stop scanning \(root.path). You can add it back later.")
        }
        .alert(
            "Scope Transfer",
            isPresented: Binding(
                get: { transferError != nil },
                set: { if !$0 { transferError = nil } }
            ),
            presenting: transferError
        ) { _ in
            Button("OK", role: .cancel) { transferError = nil }
        } message: { message in
            Text(message)
        }
    }

    private var header: some View {
        HStack {
            Text("Directories scanned for IDFW projects")
                .font(.headline)
            Spacer()
            Menu {
                ForEach(ScanRootStore.presets) { preset in
                    Button(preset.label) {
                        store.add(preset)
                        Task { await discovery.refresh() }
                    }
                }
            } label: {
                Label("Add Preset", systemImage: "star")
            }
            .menuStyle(.borderlessButton)
            .fixedSize()
        }
        .padding(.bottom, 8)
    }

    private var footer: some View {
        HStack(spacing: 8) {
            Button {
                chooseFolder()
            } label: {
                Label("Add Root", systemImage: "plus")
            }

            Button {
                runExport()
            } label: {
                Label("Export Scope…", systemImage: "square.and.arrow.up")
            }
            .disabled(isTransferring)

            Button {
                runImport()
            } label: {
                Label("Import Scope…", systemImage: "square.and.arrow.down")
            }
            .disabled(isTransferring)

            Spacer()

            Text("\(store.roots.filter(\.isEnabled).count) of \(store.roots.count) enabled")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(.top, 8)
    }

    private func chooseFolder() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = true
        panel.prompt = "Add"
        panel.message = "Select one or more directories to index"

        guard panel.runModal() == .OK else { return }
        for url in panel.urls {
            store.addRoot(url: url)
        }
        Task { await discovery.refresh() }
    }

    private func runExport() {
        isTransferring = true
        Task {
            defer { Task { @MainActor in isTransferring = false } }
            do {
                _ = try await transferHandler.export(from: store)
            } catch ScopeTransferHandler.TransferError.userCancelled {
                // silent cancel
            } catch {
                await MainActor.run {
                    transferError = error.localizedDescription
                }
            }
        }
    }

    private func runImport() {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.allowedContentTypes = [.json]
        panel.prompt = "Import"
        panel.title = "Import IDFWU Scope"

        guard panel.runModal() == .OK, let url = panel.url else { return }

        isTransferring = true
        Task {
            defer { Task { @MainActor in isTransferring = false } }
            do {
                try await transferHandler.import(into: store, url: url)
                await discovery.refresh()
            } catch ScopeTransferHandler.TransferError.userCancelled {
                // silent cancel
            } catch {
                await MainActor.run {
                    transferError = error.localizedDescription
                }
            }
        }
    }
}

// MARK: - Editable row

private struct EditableScanRootRow: View {
    @Environment(ScanRootStore.self) private var store

    let root: ScanRoot
    let onRequestDelete: (ScanRoot) -> Void

    @State private var labelDraft: String = ""
    @State private var didSeedDraft: Bool = false

    var body: some View {
        HStack(spacing: 10) {
            Toggle("", isOn: Binding(
                get: { root.isEnabled },
                set: { _ in store.toggleEnabled(id: root.id) }
            ))
            .labelsHidden()
            .toggleStyle(.switch)
            .controlSize(.mini)

            VStack(alignment: .leading, spacing: 4) {
                TextField("Label", text: $labelDraft)
                    .textFieldStyle(.plain)
                    .font(.body)
                    .onSubmit { commitLabel() }
                    .onChange(of: labelDraft) { _, _ in
                        // Debounced commit-on-change.
                        commitLabel()
                    }

                HStack(spacing: 4) {
                    Text(root.path)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                        .truncationMode(.middle)
                    Button("Change…") {
                        changePath()
                    }
                    .buttonStyle(.link)
                    .font(.caption)
                }
            }

            Spacer()

            // Per-root depth stepper. nil means "inherit global".
            HStack(spacing: 4) {
                Text(depthLabel)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .monospacedDigit()
                Stepper(
                    "",
                    value: Binding(
                        get: { root.maxDepth ?? store.maxDepth },
                        set: { store.setMaxDepth(id: root.id, depth: $0) }
                    ),
                    in: 1...5
                )
                .labelsHidden()
                .controlSize(.mini)
                if root.maxDepth != nil {
                    Button {
                        store.setMaxDepth(id: root.id, depth: nil)
                    } label: {
                        Image(systemName: "arrow.uturn.backward")
                    }
                    .buttonStyle(.borderless)
                    .help("Reset to global depth")
                }
            }

            Button {
                NSWorkspace.shared.open(URL(fileURLWithPath: root.path))
            } label: {
                Image(systemName: "arrow.up.forward.app")
            }
            .buttonStyle(.borderless)
            .help("Reveal in Finder")

            Button(role: .destructive) {
                onRequestDelete(root)
            } label: {
                Image(systemName: "trash")
            }
            .buttonStyle(.borderless)
            .help("Remove root")
        }
        .padding(.vertical, 4)
        .onAppear {
            if !didSeedDraft {
                labelDraft = root.label
                didSeedDraft = true
            }
        }
    }

    private var depthLabel: String {
        if let override = root.maxDepth {
            return "depth \(override)"
        } else {
            return "depth \(store.maxDepth)·auto"
        }
    }

    private func commitLabel() {
        let trimmed = labelDraft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, trimmed != root.label else { return }
        store.setLabel(id: root.id, label: trimmed)
    }

    private func changePath() {
        let panel = NSOpenPanel()
        panel.canChooseDirectories = true
        panel.canChooseFiles = false
        panel.allowsMultipleSelection = false
        panel.prompt = "Select"
        panel.title = "Change Scan Root Path"

        guard panel.runModal() == .OK, let url = panel.url else { return }
        store.setPath(id: root.id, path: url.path)
    }
}

// MARK: - Markers

private struct MarkersSettingsView: View {
    @Environment(ScanRootStore.self) private var store

    @State private var newMarker: String = ""
    @State private var selection: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("A directory is treated as a project if any of these marker files exist inside it.")
                .font(.callout)
                .foregroundStyle(.secondary)

            List(selection: $selection) {
                ForEach(store.markers, id: \.self) { marker in
                    HStack {
                        Image(systemName: "doc.text")
                            .foregroundStyle(.secondary)
                        Text(marker).monospaced()
                    }
                    .tag(marker)
                }
            }
            .frame(minHeight: 200)

            HStack(spacing: 8) {
                TextField("New marker (e.g. .project.json)", text: $newMarker)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit(addMarker)

                Button {
                    addMarker()
                } label: {
                    Label("Add", systemImage: "plus")
                }
                .disabled(newMarker.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                Button(role: .destructive) {
                    if let sel = selection {
                        store.removeMarker(sel)
                        selection = nil
                    }
                } label: {
                    Label("Remove", systemImage: "minus")
                }
                .disabled(selection == nil)

                Spacer()

                Button {
                    store.resetMarkers()
                } label: {
                    Label("Reset", systemImage: "arrow.uturn.backward")
                }
                .help("Restore default marker list.")
            }
        }
        .padding()
    }

    private func addMarker() {
        let trimmed = newMarker.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        store.addMarker(trimmed)
        newMarker = ""
    }
}

#Preview("Settings") {
    SettingsView()
        .environment(ScanRootStore.shared)
        .environment(ProjectDiscoveryManager())
}
