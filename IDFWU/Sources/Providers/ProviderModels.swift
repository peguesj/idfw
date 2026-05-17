import Foundation

/// The AI provider CLIs IDFWU can drive. Each maps to a system-installed
/// command-line tool that runs an agentic build loop. IDFWU does not embed
/// model intelligence — it *orchestrates* these CLIs and governs their output
/// through the IDFW/FORCE lifecycle (see `BuilderOrchestrator`).
enum ProviderID: String, CaseIterable, Sendable, Codable, Identifiable {
    case claude          // Anthropic Claude Code  — `claude`
    case codex           // OpenAI Codex CLI       — `codex`
    case gemini          // Google Gemini CLI      — `gemini`
    case ghCopilot       // GitHub Copilot CLI     — `gh copilot`

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .claude:    return "Claude Code"
        case .codex:     return "Codex CLI"
        case .gemini:    return "Gemini CLI"
        case .ghCopilot: return "GitHub Copilot"
        }
    }

    /// Primary executable name resolved on `PATH`.
    var binaryName: String {
        switch self {
        case .claude:    return "claude"
        case .codex:     return "codex"
        case .gemini:    return "gemini"
        case .ghCopilot: return "gh"
        }
    }

    /// Alternate binaries tried if the primary is absent.
    var fallbackBinaries: [String] {
        switch self {
        case .claude: return ["openclaude"]
        default:      return []
        }
    }

    /// Environment variable that overrides binary resolution (mirrors
    /// open-design's `{ID}_BIN` convention).
    var binaryOverrideEnvKey: String {
        switch self {
        case .claude:    return "CLAUDE_BIN"
        case .codex:     return "CODEX_BIN"
        case .gemini:    return "GEMINI_BIN"
        case .ghCopilot: return "GH_BIN"
        }
    }

    var symbol: String {
        switch self {
        case .claude:    return "sparkle"
        case .codex:     return "chevron.left.forwardslash.chevron.right"
        case .gemini:    return "diamond"
        case .ghCopilot: return "cat.circle"
        }
    }
}

/// Result of probing the host for a provider CLI.
struct ProviderDetection: Sendable, Identifiable, Equatable {
    let id: ProviderID
    let available: Bool
    let executablePath: String?
    let version: String?
    let detail: String?

    static func unavailable(_ id: ProviderID, detail: String) -> ProviderDetection {
        ProviderDetection(id: id, available: false, executablePath: nil, version: nil, detail: detail)
    }
}

/// Static declaration of what a provider supports.
struct ProviderCapabilities: Sendable {
    let streaming: Bool
    let models: [String]
    /// Human label for how the CLI handles tool/file permissions.
    let permissionModel: String
}

/// Inputs for a single provider run.
struct ProviderRunParams: Sendable {
    let runId: UUID
    let cwd: URL
    /// IDFW/FORCE-aware framing prepended to the user's idea (built by the
    /// orchestrator per lifecycle phase).
    let systemPrompt: String
    /// The raw user idea / phase instruction.
    let userPrompt: String
    let model: String?
}

/// A normalized event emitted by any provider, regardless of its native
/// stream format. SwiftUI renders these directly.
struct ProviderEvent: Identifiable, Sendable, Hashable {
    enum Kind: String, Sendable {
        case thinking
        case text
        case toolCall
        case toolResult
        case fileWrite
        case fileDelete
        case notice
        case error
        case done
    }

    let id: UUID
    let kind: Kind
    let text: String
    let timestamp: Date

    init(_ kind: Kind, _ text: String) {
        self.id = UUID()
        self.kind = kind
        self.text = text
        self.timestamp = Date()
    }

    var symbol: String {
        switch kind {
        case .thinking:   return "brain"
        case .text:       return "text.alignleft"
        case .toolCall:   return "wrench.and.screwdriver"
        case .toolResult: return "arrow.turn.down.right"
        case .fileWrite:  return "doc.badge.plus"
        case .fileDelete: return "doc.badge.minus"
        case .notice:     return "info.circle"
        case .error:      return "exclamationmark.triangle.fill"
        case .done:       return "checkmark.seal.fill"
        }
    }
}
