import Foundation

enum SampleData {

    // MARK: - Active project

    static let activeProject = BuilderProject(
        id: "wayfinder",
        name: "Wayfinder",
        description: "AI-powered navigation assistant for urban explorers",
        phase: .definition,
        provider: .claude,
        llmModel: "claude-sonnet-4-6",
        gateStatuses: ["ideation": .passed, "definition": .pending],
        updatedAt: Date()
    )

    // MARK: - Projects

    static let projects: [BuilderProject] = [
        activeProject,
        BuilderProject(id: "nebulafs", name: "NebulaFS",
                       description: "Distributed filesystem with CRDTs",
                       phase: .evaluation, provider: .codex, llmModel: "o4-mini",
                       gateStatuses: ["ideation": .passed, "definition": .passed, "evaluation": .pending],
                       updatedAt: Date().addingTimeInterval(-3600)),
        BuilderProject(id: "auroradb", name: "AuroraDB",
                       description: "Vector + relational hybrid database",
                       phase: .application, provider: .gemini, llmModel: "gemini-2.0-flash",
                       gateStatuses: ["ideation": .passed, "definition": .passed, "evaluation": .passed, "application": .pending],
                       updatedAt: Date().addingTimeInterval(-7200)),
        BuilderProject(id: "fluxci", name: "FluxCI",
                       description: "Declarative CI/CD runtime",
                       phase: .ideation, provider: .copilot, llmModel: "gpt-4o",
                       gateStatuses: [:],
                       updatedAt: Date().addingTimeInterval(-86400)),
        BuilderProject(id: "prismauth", name: "PrismAuth",
                       description: "Zero-trust authentication proxy",
                       phase: .definition, provider: .claude, llmModel: "claude-opus-4-7",
                       gateStatuses: ["ideation": .passed],
                       updatedAt: Date().addingTimeInterval(-172800)),
    ]

    // MARK: - Skills

    static let skills: [BuilderSkill] = [
        BuilderSkill(id: "s1", title: "Discover", command: "/idea discover", phase: .ideation,
                     description: "Guided discovery wizard"),
        BuilderSkill(id: "s2", title: "Problem Statement", command: "/problem-statement", phase: .ideation,
                     description: "Frame the core problem"),
        BuilderSkill(id: "s3", title: "Jobs-to-be-Done", command: "/jobs-to-be-done", phase: .ideation,
                     description: "JTBD framework"),
        BuilderSkill(id: "s4", title: "RACI Matrix", command: "/raci", phase: .ideation,
                     description: "Roles and responsibilities"),
        BuilderSkill(id: "s5", title: "Define", command: "/idea define", phase: .definition,
                     description: "PRD generation chain"),
        BuilderSkill(id: "s6", title: "PRD", command: "/prd", phase: .definition,
                     description: "Product requirements document"),
        BuilderSkill(id: "s7", title: "Ralph", command: "/ralph", phase: .definition,
                     description: "Autonomous fix loop"),
        BuilderSkill(id: "s8", title: "DDD", command: "/ddd", phase: .definition,
                     description: "Domain-driven design"),
        BuilderSkill(id: "s9", title: "Plan", command: "/idea plan", phase: .evaluation,
                     description: "UPM + Plane orchestration"),
        BuilderSkill(id: "s10", title: "UPM Plan", command: "/upm plan", phase: .evaluation,
                     description: "Unified project management"),
        BuilderSkill(id: "s11", title: "Risk Assessment", command: "/risk", phase: .evaluation,
                     description: "Risk identification and scoring"),
        BuilderSkill(id: "s12", title: "Execute", command: "/idea execute", phase: .application,
                     description: "Formation deployment bridge"),
        BuilderSkill(id: "s13", title: "UPM Build", command: "/upm build", phase: .application,
                     description: "Build orchestration"),
        BuilderSkill(id: "s14", title: "Ship", command: "/ship", phase: .application,
                     description: "Production deployment"),
        BuilderSkill(id: "s15", title: "Status", command: "/idea status", phase: .ideation,
                     description: "Lifecycle overview"),
    ]

    // MARK: - HyperPlot axes

    static let hyperPlotAxes: [HyperPlotAxis] = [
        HyperPlotAxis(id: "scope", label: "Scope", value: 7, maxValue: 10, targetValue: 8),
        HyperPlotAxis(id: "security", label: "Security", value: 6, maxValue: 10, targetValue: 9),
        HyperPlotAxis(id: "complexity", label: "Complexity", value: 8, maxValue: 10, targetValue: 6),
        HyperPlotAxis(id: "compliance", label: "Compliance", value: 5, maxValue: 10, targetValue: 8),
        HyperPlotAxis(id: "performance", label: "Performance", value: 7, maxValue: 10, targetValue: 8),
        HyperPlotAxis(id: "ux", label: "UX Maturity", value: 6, maxValue: 10, targetValue: 7),
        HyperPlotAxis(id: "ttm", label: "Time-to-Market", value: 5, maxValue: 10, targetValue: 6),
    ]

    // MARK: - Active gate

    nonisolated(unsafe) static let activeGate: DecisionGate.Full = {
        var gate = DecisionGate.Full(
            id: "define",
            phase: .definition,
            status: .pending,
            criteria: [
                DecisionGate.Criterion(id: "c1", label: "Problem statement is well-formed",
                                       status: .pass, detail: "Validated via /problem-statement"),
                DecisionGate.Criterion(id: "c2", label: "PRD approved by stakeholders",
                                       status: .pass, detail: "v1.2 reviewed and signed off"),
                DecisionGate.Criterion(id: "c3", label: "Architecture diagram reviewed",
                                       status: .pending, detail: "Awaiting architect sign-off"),
                DecisionGate.Criterion(id: "c4", label: "Security requirements documented",
                                       status: .fail, detail: "OWASP checklist incomplete"),
                DecisionGate.Criterion(id: "c5", label: "DDD ubiquitous language defined",
                                       status: .pass),
            ],
            artifacts: [
                DecisionGate.Artifact(id: "a1", name: "PRD v1.2", icon: "doc.text"),
                DecisionGate.Artifact(id: "a2", name: "System Architecture", icon: "chart.bar"),
                DecisionGate.Artifact(id: "a3", name: "Domain Model", icon: "circle.grid.2x2"),
                DecisionGate.Artifact(id: "a4", name: "API Contract", icon: "arrow.left.arrow.right"),
                DecisionGate.Artifact(id: "a5", name: "Risk Register", icon: "exclamationmark.triangle"),
            ],
            onResolve: nil
        )
        return gate
    }()

    // MARK: - Transcript

    nonisolated(unsafe) static let transcript: [TranscriptMessage] = {
        var msgs: [TranscriptMessage] = []
        let add = { (kind: TranscriptMessage.MessageKind) in
            msgs.append(TranscriptMessage(id: UUID(), kind: kind, timestamp: Date()))
        }

        add(.system(SystemMessage(text: "Project Wayfinder initialized · IDEA v4.0 · claude-sonnet-4-6")))
        add(.phaseTransition(PhaseTransition(from: nil, to: .ideation, label: "Entering Discovery")))
        add(.user(UserMessage(text: "I want to build an AI-powered navigation system for urban explorers")))
        add(.agent(AgentMessage(text: "Great starting point. Let me run the discovery wizard to validate your problem statement before we move into definition.", providerKind: .claude)))
        add(.toolCall(ToolCallMessage(id: UUID(), tool: "/idea discover", status: .done,
            summary: "Discovery complete — problem statement validated",
            children: [
                ToolCallMessage(id: UUID(), tool: "problem_statement_generator", status: .done, summary: nil, children: []),
                ToolCallMessage(id: UUID(), tool: "jobs_to_be_done", status: .done, summary: nil, children: []),
                ToolCallMessage(id: UUID(), tool: "raci_builder", status: .done, summary: nil, children: []),
            ])))
        add(.agent(AgentMessage(text: "Discovery complete. Your problem statement is well-formed: urban explorers lack real-time, context-aware navigation that adapts to their curiosity and safety constraints. Ready to advance to Definition?", providerKind: .claude)))
        add(.gateRef(GateRefMessage(phase: .ideation, resolution: .approve)))
        add(.phaseTransition(PhaseTransition(from: .ideation, to: .definition, label: "Gate passed · Entering Definition")))
        add(.user(UserMessage(text: "Yes, let's define the product. Generate the PRD.")))
        add(.agent(AgentMessage(text: "Generating PRD and architecture artifacts for Wayfinder…", providerKind: .claude, isThinking: true)))
        add(.toolCall(ToolCallMessage(id: UUID(), tool: "/prd", status: .done,
            summary: "PRD v1.2 generated — 4 epics, 23 user stories",
            children: [
                ToolCallMessage(id: UUID(), tool: "prd_generator", status: .done, summary: nil, children: []),
                ToolCallMessage(id: UUID(), tool: "epic_decomposer", status: .done, summary: nil, children: []),
                ToolCallMessage(id: UUID(), tool: "acceptance_criteria_writer", status: .done, summary: nil, children: []),
            ])))
        add(.fileWrite(FileWriteMessage(path: "docs/prd/wayfinder-prd-v1.2.md", lineCount: 312)))
        add(.fileWrite(FileWriteMessage(path: "docs/architecture/system-design.mmd", lineCount: 48)))
        add(.fileWrite(FileWriteMessage(path: "docs/domain/ubiquitous-language.md", lineCount: 89)))
        add(.agent(AgentMessage(text: "PRD v1.2 is ready with 4 epics and 23 user stories. The system architecture uses a microservices mesh with an AI inference layer. Review the Definition Gate below to approve before we move to Planning.", providerKind: .claude)))
        add(.gate(activeGate))

        return msgs
    }()

    // MARK: - Agent graph nodes + edges

    static let graphNodes: [GraphNode] = [
        GraphNode(id: "claude", label: "claude-sonnet-4-6", kind: .agent, phase: .definition, status: .running),
        GraphNode(id: "discover", label: "/idea discover", kind: .skill, phase: .ideation, status: .done),
        GraphNode(id: "prd_gen", label: "prd_generator", kind: .skill, phase: .definition, status: .done),
        GraphNode(id: "epic", label: "epic_decomposer", kind: .skill, phase: .definition, status: .done),
        GraphNode(id: "arch", label: "arch_builder", kind: .skill, phase: .definition, status: .running),
        GraphNode(id: "risk", label: "risk_assessor", kind: .skill, phase: .evaluation, status: .pending),
        GraphNode(id: "bash1", label: "Bash", kind: .tool, phase: nil, status: .done),
        GraphNode(id: "bash2", label: "Bash", kind: .tool, phase: nil, status: .done),
        GraphNode(id: "read1", label: "Read", kind: .tool, phase: nil, status: .done),
        GraphNode(id: "write1", label: "Write", kind: .tool, phase: nil, status: .done),
        GraphNode(id: "write2", label: "Write", kind: .tool, phase: nil, status: .done),
        GraphNode(id: "prd_doc", label: "PRD v1.2", kind: .artifact, phase: .definition, status: .done),
        GraphNode(id: "arch_doc", label: "Architecture", kind: .artifact, phase: .definition, status: .running),
    ]

    static let graphEdges: [GraphEdge] = [
        GraphEdge(id: "e1", sourceID: "claude", targetID: "discover"),
        GraphEdge(id: "e2", sourceID: "claude", targetID: "prd_gen"),
        GraphEdge(id: "e3", sourceID: "claude", targetID: "arch"),
        GraphEdge(id: "e4", sourceID: "prd_gen", targetID: "epic"),
        GraphEdge(id: "e5", sourceID: "prd_gen", targetID: "bash1"),
        GraphEdge(id: "e6", sourceID: "arch", targetID: "bash2"),
        GraphEdge(id: "e7", sourceID: "arch", targetID: "read1"),
        GraphEdge(id: "e8", sourceID: "epic", targetID: "write1"),
        GraphEdge(id: "e9", sourceID: "epic", targetID: "prd_doc"),
        GraphEdge(id: "e10", sourceID: "arch", targetID: "write2"),
        GraphEdge(id: "e11", sourceID: "arch", targetID: "arch_doc"),
        GraphEdge(id: "e12", sourceID: "discover", targetID: "risk"),
    ]

    // MARK: - Event log

    static let events: [BuilderEvent] = [
        BuilderEvent(id: UUID(), timestamp: 0.0, kind: .phaseTransition,
                     label: "Entered Ideation", phase: .ideation, actor: nil),
        BuilderEvent(id: UUID(), timestamp: 1.2, kind: .skill,
                     label: "/idea discover started", phase: .ideation, actor: "claude"),
        BuilderEvent(id: UUID(), timestamp: 3.4, kind: .tool,
                     label: "problem_statement_generator", phase: .ideation, actor: "claude", durationMs: 2100),
        BuilderEvent(id: UUID(), timestamp: 8.1, kind: .tool,
                     label: "jobs_to_be_done", phase: .ideation, actor: "claude", durationMs: 4700),
        BuilderEvent(id: UUID(), timestamp: 14.2, kind: .gate,
                     label: "Discovery Gate: approved", phase: .ideation),
        BuilderEvent(id: UUID(), timestamp: 14.5, kind: .phaseTransition,
                     label: "Entered Definition", phase: .definition),
        BuilderEvent(id: UUID(), timestamp: 15.0, kind: .llm,
                     label: "claude-sonnet-4-6 · 2,341 tokens", phase: .definition, actor: "claude", tokens: 2341),
        BuilderEvent(id: UUID(), timestamp: 18.3, kind: .skill,
                     label: "/prd started", phase: .definition, actor: "claude"),
        BuilderEvent(id: UUID(), timestamp: 22.1, kind: .tool,
                     label: "prd_generator", phase: .definition, actor: "claude", durationMs: 3800),
        BuilderEvent(id: UUID(), timestamp: 31.4, kind: .file,
                     label: "Write: docs/prd/wayfinder-prd-v1.2.md (312 lines)", phase: .definition, actor: "claude"),
        BuilderEvent(id: UUID(), timestamp: 35.8, kind: .file,
                     label: "Write: docs/architecture/system-design.mmd", phase: .definition, actor: "claude"),
        BuilderEvent(id: UUID(), timestamp: 41.2, kind: .llm,
                     label: "claude-sonnet-4-6 · 4,892 tokens", phase: .definition, actor: "claude", tokens: 4892),
        BuilderEvent(id: UUID(), timestamp: 45.0, kind: .gate,
                     label: "Definition Gate: pending review", phase: .definition),
    ]

    // MARK: - File tree

    static let fileTree: [FileEntry] = [
        FileEntry(id: UUID(), name: "docs", isDirectory: true, phase: nil, children: [
            FileEntry(id: UUID(), name: "prd", isDirectory: true, phase: .definition, children: [
                FileEntry(id: UUID(), name: "wayfinder-prd-v1.2.md", isDirectory: false, phase: .definition, size: 12_843),
            ]),
            FileEntry(id: UUID(), name: "architecture", isDirectory: true, phase: .definition, children: [
                FileEntry(id: UUID(), name: "system-design.mmd", isDirectory: false, phase: .definition, size: 2_108),
                FileEntry(id: UUID(), name: "domain-model.puml", isDirectory: false, phase: .definition, size: 1_440),
            ]),
            FileEntry(id: UUID(), name: "domain", isDirectory: true, phase: .definition, children: [
                FileEntry(id: UUID(), name: "ubiquitous-language.md", isDirectory: false, phase: .definition, size: 4_220),
            ]),
        ]),
        FileEntry(id: UUID(), name: ".force", isDirectory: true, phase: .application, children: [
            FileEntry(id: UUID(), name: "governance.json", isDirectory: false, phase: .application, size: 890),
        ]),
        FileEntry(id: UUID(), name: "schemas", isDirectory: true, phase: .definition, children: [
            FileEntry(id: UUID(), name: "wayfinder.idfw.json", isDirectory: false, phase: .definition, size: 3_200),
            FileEntry(id: UUID(), name: "constraints.idpc.json", isDirectory: false, phase: .evaluation, size: 1_400),
        ]),
    ]

    // MARK: - Milestones

    static let milestones: [Milestone] = [
        Milestone(id: UUID(), title: "Discovery Complete", phase: .ideation, status: .done, dueDate: "Apr 28"),
        Milestone(id: UUID(), title: "PRD v1.0 Draft", phase: .definition, status: .done, dueDate: "May 5"),
        Milestone(id: UUID(), title: "Architecture Review", phase: .definition, status: .inProgress, dueDate: "May 20"),
        Milestone(id: UUID(), title: "Definition Gate", phase: .definition, status: .inProgress, dueDate: "May 22"),
        Milestone(id: UUID(), title: "Risk Assessment", phase: .evaluation, status: .todo, dueDate: "May 28"),
        Milestone(id: UUID(), title: "Planning Gate", phase: .evaluation, status: .todo, dueDate: "Jun 2"),
        Milestone(id: UUID(), title: "Sprint 1 Launch", phase: .application, status: .todo, dueDate: "Jun 9"),
    ]

    // MARK: - Risks

    static let risks: [RiskItem] = [
        RiskItem(id: UUID(), label: "API rate limits from mapping providers", likelihood: 2, impact: 3, phase: .application),
        RiskItem(id: UUID(), label: "Real-time location accuracy on iOS", likelihood: 1, impact: 3, phase: .evaluation),
        RiskItem(id: UUID(), label: "LLM hallucinations in navigation context", likelihood: 3, impact: 3, phase: .definition),
        RiskItem(id: UUID(), label: "Scope creep from social features", likelihood: 3, impact: 2, phase: .ideation),
        RiskItem(id: UUID(), label: "Privacy regulations for location data", likelihood: 2, impact: 3, phase: .evaluation),
        RiskItem(id: UUID(), label: "Battery drain from continuous GPS", likelihood: 2, impact: 2, phase: .application),
    ]

    // MARK: - PRD markdown

    static let activePRD = """
# Wayfinder — Product Requirements Document v1.2

## Overview
Wayfinder is an AI-powered navigation assistant designed for urban explorers who want context-aware, curiosity-driven navigation that adapts to their interests and safety constraints.

## Problem Statement
Urban explorers lack navigation tools that respect their curiosity and safety simultaneously. Existing tools optimize for efficiency, not discovery.

## Core Epics

### Epic 1: Intelligent Route Generation
Generate routes that balance efficiency with exploration potential, incorporating user preferences, safety scores, and points of interest.

- US-001: As an explorer, I can set a destination with a "curiosity radius" so that Wayfinder suggests interesting detours.
- US-002: As a user, I can see a safety overlay that shows real-time risk factors along my route.
- US-003: As an explorer, I can save favorite "wander zones" that Wayfinder prioritizes in future routes.

### Epic 2: AI Context Engine
Persistent AI understanding of user preferences, past explorations, and current context.

- US-010: As a user, my exploration history informs future recommendations without manual configuration.
- US-011: As an explorer, I can ask natural language questions about my surroundings ("What's the history of this street?").

### Epic 3: Safety Intelligence
Real-time safety assessment using multiple data sources with privacy-preserving aggregation.

- US-020: Safety score updated every 5 minutes using aggregated anonymized data.
- US-021: Emergency routing to nearest safe zone with one gesture.

### Epic 4: Community Layer
Opt-in community features for sharing discoveries.

- US-030: Publish discovered routes with privacy controls.
- US-031: Follow other explorers' discovery feeds.

## Technical Architecture
Microservices mesh with AI inference layer, real-time location processing, and edge-first privacy model.
"""
}
