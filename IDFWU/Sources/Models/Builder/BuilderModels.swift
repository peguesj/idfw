import Foundation

// MARK: - DecisionGate (extended)

extension DecisionGate {
    struct Criterion: Identifiable, Codable {
        let id: String
        var label: String
        var status: CriterionStatus
        var detail: String?

        enum CriterionStatus: String, Codable {
            case pass, fail, pending, info
        }
    }

    struct Artifact: Identifiable, Codable {
        let id: String
        var name: String
        var icon: String?
    }

    /// Full gate with structured criteria and artifacts.
    struct Full: Identifiable {
        let id: String
        var phase: IDEAPhase
        var status: GateStatus
        var criteria: [Criterion]
        var artifacts: [Artifact]
        var onResolve: ((GateResolution) -> Void)?

        enum GateResolution: String {
            case approve, requestChanges, waive, reject
        }
    }
}

// MARK: - Builder project model

struct BuilderProject: Identifiable, Codable, Hashable {
    let id: String
    var name: String
    var description: String
    var phase: IDEAPhase
    var provider: AIProviderKind
    var llmModel: String
    var gateStatuses: [String: DecisionGate.GateStatus]
    var updatedAt: Date

    static func == (lhs: BuilderProject, rhs: BuilderProject) -> Bool { lhs.id == rhs.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }
}

// MARK: - Chat transcript models

struct TranscriptMessage: Identifiable {
    let id: UUID
    var kind: MessageKind
    var timestamp: Date

    enum MessageKind {
        case user(UserMessage)
        case agent(AgentMessage)
        case system(SystemMessage)
        case phaseTransition(PhaseTransition)
        case toolCall(ToolCallMessage)
        case fileWrite(FileWriteMessage)
        case gateRef(GateRefMessage)
        case gate(DecisionGate.Full)
    }
}

struct UserMessage {
    var text: String
    var authorName: String = "You"
}

struct AgentMessage {
    var text: String
    var providerKind: AIProviderKind
    var isThinking: Bool = false
}

struct SystemMessage {
    var text: String
}

struct PhaseTransition {
    var from: IDEAPhase?
    var to: IDEAPhase
    var label: String
}

struct ToolCallMessage: Identifiable {
    let id: UUID
    var tool: String
    var status: ToolStatus
    var summary: String?
    var children: [ToolCallMessage]
    var isExpanded: Bool = true

    enum ToolStatus: String {
        case running, done, failed
    }
}

struct FileWriteMessage {
    var path: String
    var lineCount: Int?
}

struct GateRefMessage {
    var phase: IDEAPhase
    var resolution: DecisionGate.Full.GateResolution
}

// MARK: - Skills catalog

struct BuilderSkill: Identifiable {
    let id: String
    var title: String
    var command: String
    var phase: IDEAPhase
    var description: String
}

// MARK: - HyperPlot axis

struct HyperPlotAxis: Identifiable {
    let id: String
    var label: String
    var value: Double
    var maxValue: Double
    var targetValue: Double?

    var normalizedValue: Double { value / maxValue }
    var normalizedTarget: Double { (targetValue ?? maxValue) / maxValue }
}

// MARK: - Agent graph node/edge

struct GraphNode: Identifiable {
    let id: String
    var label: String
    var kind: NodeKind
    var phase: IDEAPhase?
    var status: NodeStatus
    var x: Double = 0
    var y: Double = 0
    var vx: Double = 0
    var vy: Double = 0

    enum NodeKind {
        case agent, skill, tool, artifact
    }

    enum NodeStatus: String {
        case running, done, failed, pending
    }
}

struct GraphEdge: Identifiable {
    let id: String
    var sourceID: String
    var targetID: String
}

// MARK: - Event log

struct BuilderEvent: Identifiable {
    let id: UUID
    var timestamp: Double
    var kind: EventKind
    var label: String
    var phase: IDEAPhase?
    var actor: String?
    var durationMs: Int?
    var tokens: Int?

    enum EventKind: String {
        case phaseTransition = "phase"
        case gate            = "gate"
        case tool            = "tool"
        case llm             = "llm"
        case file            = "file"
        case skill           = "skill"
    }
}

// MARK: - Workspace tab

enum WorkspaceTab: String, CaseIterable, Identifiable {
    case artifact = "Artifact"
    case files    = "Files"
    case diagram  = "Diagram"
    case plan     = "Plan"
    case hyperplot = "HyperPlot"
    case telemetry = "Telemetry"

    var id: String { rawValue }

    var symbol: String {
        switch self {
        case .artifact:  return "doc.text"
        case .files:     return "folder"
        case .diagram:   return "chart.bar.doc.horizontal"
        case .plan:      return "checklist"
        case .hyperplot: return "chart.xyaxis.line"
        case .telemetry: return "waveform"
        }
    }
}

// MARK: - File tree

struct FileEntry: Identifiable {
    let id: UUID
    var name: String
    var isDirectory: Bool
    var phase: IDEAPhase?
    var children: [FileEntry]?
    var size: Int?
}

// MARK: - Plan

struct Milestone: Identifiable {
    let id: UUID
    var title: String
    var phase: IDEAPhase
    var status: MilestoneStatus
    var dueDate: String?

    enum MilestoneStatus: String {
        case done, inProgress, blocked, todo
    }
}

struct RiskItem: Identifiable {
    let id: UUID
    var label: String
    var likelihood: Int   // 1–3
    var impact: Int       // 1–3
    var phase: IDEAPhase

    var score: Int { likelihood * impact }
}

// MARK: - Builder scene

enum BuilderScene: String {
    case hero
    case discover
    case active
    case gate
    case plan
    case hyperplot
    case diagram
    case telemetry
    case browser
}

// MARK: - AI Provider kind (builder-facing subset)

enum AIProviderKind: String, Codable, CaseIterable, Identifiable {
    case claude
    case codex
    case gemini
    case copilot

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .claude:  return "Claude Code"
        case .codex:   return "Codex CLI"
        case .gemini:  return "Gemini CLI"
        case .copilot: return "GitHub Copilot"
        }
    }

    var color: Color {
        switch self {
        case .claude:  return DesignTokens.Provider.claude
        case .codex:   return DesignTokens.Provider.codex
        case .gemini:  return DesignTokens.Provider.gemini
        case .copilot: return DesignTokens.Provider.copilot
        }
    }
}

import SwiftUI
