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

    enum GateDecision { case approve, requestChanges, reject, waive }

    /// Gate for a phase boundary, derived from the canonical `/idea`
    /// pathway (`IDEAPathway`) so the guided flow matches the real
    /// determined sequence and its pass criteria.
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
}
