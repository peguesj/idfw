import SwiftUI

/// The IDFWU "Builder" — a Lovable/Replit-style "describe your idea → build
/// it" surface, but technical and governed by the IDFW/IDEA lifecycle with
/// FORCE conventions. The hero prompt feeds a provider CLI; progression is
/// gated phase-by-phase (I → D → E → A).
struct BuilderView: View {
    @Environment(ProviderRegistry.self) private var registry
    @Environment(BuilderOrchestrator.self) private var orchestrator
    @State private var didAttach = false

    var body: some View {
        @Bindable var orchestrator = orchestrator

        VStack(spacing: 0) {
            IDEALifecycleStepper(
                currentPhase: orchestrator.phase,
                completedPhases: orchestrator.completedPhases
            )
            Divider()

            ProviderPickerBar(orchestrator: orchestrator)
            Divider()

            HSplitView {
                VStack(alignment: .leading, spacing: 10) {
                    heroPrompt(orchestrator)
                    workspaceRow(orchestrator)
                }
                .padding(16)
                .frame(minWidth: 360, idealWidth: 440)

                VStack(spacing: 0) {
                    if orchestrator.transcript.isEmpty {
                        EmptyStateView(
                            symbol: "wand.and.stars",
                            title: "Describe your idea",
                            subtitle: "IDFWU will walk it through Idea → Development → Evaluation → Application, gating each phase."
                        )
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        BuilderTranscriptView(events: orchestrator.transcript)
                    }

                    if let gate = orchestrator.gate {
                        Divider()
                        GateApprovalCard(
                            gate: gate,
                            phase: orchestrator.phase
                        ) { decision in
                            orchestrator.decide(decision)
                        }
                        .padding(12)
                    }
                }
                .frame(minWidth: 420)
            }
        }
        .frame(minWidth: 900, minHeight: 600)
        .navigationTitle("IDFWU Builder")
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
    }

    // MARK: - Hero prompt

    @ViewBuilder
    private func heroPrompt(_ orchestrator: BuilderOrchestrator) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("What do you want to build?")
                .font(.system(.title2, design: .rounded).weight(.semibold))
            Text("Phase \(orchestrator.phase.letter) · \(orchestrator.phase.title) — \(orchestrator.phase.tagline)")
                .font(.caption)
                .foregroundStyle(orchestrator.phase.accentColor)

            TextEditor(text: Binding(
                get: { orchestrator.idea },
                set: { orchestrator.idea = $0 }
            ))
            .font(.body)
            .frame(minHeight: 160)
            .padding(6)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .strokeBorder(
                        orchestrator.idea.isEmpty ? Color.secondary.opacity(0.3)
                        : orchestrator.phase.accentColor.opacity(0.5),
                        lineWidth: 1)
            )

            HStack {
                if orchestrator.isRunning {
                    Button(role: .destructive) {
                        orchestrator.stop()
                    } label: {
                        Label("Stop", systemImage: "stop.fill")
                    }
                } else {
                    Button {
                        orchestrator.startPhase()
                    } label: {
                        Label("Build · \(orchestrator.phase.title)",
                              systemImage: "sparkles")
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(orchestrator.phase.accentColor)
                    .disabled(orchestrator.idea.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                    .keyboardShortcut(.return, modifiers: .command)
                }

                Spacer()

                if orchestrator.isRunning {
                    ProgressView().controlSize(.small)
                }

                Button {
                    orchestrator.reset()
                } label: {
                    Label("Reset", systemImage: "arrow.counterclockwise")
                }
                .buttonStyle(.borderless)
                .disabled(orchestrator.isRunning)
            }
        }
    }

    @ViewBuilder
    private func workspaceRow(_ orchestrator: BuilderOrchestrator) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Label("Workspace", systemImage: "folder")
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
            HStack(spacing: 6) {
                Text(orchestrator.workspaceURL.path)
                    .font(.caption.monospaced())
                    .foregroundStyle(.tertiary)
                    .lineLimit(1)
                    .truncationMode(.middle)
                Button {
                    NSWorkspace.shared.activateFileViewerSelecting([orchestrator.workspaceURL])
                } label: {
                    Image(systemName: "arrow.up.forward.app")
                }
                .buttonStyle(.borderless)
                .help("Reveal workspace in Finder")
            }

            if !orchestrator.artifacts.isEmpty {
                Divider().padding(.vertical, 4)
                Label("Artifacts", systemImage: "doc.on.doc")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                ForEach(IDEAPhase.allCases, id: \.self) { phase in
                    if let files = orchestrator.artifacts[phase], !files.isEmpty {
                        ForEach(files, id: \.self) { file in
                            HStack(spacing: 4) {
                                Image(systemName: "circle.fill")
                                    .font(.system(size: 5))
                                    .foregroundStyle(phase.accentColor)
                                Text(file)
                                    .font(.caption2.monospaced())
                                    .lineLimit(1)
                                    .truncationMode(.middle)
                            }
                        }
                    }
                }
            }
            Spacer()
        }
    }
}
