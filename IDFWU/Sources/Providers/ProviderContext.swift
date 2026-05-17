import Foundation

/// Resolves and hands off "inherited" AI context to a provider CLI before a
/// run — the open-design pattern adapted to IDFWU.
///
/// Spawning the real `claude`/`codex`/`gemini` binary already inherits that
/// provider's own home context (config dir, skills, auth). This type adds
/// the *cross-context* layer open-design performs: detecting that context
/// for UI transparency, composing a layered system preamble (IDFW/FORCE
/// contract + workspace + active skill + phase), and staging `.mcp.json`
/// into the workspace so the CLI auto-loads shared MCP servers.
enum ProviderContext {

    /// Where each provider keeps its own config/skills (for the "inherited
    /// context" status surfaced in the UI).
    static func configDir(for id: ProviderID) -> URL? {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let sub: String
        switch id {
        case .claude:    sub = ".claude"
        case .codex:     sub = ".codex"
        case .gemini:    sub = ".gemini"
        case .ghCopilot: sub = ".config/gh"
        }
        let url = home.appendingPathComponent(sub)
        return FileManager.default.fileExists(atPath: url.path) ? url : nil
    }

    static func skillsDir(for id: ProviderID) -> URL? {
        guard id == .claude else { return nil }
        let url = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".claude/skills")
        return FileManager.default.fileExists(atPath: url.path) ? url : nil
    }

    /// One-line summary of what the spawned CLI will inherit (UI display).
    static func inheritedSummary(for id: ProviderID) -> String {
        var parts: [String] = []
        if let cfg = configDir(for: id) { parts.append("config: \(cfg.lastPathComponent)") }
        if skillsDir(for: id) != nil { parts.append("skills: ~/.claude/skills") }
        if FileManager.default.fileExists(atPath: sharedMCPConfig().path) { parts.append("MCP: shared") }
        return parts.isEmpty ? "no inherited context detected" : parts.joined(separator: " · ")
    }

    /// Shared MCP config IDFWU stages into the workspace so a Claude run
    /// auto-loads the same MCP servers. Users place it here.
    static func sharedMCPConfig() -> URL {
        FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".idfwu/mcp.json")
    }

    /// Copy the shared MCP config into the workspace as `.mcp.json` so the
    /// CLI inherits MCP servers (Claude Code reads `<cwd>/.mcp.json`).
    static func stageMCP(into workspace: URL) {
        let shared = sharedMCPConfig()
        guard FileManager.default.fileExists(atPath: shared.path) else { return }
        let dest = workspace.appendingPathComponent(".mcp.json")
        try? FileManager.default.createDirectory(at: workspace, withIntermediateDirectories: true)
        try? FileManager.default.removeItem(at: dest)
        try? FileManager.default.copyItem(at: shared, to: dest)
    }

    /// Layered system preamble (open-design composition order:
    /// framework-contract → workspace-context → inherited-context →
    /// phase-instruction). Prepended to the user's idea.
    static func composeSystemContext(
        provider: ProviderID,
        workspace: URL,
        stage: IDEAPathway.Stage
    ) -> String {
        let inherited = inheritedSummary(for: provider)
        return """
        # IDFWU BUILD ENGINE — \(provider.displayName)

        You are the build engine inside IDFWU, an IDE that turns ideas into \
        reality under the IDFW/IDEA framework with FORCE governance. You do \
        NOT free-build: you advance a determined `/idea` pathway one gated \
        phase at a time.

        ## Workspace
        Produce concrete files under: \(workspace.path)
        Inherited context (\(provider.displayName)): \(inherited)
        If a `.mcp.json` exists in the workspace, its MCP servers are available to you.

        ## FORCE
        Structure work so it could be driven by YUNG subagents \
        ($CODE/$TEST/$INFRA/$DOC/$VCS). Governance, audit and quality gates apply.

        ## Current phase — \(stage.command)  ·  \(stage.title)
        Purpose: \(stage.purpose)
        Do, in order:
        \(stage.subSteps.enumerated().map { "  \($0.offset + 1). \($0.element)" }.joined(separator: "\n"))
        Produce these artifacts (use IDEA schema infixes): \
        \(stage.artifacts.joined(separator: ", ")).
        Do NOT proceed past this phase — it gates on: \(stage.gateCriteria)
        End with a one-line summary of what you produced.
        """
    }
}
