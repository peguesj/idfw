import SwiftUI

/// The four IDEA framework phases. "IDEA" expands to
/// **Idea-to-Development, Evaluation and Application**
/// (see `idea-framework/docs/IDEA_Complete_Reference.md`).
///
/// Every artifact discovered inside a project — typed IDEA documents, free-form
/// markdown, diagrams, FORCE configs, schemas — is classified into exactly one
/// phase so the UI can group content by the stage of the product lifecycle it
/// belongs to, rather than by file extension.
enum IDEAPhase: String, CaseIterable, Sendable, Hashable {
    /// **I** — Idea / inception. Project seeds, journey definitions, kickoff
    /// material, the raw concept capture that precedes formal definition.
    case ideation

    /// **D** — Development / definition. Schemas, diagrams, contracts,
    /// architecture docs, DDD, the formal artifacts produced by `/idea define`.
    case definition

    /// **E** — Evaluation. Constraints, risk, compliance, tests, security —
    /// anything that judges whether the definition is sound.
    case evaluation

    /// **A** — Application. Governance, FORCE runtime, deployment, CI/CD —
    /// the artifacts that carry the definition into production.
    case application

    /// Single-letter label displayed in the sidebar column header.
    var letter: String {
        switch self {
        case .ideation:    return "I"
        case .definition:  return "D"
        case .evaluation:  return "E"
        case .application: return "A"
        }
    }

    /// Human-readable section title for the phase column.
    var title: String {
        switch self {
        case .ideation:    return "Idea"
        case .definition:  return "Development"
        case .evaluation:  return "Evaluation"
        case .application: return "Application"
        }
    }

    /// One-line subtitle, shown under the phase header.
    var tagline: String {
        switch self {
        case .ideation:    return "Capture the concept"
        case .definition:  return "Define docs, schemas, diagrams"
        case .evaluation:  return "Constraints, risk, compliance"
        case .application: return "Governance, runtime, delivery"
        }
    }

    /// SF Symbol used for the phase header icon.
    var symbol: String {
        switch self {
        case .ideation:    return "lightbulb.fill"
        case .definition:  return "square.stack.3d.up.fill"
        case .evaluation:  return "checkmark.shield.fill"
        case .application: return "paperplane.fill"
        }
    }

    /// Accent color for the phase header and badges.
    var accentColor: Color {
        switch self {
        case .ideation:    return .yellow
        case .definition:  return .blue
        case .evaluation:  return .orange
        case .application: return .green
        }
    }
}

/// Classifies project artifacts into an `IDEAPhase`.
///
/// Resolution order:
/// 1. Typed IDEA schemas (`IDEASchemaType`) — exact mapping.
/// 2. Filename / path heuristics for free-form content (markdown, configs,
///    diagrams, FORCE directories).
/// 3. Fallback based on the coarse `ProjectDocumentType` from the scanner.
enum IDEAPhaseClassifier {

    /// Classify a `ProjectDocument` by inspecting its name and type.
    static func phase(for document: ProjectDocument) -> IDEAPhase {
        let name = document.name.lowercased()
        let path = document.path.lowercased()

        // 1. Typed IDEA schemas (strongest signal).
        if let schemaType = schemaType(fromName: name), let mapped = phase(for: schemaType) {
            return mapped
        }

        // 2. Path / filename heuristics.
        if path.contains("/.force/") || path.contains("/force/") {
            return .application
        }
        if path.contains("/tests/") || path.contains("/test/") || name.hasPrefix("test_") || name.hasSuffix("_test.py") {
            return .evaluation
        }
        if name.contains("constraint") || name.contains("risk") || name.contains("compliance") || name.contains("security") {
            return .evaluation
        }
        if name.contains("govern") || name.contains("policy") || name.contains("deploy") || name.contains("runtime") {
            return .application
        }
        if name.contains("journey") || name.contains("kickoff") || name.contains("inception") || name.contains("idfpj") {
            return .ideation
        }
        if name.contains("prd") || name.contains("brd") || name.contains("frs") || name.contains("tad") || name.contains("api")
            || name.contains("ddd") || name.contains("architecture") || name.contains("spec") || name.contains("schema") {
            return .definition
        }

        // Diagrams always fall into Definition unless they're audit/security diagrams.
        if name.hasSuffix(".mmd") || name.hasSuffix(".mermaid") || name.hasSuffix(".puml") || name.hasSuffix(".plantuml") {
            return .definition
        }

        // 3. Fallback on the scanner's coarse type.
        switch document.type {
        case .schema:  return .definition
        case .force:   return .application
        case .config:  return .application
        case .diagram: return .definition
        case .idea:    return .definition
        case .doc:     return defaultPhaseForGenericDoc(name: name)
        }
    }

    /// Map an `IDEASchemaType` to its canonical phase.
    static func phase(for schemaType: IDEASchemaType) -> IDEAPhase? {
        switch schemaType {
        case .idfpj:           return .ideation      // project journey seed
        case .idpg:            return .ideation      // project generator / prompts
        case .idfw:            return .definition    // master framework spec
        case .iddv:            return .definition    // document variables
        case .iddg:            return .definition    // document diagrams
        case .iddc:            return .definition    // document contracts
        case .idda:            return .definition    // document actions
        case .ddd:             return .definition    // domain-driven design
        case .idpc:            return .evaluation    // constraints
        }
    }

    // MARK: - Helpers

    /// Detect an `IDEASchemaType` from a filename like `foo.idfw.json` or
    /// `bar.idda.schema.json`.
    private static func schemaType(fromName name: String) -> IDEASchemaType? {
        for type in IDEASchemaType.allCases {
            let token = ".\(type.rawValue)."
            if name.contains(token) { return type }
        }
        return nil
    }

    /// README, LICENSE, CHANGELOG etc. are project metadata — surface them under
    /// Ideation so they're easy to find when onboarding to a project.
    private static func defaultPhaseForGenericDoc(name: String) -> IDEAPhase {
        if name.contains("changelog") || name.contains("release") { return .application }
        if name.contains("contributing") || name.contains("license") { return .application }
        return .ideation
    }
}
