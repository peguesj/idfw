import Foundation
import Observation

/// Drives the Lovable/Replit-style "describe your idea → build it" loop, but
/// governed by the **IDFW/IDEA** lifecycle and **FORCE** conventions.
@MainActor
@Observable
final class BuilderOrchestrator {

    // MARK: Inputs
    var idea: String = ""
    var selectedProvider: ProviderID = .claude
    var selectedModel: String = "default"
    var workspaceURL: URL = BuilderOrchestrator.defaultWorkspace()

    // MARK: Lifecycle state
    private(set) var phase: IDEAPhase = .ideation
    private(set) var transcript: [ProviderEvent] = []
    private(set) var isRunning = false
    private(set) var gate: DecisionGate?

    // MARK: Live project (populated by processIdea)
    private(set) var activeProject: BuilderProject?
    private(set) var chatMessages: [TranscriptMessage] = []
    private(set) var constraints: [ConstraintItem] = []
    private(set) var actions: [ActionItem] = []
    private(set) var hyperPlotAxes: [HyperPlotAxis] = []
    private(set) var milestones: [Milestone] = []
    private(set) var risks: [RiskItem] = []
    private(set) var files: [FileEntry] = []
    private(set) var graphNodes: [GraphNode] = []
    private(set) var graphEdges: [GraphEdge] = []
    private(set) var events: [BuilderEvent] = []
    private(set) var artifactMarkdown: String = ""

    private var ideaTask: Task<Void, Never>?
    private(set) var completedPhases: Set<IDEAPhase> = []
    /// Artifact filenames the run reported writing, grouped by phase.
    private(set) var artifacts: [IDEAPhase: [String]] = [:]

    private var runTask: Task<Void, Never>?
    private weak var registry: ProviderRegistry?

    func attach(registry: ProviderRegistry) { self.registry = registry }

    // MARK: - Run control

    /// Start (or re-run) the current phase with the selected provider.
    func startPhase() {
        guard !idea.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            append(.error, "Describe your idea first.")
            return
        }
        guard let registry, let provider = registry.provider(selectedProvider),
              registry.detection(selectedProvider).available else {
            append(.error, "\(selectedProvider.displayName) is not installed. Pick an available provider.")
            return
        }

        ensureWorkspace()
        ProviderContext.stageMCP(into: workspaceURL)   // inherit shared MCP servers
        gate = nil
        isRunning = true
        let stage = IDEAPathway.stage(for: phase)
        append(.notice, "── \(stage.command) · \(stage.title) — \(stage.purpose) ──")

        let params = ProviderRunParams(
            runId: UUID(),
            cwd: workspaceURL,
            systemPrompt: ProviderContext.composeSystemContext(
                provider: selectedProvider, workspace: workspaceURL, stage: stage),
            userPrompt: idea,
            model: selectedModel
        )

        runTask = Task { [weak self] in
            guard let self else { return }
            do {
                for try await event in provider.run(params) {
                    if Task.isCancelled { break }
                    self.consume(event)
                }
            } catch {
                self.append(.error, error.localizedDescription)
            }
            self.finishRun()
        }
    }

    func stop() {
        runTask?.cancel()
        runTask = nil
        isRunning = false
        append(.notice, "Stopped by user.")
    }

    /// Resolve the current phase's gate and advance the lifecycle.
    func decide(_ decision: GateDecision) {
        guard var current = gate else { return }
        switch decision {
        case .approve:
            current.status = .passed
            gate = current
            completedPhases.insert(phase)
            append(.notice, "Gate passed: \(current.title)")
            advancePhase()
        case .waive:
            current.status = .waived
            gate = current
            completedPhases.insert(phase)
            append(.notice, "Gate waived: \(current.title)")
            advancePhase()
        case .requestChanges:
            current.status = .pending
            gate = nil
            append(.notice, "Changes requested — re-run \(phase.title) with a refined idea.")
        case .reject:
            current.status = .failed
            gate = current
            append(.error, "Gate rejected: \(current.title). Lifecycle halted at \(phase.title).")
        }
    }

    func reset() {
        runTask?.cancel()
        runTask = nil
        isRunning = false
        phase = .ideation
        transcript = []
        gate = nil
        completedPhases = []
        artifacts = [:]
    }

    // MARK: - Stream consumption

    private func consume(_ event: ProviderEvent) {
        transcript.append(event)
        if event.kind == .fileWrite {
            artifacts[phase, default: []].append(event.text)
        }
        if transcript.count > 1000 {
            transcript.removeFirst(transcript.count - 1000)
        }
    }

    private func finishRun() {
        isRunning = false
        runTask = nil
        // Surface the phase gate for human decision (IDFW governance).
        if gate == nil {
            gate = Self.gate(for: phase)
            append(.notice, "Reached \(phase.title) gate — review and decide to advance.")
        }
    }

    private func advancePhase() {
        let all = IDEAPhase.allCases
        guard let idx = all.firstIndex(of: phase) else { return }
        if idx + 1 < all.count {
            phase = all[idx + 1]
            gate = nil
            append(.notice, "→ Advanced to \(phase.letter) · \(phase.title). Run when ready.")
        } else {
            append(.done, "All IDEA phases complete. Your idea is realized in \(workspaceURL.path).")
        }
    }

    private func append(_ kind: ProviderEvent.Kind, _ text: String) {
        transcript.append(ProviderEvent(kind, text))
    }

    // MARK: - Workspace

    private func ensureWorkspace() {
        let fm = FileManager.default
        try? fm.createDirectory(at: workspaceURL, withIntermediateDirectories: true)
        // Defense-in-depth: provider CLIs are nested Claude Code/Codex sessions
        // whose SessionEnd hooks may resolve log paths relative to cwd. Pre-
        // create the dir tree so a cwd-relative hook can't FileNotFoundError
        // and abort the build (root cause also fixed in ~/.claude/hooks/idfwu).
        try? fm.createDirectory(
            at: workspaceURL.appendingPathComponent(".claude/hooks/logs"),
            withIntermediateDirectories: true)
    }

    private static func defaultWorkspace() -> URL {
        let stamp = ISO8601DateFormatter().string(from: Date())
            .replacingOccurrences(of: ":", with: "-")
        return FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Developer/idfwu-builds/build-\(stamp)")
    }

    // MARK: - IDFW/FORCE phase framing

    enum GateDecision { case approve, requestChanges, reject, waive }

    static func gate(for phase: IDEAPhase) -> DecisionGate {
        let stage = IDEAPathway.stage(for: phase)
        let nextTitle = IDEAPathway.next(after: phase)?.title ?? "completion"
        return DecisionGate(
            id: "gate-\(stage.id)",
            title: stage.gateTitle,
            criteria: stage.gateCriteria,
            status: .pending,
            options: ["Approve", "Request Changes", "Reject", "Waive"],
            description: "Approve to advance \(stage.command) → \(nextTitle).")
    }

    // MARK: - IdeaEngine-powered flow

    /// Entry point: analyze the idea via the Anthropic API, stream text to
    /// the chat transcript, and populate all workspace data from the
    /// structured scaffold_project tool result.
    func processIdea(_ idea: String) {
        ideaTask?.cancel()
        isRunning = true
        self.idea = idea

        // Immediately create a placeholder project so the 3-pane IDE appears without waiting for the spec.
        if activeProject == nil {
            activeProject = BuilderProject(
                id: UUID().uuidString,
                name: "Analyzing…",
                description: idea,
                phase: .ideation,
                provider: .claude,
                llmModel: "claude-sonnet-4-6",
                gateStatuses: [:],
                updatedAt: Date()
            )
        }

        // User message
        appendChat(.user(UserMessage(text: idea)))
        appendEvent(.phaseTransition, "Starting IDEA discovery analysis")

        // Thinking placeholder — replaced with streamed text
        let thinkingID = UUID()
        chatMessages.append(TranscriptMessage(
            id: thinkingID,
            kind: .agent(AgentMessage(text: "", providerKind: .claude, isThinking: true)),
            timestamp: Date()
        ))

        ideaTask = Task { @MainActor [weak self] in
            guard let self else { return }
            var agentText = ""
            do {
                for try await event in IdeaEngine.analyze(idea: idea) {
                    guard !Task.isCancelled else { break }
                    switch event {
                    case .textToken(let token):
                        agentText += token
                        self.updateThinkingBubble(id: thinkingID, text: agentText)
                    case .projectSpec(let spec):
                        self.applySpec(spec)
                        self.appendEvent(.phaseTransition, "Discovery complete — scaffold ready")
                        self.appendChat(.phaseTransition(PhaseTransition(
                            from: nil, to: .ideation,
                            label: "I · Discover — Analysis complete")))
                    case .error(let msg):
                        self.appendChat(.system(SystemMessage(text: "Error: \(msg)")))
                        self.isRunning = false
                    case .done:
                        self.isRunning = false
                    }
                }
            } catch {
                self.appendChat(.system(SystemMessage(text: "Engine error: \(error.localizedDescription)")))
                self.isRunning = false
            }
        }
    }

    func resetProject() {
        ideaTask?.cancel()
        ideaTask = nil
        isRunning = false
        activeProject = nil
        chatMessages = []
        constraints = []
        actions = []
        hyperPlotAxes = []
        milestones = []
        risks = []
        files = []
        graphNodes = []
        graphEdges = []
        events = []
        artifactMarkdown = ""
        phase = .ideation
    }

    // MARK: - Private helpers

    private func updateThinkingBubble(id: UUID, text: String) {
        guard let idx = chatMessages.firstIndex(where: { $0.id == id }) else { return }
        chatMessages[idx] = TranscriptMessage(
            id: id,
            kind: .agent(AgentMessage(text: text, providerKind: .claude, isThinking: false)),
            timestamp: chatMessages[idx].timestamp
        )
    }

    private func applySpec(_ spec: IdeaProjectSpec) {
        let projectID = UUID().uuidString
        activeProject = BuilderProject(
            id: projectID,
            name: spec.project.name,
            description: spec.project.description,
            phase: spec.project.phase,
            provider: spec.project.provider,
            llmModel: spec.project.model,
            gateStatuses: [:],
            updatedAt: Date()
        )
        artifactMarkdown = spec.artifactMarkdown
        constraints = spec.constraints
        actions = spec.actions
        hyperPlotAxes = spec.hyperplotAxes
        milestones = spec.milestones
        risks = spec.risks
        files = spec.files
        graphNodes = buildGraphNodes(from: spec.actions)
        graphEdges = buildGraphEdges(from: spec.actions)
        events = buildEvents(from: spec)
    }

    private func appendChat(_ kind: TranscriptMessage.MessageKind) {
        chatMessages.append(TranscriptMessage(id: UUID(), kind: kind, timestamp: Date()))
    }

    private func appendEvent(_ kind: BuilderEvent.EventKind, _ label: String) {
        events.append(BuilderEvent(
            id: UUID(), timestamp: Date().timeIntervalSince1970,
            kind: kind, label: label, phase: phase, actor: "IdeaEngine"))
    }

    private func buildGraphNodes(from actions: [ActionItem]) -> [GraphNode] {
        actions.map { a in
            GraphNode(
                id: a.id,
                label: a.artifactId,
                kind: .skill,
                phase: a.phase,
                status: a.status == .done ? .done : a.status == .running ? .running : .pending,
                x: Double.random(in: 100...800),
                y: Double.random(in: 80...500)
            )
        }
    }

    private func buildGraphEdges(from actions: [ActionItem]) -> [GraphEdge] {
        var edges: [GraphEdge] = []
        for action in actions {
            for ref in action.inputRefs {
                if actions.contains(where: { $0.artifactId == ref || $0.id == ref }) {
                    edges.append(GraphEdge(
                        id: "\(ref)->\(action.id)",
                        sourceID: ref,
                        targetID: action.id
                    ))
                }
            }
        }
        return edges
    }

    private func buildEvents(from spec: IdeaProjectSpec) -> [BuilderEvent] {
        var evts: [BuilderEvent] = []
        var t = Date().timeIntervalSince1970 - 30
        evts.append(BuilderEvent(id: UUID(), timestamp: t, kind: .phaseTransition,
                                 label: "Discovery started", phase: .ideation, actor: "IdeaEngine"))
        t += 8
        for constraint in spec.constraints.prefix(3) {
            evts.append(BuilderEvent(id: UUID(), timestamp: t, kind: .gate,
                                     label: constraint.title, phase: .ideation, actor: "IDPC"))
            t += 2
        }
        for action in spec.actions.prefix(4) {
            evts.append(BuilderEvent(id: UUID(), timestamp: t, kind: .tool,
                                     label: "Generate \(action.artifactId)", phase: action.phase,
                                     actor: "IDDA", durationMs: action.duration.map { Int($0 * 1000) }))
            t += 1.5
        }
        evts.append(BuilderEvent(id: UUID(), timestamp: t, kind: .phaseTransition,
                                 label: "Discovery complete", phase: .ideation, actor: "IdeaEngine"))
        return evts
    }
}
