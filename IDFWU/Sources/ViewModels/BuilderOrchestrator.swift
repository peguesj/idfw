import Foundation
import Observation

/// Drives the Lovable/Replit-style "describe your idea → build it" loop, but
/// governed by the **IDFW/IDEA** lifecycle and **FORCE** conventions.
///
/// The provider CLI does the generative work; the orchestrator owns
/// *progression*: it frames the user's idea per `IDEAPhase`, runs the
/// selected provider, then blocks at a `DecisionGate` until the human
/// approves before advancing I → D → E → A.
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
        gate = nil
        isRunning = true
        append(.notice, "── \(phase.letter) · \(phase.title) — \(phase.tagline) ──")

        let params = ProviderRunParams(
            runId: UUID(),
            cwd: workspaceURL,
            systemPrompt: systemPrompt(for: phase),
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
        try? FileManager.default.createDirectory(
            at: workspaceURL, withIntermediateDirectories: true)
    }

    private static func defaultWorkspace() -> URL {
        let stamp = ISO8601DateFormatter().string(from: Date())
            .replacingOccurrences(of: ":", with: "-")
        return FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Developer/idfwu-builds/build-\(stamp)")
    }

    // MARK: - IDFW/FORCE phase framing

    /// Per-phase system prompt. This is where IDFWU asserts "more technicality
    /// and respect to IDFW and FORCE" — it constrains the provider to the
    /// phase's purpose, the IDEA schema artifacts it must emit, and FORCE
    /// governance, instead of letting it free-build.
    private func systemPrompt(for phase: IDEAPhase) -> String {
        let common = """
        You are the build engine inside IDFWU, an IDE that turns ideas into \
        reality under the IDFW/IDEA framework with FORCE governance. Work ONLY \
        within the current lifecycle phase. Produce concrete files in the \
        working directory. Name framework artifacts with IDEA schema infixes \
        (e.g. `*.idfw.json`, `*.iddv.json`, `*.iddg.json`, `*.iddc.json`, \
        `*.idda.json`, `*.ddd.md`, `*.idpc.json`, `*.idpg.json`, \
        `*.idfpj.json`). Respect FORCE: structure work so it could be driven \
        by YUNG subagents ($CODE/$TEST/$INFRA/$DOC/$VCS). Be technical and \
        precise. End with a one-line summary of what you produced.
        """
        let phaseSpecific: String
        switch phase {
        case .ideation:
            phaseSpecific = """
            PHASE I — IDEATION. Capture the concept. Produce an `idea.idfw.json` \
            framework seed: problem statement, target user, value, scope, key \
            constraints, and success criteria. Do NOT implement yet. This gates \
            on clarity, scope, and feasibility.
            """
        case .definition:
            phaseSpecific = """
            PHASE D — DEFINITION. From the approved idea, design the solution. \
            Emit IDEA definition artifacts: variables (`*.iddv.json`), diagrams \
            (`*.iddg` mermaid), contracts (`*.iddc.json`), actions \
            (`*.idda.json`), and a `domain.ddd.md`. Scaffold the project \
            structure. This gates on architectural soundness and contract \
            completeness.
            """
        case .evaluation:
            phaseSpecific = """
            PHASE E — EVALUATION. Validate the definition. Produce constraint \
            and governance artifacts (`*.idpc.json`, `*.idpg.json`), write \
            tests, and run a self-review for security, performance, and \
            compliance. Report risks. This gates on quality and risk \
            mitigation.
            """
        case .application:
            phaseSpecific = """
            PHASE A — APPLICATION. Carry the definition into a working build. \
            Implement the core, wire deployment/runtime config, produce an \
            `*.idfpj.json` project journey. Make it runnable. This gates on \
            deployment readiness.
            """
        }
        return common + "\n\n" + phaseSpecific
    }

    enum GateDecision { case approve, requestChanges, reject, waive }

    /// Canonical gate for each phase boundary (criteria from the IDFW
    /// methodology).
    static func gate(for phase: IDEAPhase) -> DecisionGate {
        switch phase {
        case .ideation:
            return DecisionGate(
                id: "gate-ideation", title: "Ideation Gate",
                criteria: "Problem is clear, scope is bounded, and the concept is feasible.",
                status: .pending,
                options: ["Approve", "Request Changes", "Reject", "Waive"],
                description: "Advance to Definition once the idea is well-formed.")
        case .definition:
            return DecisionGate(
                id: "gate-definition", title: "Definition Gate",
                criteria: "Architecture is sound, contracts complete, dependencies resolved.",
                status: .pending,
                options: ["Approve", "Request Changes", "Reject", "Waive"],
                description: "Advance to Evaluation once the design holds together.")
        case .evaluation:
            return DecisionGate(
                id: "gate-evaluation", title: "Evaluation Gate",
                criteria: "Security, performance, and compliance risks are mitigated.",
                status: .pending,
                options: ["Approve", "Request Changes", "Reject", "Waive"],
                description: "Advance to Application once the design is validated.")
        case .application:
            return DecisionGate(
                id: "gate-application", title: "Deployment Readiness Gate",
                criteria: "Build runs, runtime/deploy config present, journey documented.",
                status: .pending,
                options: ["Approve", "Request Changes", "Reject", "Waive"],
                description: "Approve to mark the idea realized.")
        }
    }
}
