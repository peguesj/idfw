import Foundation

/// The canonical, determined `/idea` pathway baked into the app as a typed
/// reference. Source of truth: `~/.claude/skills/idea/SKILL.md` +
/// `idea-framework/docs/IDEA_Complete_Reference.md`.
///
/// The `/idea` skill walks a project through an ordered lifecycle —
/// **new → discover → define → plan → execute → status** — with a human
/// decision gate between phases. The Swift `IDEAPhase` enum
/// (ideation/definition/evaluation/application) is the UI grouping; this
/// type carries the *procedural* pathway (commands, sub-steps, artifacts,
/// gate criteria) that the guided Builder follows.
struct IDEAPathway {

    struct Stage: Identifiable, Sendable {
        let id: String
        let phase: IDEAPhase
        let command: String          // the `/idea` sub-command
        let title: String
        let purpose: String
        let subSteps: [String]
        let artifacts: [String]      // IDEA schema artifact filenames produced
        let gateTitle: String
        let gateCriteria: String
    }

    /// Ordered stages — strictly sequential, gated between each.
    static let stages: [Stage] = [
        Stage(
            id: "discover",
            phase: .ideation,
            command: "/idea discover",
            title: "Discover",
            purpose: "Deepen user, market and risk understanding; frame the problem.",
            subSteps: [
                "Capture problem context (guided intake, 5–8 questions)",
                "Formalize the problem statement (/problem-statement)",
                "Capture user jobs (/jobs-to-be-done)",
                "Risk assessment, constraints & assumptions registry",
                "Stakeholder registry + RACI matrix"
            ],
            artifacts: ["idea_context.json", "*.idfpj.json", "problem_statement"],
            gateTitle: "Discovery Gate",
            gateCriteria: "Problem statement well-formed, JTBD complete, constraints & RACI documented."
        ),
        Stage(
            id: "define",
            phase: .definition,
            command: "/idea define",
            title: "Define",
            purpose: "Convert discovery into a PRD + machine-readable prd.json and the IDEA definition artifacts.",
            subSteps: [
                "Generate PRD (/prd) from discovery context",
                "Convert PRD → prd.json (/ralph)",
                "User stories + epics + acceptance criteria",
                "Architecture: variables/diagrams/contracts/actions + DDD",
                "Validate prd.json against schema"
            ],
            artifacts: ["prd.json", "*.idfw.json", "*.iddv.json", "*.iddg.json",
                        "*.iddc.json", "*.idda.json", "domain.ddd.md"],
            gateTitle: "Definition Gate",
            gateCriteria: "PRD + prd.json schema-valid, stories have acceptance criteria, architecture sound."
        ),
        Stage(
            id: "plan",
            phase: .evaluation,
            command: "/idea plan",
            title: "Plan",
            purpose: "Create tracking infrastructure, risk matrix and milestone timeline from the PRD.",
            subSteps: [
                "Create Plane issues + CLAUDE.md checkpoints (/upm plan)",
                "Milestone timeline + resource allocation",
                "Risk matrix with mitigations",
                "Communication plan + orchestration topology"
            ],
            artifacts: ["*.idpc.json", "*.idpg.json", "risk_matrix", "plane_issue_ids"],
            gateTitle: "Planning Gate",
            gateCriteria: "Milestones mapped, risks mitigated, Plane issues created, resourcing realistic."
        ),
        Stage(
            id: "execute",
            phase: .application,
            command: "/idea execute",
            title: "Execute",
            purpose: "Formation-based agent deployment against the plan; build the thing.",
            subSteps: [
                "Trigger formation deployment (/upm build)",
                "Spawn agents; run waves against checkpoints",
                "Pre-commit / compliance / security gates",
                "Live integration tests; capture patterns; /ship"
            ],
            artifacts: ["*.idfpj.json", "formation_id", "build artifacts"],
            gateTitle: "Deployment Readiness Gate",
            gateCriteria: "Build runs, checks green, compliance audit passed, journey documented."
        )
    ]

    static func stage(for phase: IDEAPhase) -> Stage {
        stages.first { $0.phase == phase } ?? stages[0]
    }

    static func next(after phase: IDEAPhase) -> Stage? {
        guard let idx = stages.firstIndex(where: { $0.phase == phase }),
              idx + 1 < stages.count else { return nil }
        return stages[idx + 1]
    }
}
