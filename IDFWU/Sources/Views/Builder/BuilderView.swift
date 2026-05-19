import SwiftUI

// MARK: - Builder shell (3-pane IDE)

struct BuilderView: View {
    @Environment(ProviderRegistry.self) private var registry
    @Environment(BuilderOrchestrator.self) private var orchestrator
    @Environment(DaemonController.self) private var daemonController

    // Navigation & scene state
    @State private var activeView: BuilderTopView = .builder
    @State private var activeGate: DecisionGate.Full? = nil

    // Input
    @State private var inputText: String = ""

    // Overlay state
    @State private var showCommandK = false
    @State private var showSettings = false
    @State private var showGateModal = false

    @State private var didAttach = false

    private var messages: [TranscriptMessage] { orchestrator.chatMessages }

    var body: some View {
        ZStack {
            mainContent
                .frame(minWidth: 1100, minHeight: 700)

            if showCommandK {
                CommandKPalette(
                    isPresented: $showCommandK,
                    projects: orchestrator.activeProject.map { [$0] } ?? [],
                    onSelectProject: { _ in
                        activeView = .builder
                        showCommandK = false
                    },
                    onSelectSkill: { _ in showCommandK = false }
                )
                .zIndex(100)
                .transition(.opacity.combined(with: .scale(scale: 0.97, anchor: .top)))
            }

            if showGateModal, let gate = activeGate {
                GateModal(gate: gate) { showGateModal = false }
                    .zIndex(80)
                    .transition(.opacity)
            }
        }
        .background(DesignTokens.Background.base)
        .animation(.easeOut(duration: 0.16), value: showCommandK)
        .animation(.easeOut(duration: 0.16), value: showGateModal)
        .sheet(isPresented: $showSettings) {
            SettingsSheetView()
        }
        .task {
            if !didAttach {
                orchestrator.attach(registry: registry)
                await registry.refreshDetections()
                if let preferred = registry.defaultProvider {
                    orchestrator.selectedProvider = preferred
                }
                didAttach = true
            }
        }
        .background {
            Button("") { showCommandK.toggle() }
                .keyboardShortcut("k", modifiers: .command)
                .frame(width: 0, height: 0)
                .opacity(0)
        }
    }

    // MARK: - Scene routing — LeftNavigation always visible (title + settings always accessible)

    @ViewBuilder
    private var mainContent: some View {
        HStack(spacing: 0) {
            LeftNavigation(
                activeView: $activeView,
                activeProject: orchestrator.activeProject,
                projects: orchestrator.activeProject.map { [$0] } ?? [],
                onOpenSettings: { showSettings = true },
                onOpenCommandK: { showCommandK = true }
            )

            centerContent
        }
    }

    // MARK: - Center content (driven by activeView)

    @ViewBuilder
    private var centerContent: some View {
        if let project = orchestrator.activeProject {
            switch activeView {
            case .builder, .inspector:
                builderPane(project: project)

            case .browser:
                ProjectBrowserView(projects: [project]) { _ in activeView = .builder }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)

            case .graph:
                AgentGraphView(nodes: orchestrator.graphNodes, edges: orchestrator.graphEdges)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)

            case .hyperplot:
                HyperPlotTabView(axes: orchestrator.hyperPlotAxes)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        } else {
            HeroPromptView(
                inputText: $inputText,
                onSubmit: { idea in
                    orchestrator.processIdea(idea)
                    inputText = ""
                    activeView = .builder
                },
                onSkillTap: { _ in }
            )
        }
    }

    // MARK: - 3-pane builder layout

    @ViewBuilder
    private func builderPane(project: BuilderProject) -> some View {
        ChatPaneView(
            project: project,
            messages: messages,
            inputText: $inputText,
            onSend: { text in
                orchestrator.processIdea(text)
                inputText = ""
            },
            onGateExpand: { gate in
                activeGate = gate
                showGateModal = true
            },
            onPinGate: { gate in
                activeGate = gate
            }
        )
        .frame(maxWidth: .infinity)

        WorkspacePane(
            project: project,
            activeGate: activeGate
        )
    }

}

// MARK: - Settings sheet

struct SettingsSheetView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTab: SettingsTab = .providers

    enum SettingsTab: String, CaseIterable, Identifiable {
        case providers  = "Providers"
        case gates      = "Gates"
        case skills     = "Skills"
        case artifacts  = "Artifacts"
        case telemetry  = "Telemetry"
        case daemon     = "Daemon"
        case appearance = "Appearance"

        var id: String { rawValue }

        var symbol: String {
            switch self {
            case .providers:  return "cpu"
            case .gates:      return "diamond"
            case .skills:     return "bolt"
            case .artifacts:  return "doc.on.doc"
            case .telemetry:  return "chart.bar.doc.horizontal"
            case .daemon:     return "gearshape.2"
            case .appearance: return "paintpalette"
            }
        }
    }

    var body: some View {
        HStack(spacing: 0) {
            tabRail
                .frame(width: 160)

            Divider().background(DesignTokens.Hairline.soft)

            tabContent
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
                .background(DesignTokens.Background.base)
        }
        .frame(width: 640, height: 480)
        .background(DesignTokens.Background.base)
        .overlay(alignment: .topTrailing) {
            Button(action: { dismiss() }) {
                Image(systemName: "xmark")
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
                    .padding(8)
                    .background(Circle().fill(DesignTokens.Glass.thin))
            }
            .buttonStyle(.plain)
            .padding(12)
        }
    }

    // MARK: Tab rail

    private var tabRail: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(spacing: 8) {
                BrandMark(size: 22)
                Text("Settings")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(DesignTokens.Foreground.primary)
            }
            .padding(.horizontal, 12)
            .padding(.top, 16)
            .padding(.bottom, 10)

            Divider().background(DesignTokens.Hairline.soft)
                .padding(.bottom, 4)

            ForEach(SettingsTab.allCases) { tab in
                settingsTabButton(tab)
            }
            Spacer()
        }
        .background(DesignTokens.Background.sunken)
    }

    private func settingsTabButton(_ tab: SettingsTab) -> some View {
        let active = selectedTab == tab
        return Button(action: { selectedTab = tab }) {
            HStack(spacing: 8) {
                Image(systemName: tab.symbol)
                    .font(.system(size: 12, weight: active ? .semibold : .regular))
                    .frame(width: 16)
                Text(tab.rawValue)
                    .font(.system(size: 12, weight: active ? .semibold : .regular))
                Spacer(minLength: 0)
            }
            .foregroundStyle(active ? DesignTokens.Foreground.primary : DesignTokens.Foreground.secondary)
            .padding(.horizontal, 12)
            .padding(.vertical, 7)
            .background(
                RoundedRectangle(cornerRadius: 6)
                    .fill(active ? DesignTokens.Background.raised : Color.clear)
            )
        }
        .buttonStyle(.plain)
        .padding(.horizontal, 6)
    }

    // MARK: Tab content

    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case .providers:  ProvidersSettings()
        case .gates:      GatesSettings()
        case .skills:     SkillsSettings()
        case .artifacts:  ArtifactsSettings()
        case .telemetry:  TelemetrySettings()
        case .daemon:     DaemonSettings()
        case .appearance: AppearanceSettings()
        }
    }
}

// MARK: - Providers settings

private struct ProvidersSettings: View {
    private let providerInfo: [(AIProviderKind, String, String)] = [
        (.claude,  "claude",  "claude-sonnet-4-6"),
        (.codex,   "codex",   "codex-mini"),
        (.gemini,  "gemini",  "gemini-2.5-pro"),
        (.copilot, "gh copilot", "gpt-4o"),
    ]

    @State private var enabled: [AIProviderKind: Bool] = Dictionary(
        uniqueKeysWithValues: AIProviderKind.allCases.map { ($0, true) }
    )
    @State private var modelOverrides: [AIProviderKind: String] = [:]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                OverlineLabel(text: "AI Providers").padding(.bottom, 2)
                ForEach(providerInfo, id: \.0) { kind, cli, defaultModel in
                    ProviderSettingsRow(
                        kind: kind,
                        cliPath: cli,
                        defaultModel: defaultModel,
                        isEnabled: Binding(
                            get: { enabled[kind] ?? true },
                            set: { enabled[kind] = $0 }
                        ),
                        modelOverride: Binding(
                            get: { modelOverrides[kind] ?? "" },
                            set: { modelOverrides[kind] = $0 }
                        )
                    )
                }
            }
            .padding(20)
        }
    }
}

private struct ProviderSettingsRow: View {
    let kind: AIProviderKind
    let cliPath: String
    let defaultModel: String
    @Binding var isEnabled: Bool
    @Binding var modelOverride: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 10) {
                ProviderGlyph(kind: kind, size: 18)
                Text(kind.displayName)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                Spacer()
                Toggle("", isOn: $isEnabled).labelsHidden()
            }
            if isEnabled {
                settingsField(label: "CLI", value: cliPath)
                settingsFieldEditable(label: "Model", placeholder: defaultModel, text: $modelOverride)
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                .fill(DesignTokens.Background.surface)
                .overlay(
                    RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                        .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                )
        )
    }

    private func settingsField(label: String, value: String) -> some View {
        HStack(spacing: 8) {
            Text(label)
                .font(.system(size: 11))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
                .frame(width: 44, alignment: .trailing)
            Text(value)
                .font(.system(size: 11, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.secondary)
        }
    }

    private func settingsFieldEditable(label: String, placeholder: String, text: Binding<String>) -> some View {
        HStack(spacing: 8) {
            Text(label)
                .font(.system(size: 11))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
                .frame(width: 44, alignment: .trailing)
            TextField(placeholder, text: text)
                .font(.system(size: 11, design: .monospaced))
                .textFieldStyle(.plain)
                .foregroundStyle(DesignTokens.Foreground.primary)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(
                    RoundedRectangle(cornerRadius: 5)
                        .fill(DesignTokens.Background.sunken)
                        .overlay(
                            RoundedRectangle(cornerRadius: 5)
                                .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                        )
                )
        }
    }
}

// MARK: - Gates settings

private struct GatesSettings: View {
    @State private var requireAllCriteria = true
    @State private var allowWaive = true
    @State private var autoAdvanceOnPass = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                OverlineLabel(text: "Gate Behavior").padding(.bottom, 2)

                SettingsToggleRow(
                    label: "Require all criteria to pass",
                    sublabel: "Gate cannot be approved if any criterion is failing",
                    isOn: $requireAllCriteria
                )
                SettingsToggleRow(
                    label: "Allow waiving criteria",
                    sublabel: "Project leads can waive non-blocking criteria",
                    isOn: $allowWaive
                )
                SettingsToggleRow(
                    label: "Auto-advance on full pass",
                    sublabel: "Automatically move to next phase when all gates pass",
                    isOn: $autoAdvanceOnPass
                )

                OverlineLabel(text: "Gate Phases")
                    .padding(.top, 8).padding(.bottom, 2)

                ForEach(IDEAPhase.allCases, id: \.self) { phase in
                    HStack(spacing: 10) {
                        IDEAPhaseLetter(phase: phase, size: .sm, state: .active)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(phase.builderTitle)
                                .font(.system(size: 12, weight: .medium))
                                .foregroundStyle(DesignTokens.Foreground.primary)
                            Text("Gate \(phase.letter): \(phase.gateTagline)")
                                .font(.system(size: 10))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                        }
                        Spacer()
                        PhaseChip(phase: phase)
                    }
                    .padding(10)
                    .background(
                        RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                            .fill(DesignTokens.Background.surface)
                    )
                }
            }
            .padding(20)
        }
    }
}

// MARK: - Skills settings

private struct SkillsSettings: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    OverlineLabel(text: "Available Skills")
                    Spacer()
                    Text("\(SampleData.skills.count)")
                        .font(.system(size: 10))
                        .foregroundStyle(DesignTokens.Foreground.quaternary)
                }
                .padding(.bottom, 4)

                ForEach(SampleData.skills) { skill in
                    HStack(spacing: 10) {
                        IDEAPhaseLetter(phase: skill.phase, size: .sm, state: .active)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(skill.command)
                                .font(.system(size: 11, weight: .medium, design: .monospaced))
                                .foregroundStyle(DesignTokens.Foreground.primary)
                            Text(skill.description)
                                .font(.system(size: 10))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                                .lineLimit(1)
                        }
                        Spacer()
                        Text(skill.phase.builderTitle)
                            .font(.system(size: 9))
                            .foregroundStyle(skill.phase.color)
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                }
            }
            .padding(20)
        }
    }
}

// MARK: - Artifacts settings

private struct ArtifactsSettings: View {
    @State private var outputPath = "~/Developer/idfwu-artifacts"
    @State private var autoCommit = false
    @State private var openAfterWrite = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                OverlineLabel(text: "Output Settings").padding(.bottom, 2)
                settingsTextRow(label: "Output path", value: $outputPath, placeholder: "~/Developer/artifacts")
                SettingsToggleRow(
                    label: "Auto-commit artifacts",
                    sublabel: "Commit written files to git after each phase",
                    isOn: $autoCommit
                )
                SettingsToggleRow(
                    label: "Open in editor after write",
                    sublabel: "Reveal newly written files in the workspace pane",
                    isOn: $openAfterWrite
                )
            }
            .padding(20)
        }
    }

    private func settingsTextRow(label: String, value: Binding<String>, placeholder: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label)
                .font(.system(size: 11, weight: .medium))
                .foregroundStyle(DesignTokens.Foreground.secondary)
            TextField(placeholder, text: value)
                .font(.system(size: 11, design: .monospaced))
                .textFieldStyle(.plain)
                .foregroundStyle(DesignTokens.Foreground.primary)
                .padding(.horizontal, 10).padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .fill(DesignTokens.Background.sunken)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                        )
                )
        }
    }
}

// MARK: - Telemetry settings

private struct TelemetrySettings: View {
    @State private var apmURL = "http://localhost:3032"
    @State private var graphPhysics = true
    @State private var liveMetrics = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                OverlineLabel(text: "APM Connection").padding(.bottom, 2)
                VStack(alignment: .leading, spacing: 6) {
                    Text("APM server URL")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                    TextField("http://localhost:3032", text: $apmURL)
                        .font(.system(size: 11, design: .monospaced))
                        .textFieldStyle(.plain)
                        .foregroundStyle(DesignTokens.Foreground.primary)
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(
                            RoundedRectangle(cornerRadius: 6)
                                .fill(DesignTokens.Background.sunken)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 6)
                                        .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                                )
                        )
                }
                OverlineLabel(text: "Graph Options")
                    .padding(.top, 8).padding(.bottom, 2)
                SettingsToggleRow(
                    label: "Enable physics simulation",
                    sublabel: "Force-directed layout with charge repulsion and spring edges",
                    isOn: $graphPhysics
                )
                SettingsToggleRow(
                    label: "Live metrics stream",
                    sublabel: "Stream agent telemetry events in real time",
                    isOn: $liveMetrics
                )
            }
            .padding(20)
        }
    }
}

// MARK: - Daemon settings

private struct DaemonSettings: View {
    @State private var pythonPath = "~/.venv/idfw/bin/python"
    @State private var autoRestart = true
    @State private var logLevel = "info"
    private let logLevels = ["debug", "info", "warning", "error"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                OverlineLabel(text: "Daemon Process").padding(.bottom, 2)
                VStack(alignment: .leading, spacing: 6) {
                    Text("Python interpreter")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                    TextField("~/.venv/idfw/bin/python", text: $pythonPath)
                        .font(.system(size: 11, design: .monospaced))
                        .textFieldStyle(.plain)
                        .foregroundStyle(DesignTokens.Foreground.primary)
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(
                            RoundedRectangle(cornerRadius: 6)
                                .fill(DesignTokens.Background.sunken)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 6)
                                        .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                                )
                        )
                }
                SettingsToggleRow(
                    label: "Auto-restart on crash",
                    sublabel: "Daemon is automatically restarted if it exits unexpectedly",
                    isOn: $autoRestart
                )
                VStack(alignment: .leading, spacing: 6) {
                    Text("Log level")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                    Picker("", selection: $logLevel) {
                        ForEach(logLevels, id: \.self) { Text($0).tag($0) }
                    }
                    .labelsHidden()
                    .frame(width: 120)
                }
            }
            .padding(20)
        }
    }
}

// MARK: - Appearance settings

private struct AppearanceSettings: View {
    @State private var colorScheme = "auto"
    @State private var density = "comfortable"
    @State private var animationsEnabled = true
    private let schemes = ["auto", "light", "dark"]
    private let densities = ["compact", "comfortable", "spacious"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                OverlineLabel(text: "Theme").padding(.bottom, 2)
                VStack(alignment: .leading, spacing: 6) {
                    Text("Color scheme")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                    Picker("", selection: $colorScheme) {
                        ForEach(schemes, id: \.self) { Text($0.capitalized).tag($0) }
                    }
                    .labelsHidden().pickerStyle(.segmented).frame(maxWidth: 220)
                }
                VStack(alignment: .leading, spacing: 6) {
                    Text("UI density")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                    Picker("", selection: $density) {
                        ForEach(densities, id: \.self) { Text($0.capitalized).tag($0) }
                    }
                    .labelsHidden().pickerStyle(.segmented).frame(maxWidth: 280)
                }
                SettingsToggleRow(
                    label: "Enable animations",
                    sublabel: "Phase transitions, hover effects, and ambient glows",
                    isOn: $animationsEnabled
                )
                OverlineLabel(text: "Phase Colors")
                    .padding(.top, 8).padding(.bottom, 4)
                HStack(spacing: 10) {
                    ForEach(IDEAPhase.allCases, id: \.self) { phase in
                        VStack(spacing: 6) {
                            Circle()
                                .fill(phase.color)
                                .frame(width: 28, height: 28)
                                .shadow(color: phase.glowColor.opacity(0.4), radius: 8)
                            Text(phase.letter)
                                .font(.system(size: 10, weight: .semibold))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                        }
                    }
                }
            }
            .padding(20)
        }
    }
}

// MARK: - Settings toggle row (shared)

struct SettingsToggleRow: View {
    let label: String
    let sublabel: String
    @Binding var isOn: Bool

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            VStack(alignment: .leading, spacing: 2) {
                Text(label)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                Text(sublabel)
                    .font(.system(size: 10))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
            }
            Spacer()
            Toggle("", isOn: $isOn).labelsHidden()
        }
        .padding(10)
        .background(
            RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                .fill(DesignTokens.Background.surface)
        )
    }
}
