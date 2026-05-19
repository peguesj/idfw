import Foundation

// MARK: - Events the engine emits

enum IdeaEngineEvent: Sendable {
    case textToken(String)
    case projectSpec(IdeaProjectSpec)
    case error(String)
    case done
}

// MARK: - Structured output from scaffold_project tool

struct IdeaProjectSpec: Sendable {
    var project: IdeaProjectMeta
    var artifactMarkdown: String
    var constraints: [ConstraintItem]
    var actions: [ActionItem]
    var hyperplotAxes: [HyperPlotAxis]
    var milestones: [Milestone]
    var risks: [RiskItem]
    var files: [FileEntry]
}

struct IdeaProjectMeta: Sendable {
    var name: String
    var description: String
    var phase: IDEAPhase
    var provider: AIProviderKind
    var model: String
}

// MARK: - Engine

struct IdeaEngine {

    private static let specStartMarker = "IDFWU_SPEC_JSON_START"
    private static let specEndMarker   = "IDFWU_SPEC_JSON_END"

    // MARK: Entry point — keychain API key first, env fallback, CLI last resort

    static func analyze(idea: String) -> AsyncThrowingStream<IdeaEngineEvent, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    // 1. Real API key from keychain (stored via Settings → Connectors)
                    let keychainKey = try? await KeychainHelper.shared.get(key: "anthropic.api_key")

                    // 2. Env var only if it's a real API key (not a Claude Code OAuth token)
                    let envKey: String? = {
                        let k = ProcessInfo.processInfo.environment["ANTHROPIC_API_KEY"] ?? ""
                        return k.hasPrefix("sk-ant-api03-") ? k : nil
                    }()

                    if let key = keychainKey ?? envKey, !key.isEmpty {
                        for try await event in analyzeViaAPI(idea: idea, apiKey: key) {
                            continuation.yield(event)
                        }
                        continuation.finish()
                        return
                    }

                    // 3. Dev fixture (CLI auth fails outside Claude Code session; fixture takes priority)
                    let fixturePath = NSHomeDirectory() + "/.idfwu/test-fixture.json"
                    if let data = FileManager.default.contents(atPath: fixturePath),
                       let json = String(data: data, encoding: .utf8),
                       let spec = parseSpec(from: json) {
                        continuation.yield(.textToken("[fixture] "))
                        continuation.yield(.textToken(spec.artifactMarkdown))
                        continuation.yield(.projectSpec(spec))
                        continuation.yield(.done)
                        continuation.finish()
                        return
                    }

                    // 4. CLI path (last resort — requires working claude CLI auth)
                    if let claudePath = ProviderBinaryResolver.resolve(.claude) {
                        for try await event in analyzeViaCLI(idea: idea, claudePath: claudePath) {
                            continuation.yield(event)
                        }
                        continuation.finish()
                        return
                    }

                    continuation.yield(.error("No API key configured. Add your Anthropic API key in Settings → Connectors → Anthropic."))
                    continuation.finish()
                } catch {
                    continuation.yield(.error(error.localizedDescription))
                    continuation.finish()
                }
            }
        }
    }

    // MARK: - CLI path (primary — uses installed claude/codex CLI, no API key needed)

    private static func analyzeViaCLI(
        idea: String,
        claudePath: String
    ) -> AsyncThrowingStream<IdeaEngineEvent, Error> {
        AsyncThrowingStream { continuation in
            Task {
                let proc = ProviderProcess()
                let args = ["-p", "--output-format", "stream-json", "--verbose",
                            "--permission-mode", "bypassPermissions"]
                let prompt = cliSystemPrompt + "\n\n---\n\nAnalyze this product idea and scaffold the IDEA project: \(idea)"

                let tmpDir = FileManager.default.temporaryDirectory
                    .appendingPathComponent("idfwu-idea-\(UUID().uuidString.prefix(8))")
                try? FileManager.default.createDirectory(at: tmpDir, withIntermediateDirectories: true)

                var fullText = ""
                var streamError: String? = nil

                do {
                    let lines = proc.stream(
                        executable: URL(fileURLWithPath: claudePath),
                        arguments: args,
                        // Empty string = remove key from subprocess env, so CLI falls back to OAuth
                        extraEnvironment: ["ANTHROPIC_API_KEY": ""],
                        currentDirectory: tmpDir,
                        stdin: prompt
                    )
                    outer: for try await line in lines {
                        if Task.isCancelled { break }
                        for event in ProviderStreamParser.parse(line: line, provider: .claude) {
                            switch event.kind {
                            case .text, .thinking:
                                if !event.text.isEmpty {
                                    fullText += event.text
                                    continuation.yield(.textToken(event.text))
                                }
                            case .error:
                                streamError = event.text
                                continuation.yield(.error(event.text))
                                break outer
                            default:
                                break
                            }
                        }
                    }
                } catch {
                    continuation.yield(.error(error.localizedDescription))
                    continuation.finish()
                    return
                }

                // Only attempt spec extraction if no stream-level error occurred
                if streamError == nil {
                    if let spec = extractSpec(from: fullText) {
                        continuation.yield(.projectSpec(spec))
                    } else {
                        continuation.yield(.error("Could not parse project spec from Claude's response. The discovery analysis is shown above."))
                    }
                }

                continuation.yield(.done)
                continuation.finish()
            }
        }
    }

    // MARK: - API path (fallback — requires ANTHROPIC_API_KEY or keychain entry)

    private static func analyzeViaAPI(
        idea: String,
        apiKey: String
    ) -> AsyncThrowingStream<IdeaEngineEvent, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    let request = try buildAPIRequest(idea: idea, apiKey: apiKey)
                    let (bytes, response) = try await URLSession.shared.bytes(for: request)
                    guard let http = response as? HTTPURLResponse else {
                        continuation.yield(.error("Invalid HTTP response"))
                        continuation.finish()
                        return
                    }
                    if http.statusCode != 200 {
                        var body = ""
                        for try await line in bytes.lines { body += line }
                        continuation.yield(.error("Anthropic API \(http.statusCode): \(body.prefix(300))"))
                        continuation.finish()
                        return
                    }
                    try await parseAPIStream(bytes: bytes, continuation: continuation)
                } catch {
                    continuation.yield(.error(error.localizedDescription))
                    continuation.finish()
                }
            }
        }
    }

    // MARK: - Spec extraction from CLI text output

    private static func extractSpec(from text: String) -> IdeaProjectSpec? {
        // Look for IDFWU_SPEC_JSON_START...END markers first
        if let startRange = text.range(of: specStartMarker),
           let endRange   = text.range(of: specEndMarker),
           startRange.upperBound < endRange.lowerBound {
            let jsonStr = String(text[startRange.upperBound..<endRange.lowerBound])
                .trimmingCharacters(in: .whitespacesAndNewlines)
            return parseSpec(from: jsonStr)
        }
        // Fallback: look for a ```json code block
        let pattern = "```json\\s*\\n([\\s\\S]*?)\\n```"
        if let regex = try? NSRegularExpression(pattern: pattern),
           let match = regex.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)),
           let range = Range(match.range(at: 1), in: text) {
            return parseSpec(from: String(text[range]))
        }
        return nil
    }

    // MARK: - API request builder

    private static let apiURL   = URL(string: "https://api.anthropic.com/v1/messages")!
    private static let apiModel = "claude-sonnet-4-6"

    private static func buildAPIRequest(idea: String, apiKey: String) throws -> URLRequest {
        var req = URLRequest(url: apiURL)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        req.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")

        let body: [String: Any] = [
            "model": apiModel,
            "max_tokens": 8192,
            "stream": true,
            "system": apiSystemPrompt,
            "tools": [scaffoldProjectTool],
            "tool_choice": ["type": "auto"],
            "messages": [["role": "user", "content": "Analyze this product idea and scaffold the IDEA project: \(idea)"]]
        ]
        req.httpBody = try JSONSerialization.data(withJSONObject: body)
        return req
    }

    // MARK: - SSE stream parser (API path)

    private static func parseAPIStream(
        bytes: URLSession.AsyncBytes,
        continuation: AsyncThrowingStream<IdeaEngineEvent, Error>.Continuation
    ) async throws {
        var inToolBlock = false
        var toolJSON = ""

        for try await line in bytes.lines {
            guard line.hasPrefix("data: ") else { continue }
            let jsonStr = String(line.dropFirst(6))
            guard jsonStr != "[DONE]",
                  let data = jsonStr.data(using: .utf8),
                  let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let type_ = obj["type"] as? String
            else { continue }

            switch type_ {
            case "content_block_start":
                guard let block = obj["content_block"] as? [String: Any],
                      let blockType = block["type"] as? String else { break }
                if blockType == "tool_use" { inToolBlock = true; toolJSON = "" }

            case "content_block_delta":
                guard let delta = obj["delta"] as? [String: Any],
                      let deltaType = delta["type"] as? String else { break }
                if deltaType == "text_delta", let text = delta["text"] as? String {
                    continuation.yield(.textToken(text))
                } else if deltaType == "input_json_delta", let partial = delta["partial_json"] as? String {
                    toolJSON += partial
                }

            case "content_block_stop":
                if inToolBlock && !toolJSON.isEmpty {
                    if let spec = parseSpec(from: toolJSON) {
                        continuation.yield(.projectSpec(spec))
                    }
                    inToolBlock = false; toolJSON = ""
                }

            case "message_stop":
                continuation.yield(.done)
                continuation.finish()
                return

            default: break
            }
        }
        continuation.yield(.done)
        continuation.finish()
    }

    // MARK: - JSON → domain model

    private static func parseSpec(from json: String) -> IdeaProjectSpec? {
        guard let data = json.trimmingCharacters(in: .whitespacesAndNewlines).data(using: .utf8),
              let raw = try? JSONDecoder().decode(RawSpec.self, from: data)
        else { return nil }
        return raw.toDomain()
    }

    // MARK: - Shared helpers

    private static func errorStream(_ message: String) -> AsyncThrowingStream<IdeaEngineEvent, Error> {
        AsyncThrowingStream { continuation in
            continuation.yield(.error(message))
            continuation.finish()
        }
    }

    // MARK: - CLI system prompt

    private static let cliSystemPrompt = """
You are an expert IDEA Framework (Ideation→Definition→Evaluation→Application) analyst and product architect.

When given a product idea, do two things in order:

1. Write a thorough discovery analysis as readable markdown covering:
   - Restate the idea as a crisp problem statement
   - Target users and their core jobs-to-be-done (3-5 JTBD statements)
   - Market insight and differentiation angle
   - Key technical and architectural considerations
   - Top constraints and risks specific to this idea

2. After the analysis, output the complete project specification using EXACTLY this format — no backticks around the JSON, just the markers and JSON:

\(specStartMarker)
{"project":{"name":"<app name>","description":"<one sentence description>","phase":"ideation","provider":"claude","model":"claude-sonnet-4-6"},"artifact_markdown":"<full discovery doc as escaped markdown string>","constraints":[{"id":"IDPC-001","title":"<constraint title>","severity":"blocking","status":"pending","source":"<standard/policy>","evidence":"<why this constraint applies>","axis_deltas":{"security":1.5}},...],"actions":[{"id":"act-001","phase":"ideation","action_type":"generate","artifact_id":"DISCOVERY.md","input_refs":[],"status":"done","duration":3.5},...],"hyperplot_axes":[{"id":"scope","label":"Scope","value":7.0,"max_value":10.0,"target_value":6.0},{"id":"security","label":"Security","value":6.0,"max_value":10.0},{"id":"complexity","label":"Complexity","value":5.0,"max_value":10.0},{"id":"compliance","label":"Compliance","value":5.0,"max_value":10.0},{"id":"performance","label":"Performance","value":4.0,"max_value":10.0},{"id":"ux","label":"UX","value":7.0,"max_value":10.0},{"id":"time_to_market","label":"Time to Market","value":5.0,"max_value":10.0}],"milestones":[{"title":"Discovery Complete","phase":"ideation","status":"done"},...],"risks":[{"label":"<risk description>","likelihood":2,"impact":3,"phase":"evaluation"},...],"files":[{"name":"<project-slug>/","is_directory":true,"children":[{"name":"DISCOVERY.md","is_directory":false,"phase":"ideation","size":2800},...]}]}
\(specEndMarker)

Rules for the JSON spec:
- Every axis_deltas value is a number (positive or negative float)
- likelihood and impact are integers 1, 2, or 3
- phase values are exactly: ideation, definition, evaluation, application
- severity values are exactly: blocking, advisory
- status values for constraints: passing, violated, pending, waived
- status values for actions: queued, running, done, failed
- status values for milestones: done, inProgress, blocked, todo
- action_type values: generate, update, remove
- provider values: claude, codex, gemini, copilot
- All string values in the JSON must be properly escaped
- Do NOT use backticks or code fences around the spec block
- Be specific to this exact idea — never use placeholder text
"""

    // MARK: - API system prompt (fallback path)

    private static let apiSystemPrompt = """
You are an expert IDEA Framework (Idea→Definition→Evaluation→Application) analyst and product architect. \
When given a product idea, you:

1. Write a thorough discovery analysis covering:
   - Restate the idea as a crisp problem statement
   - Target users and their core jobs-to-be-done (3-5 JTBD statements)
   - Market insight and differentiation angle
   - Key technical and architectural considerations
   - Top constraints and risks specific to this idea

2. Then call `scaffold_project` with the full structured specification.

Be direct and specific. Every constraint, action, milestone, and risk must be tailored to the \
actual idea — never use generic placeholder text. Score HyperPlot axes based on real project \
characteristics: scope (features needed), security (data sensitivity), complexity (technical depth), \
compliance (legal/regulatory exposure), performance (latency/scale needs), ux (design complexity), \
time_to_market (build timeline pressure). Scale is 0–10.

For the `artifact_markdown`, write a complete discovery document including the problem statement, \
JTBD, key constraints, architecture sketch, and initial risk log in markdown format.
"""

    // MARK: - Tool definition (API fallback path only)

    nonisolated(unsafe) private static let scaffoldProjectTool: [String: Any] = [
        "name": "scaffold_project",
        "description": "Scaffold a full IDEA project specification from the discovery analysis.",
        "input_schema": [
            "type": "object",
            "required": ["project", "artifact_markdown", "constraints", "actions", "hyperplot_axes", "milestones", "risks", "files"],
            "properties": [
                "project": [
                    "type": "object",
                    "required": ["name", "description", "phase", "provider", "model"],
                    "properties": [
                        "name": ["type": "string"],
                        "description": ["type": "string"],
                        "phase": ["type": "string", "enum": ["ideation", "definition", "evaluation", "application"]],
                        "provider": ["type": "string", "enum": ["claude", "codex", "gemini", "copilot"]],
                        "model": ["type": "string"]
                    ]
                ],
                "artifact_markdown": ["type": "string"],
                "constraints": [
                    "type": "array",
                    "items": [
                        "type": "object",
                        "required": ["id", "title", "severity", "status", "source", "evidence", "axis_deltas"],
                        "properties": [
                            "id": ["type": "string"],
                            "title": ["type": "string"],
                            "severity": ["type": "string", "enum": ["blocking", "advisory"]],
                            "status": ["type": "string", "enum": ["passing", "violated", "pending", "waived"]],
                            "source": ["type": "string"],
                            "evidence": ["type": "string"],
                            "axis_deltas": ["type": "object", "additionalProperties": ["type": "number"]]
                        ]
                    ]
                ],
                "actions": [
                    "type": "array",
                    "items": [
                        "type": "object",
                        "required": ["id", "phase", "action_type", "artifact_id", "input_refs", "status"],
                        "properties": [
                            "id": ["type": "string"],
                            "phase": ["type": "string", "enum": ["ideation", "definition", "evaluation", "application"]],
                            "action_type": ["type": "string", "enum": ["generate", "update", "remove"]],
                            "artifact_id": ["type": "string"],
                            "input_refs": ["type": "array", "items": ["type": "string"]],
                            "status": ["type": "string", "enum": ["queued", "running", "done", "failed"]],
                            "duration": ["type": "number"]
                        ]
                    ]
                ],
                "hyperplot_axes": [
                    "type": "array",
                    "items": [
                        "type": "object",
                        "required": ["id", "label", "value", "max_value"],
                        "properties": [
                            "id": ["type": "string"],
                            "label": ["type": "string"],
                            "value": ["type": "number"],
                            "max_value": ["type": "number"],
                            "target_value": ["type": "number"]
                        ]
                    ]
                ],
                "milestones": [
                    "type": "array",
                    "items": [
                        "type": "object",
                        "required": ["title", "phase", "status"],
                        "properties": [
                            "title": ["type": "string"],
                            "phase": ["type": "string", "enum": ["ideation", "definition", "evaluation", "application"]],
                            "status": ["type": "string", "enum": ["done", "inProgress", "blocked", "todo"]],
                            "due_date": ["type": "string"]
                        ]
                    ]
                ],
                "risks": [
                    "type": "array",
                    "items": [
                        "type": "object",
                        "required": ["label", "likelihood", "impact", "phase"],
                        "properties": [
                            "label": ["type": "string"],
                            "likelihood": ["type": "integer", "minimum": 1, "maximum": 3],
                            "impact": ["type": "integer", "minimum": 1, "maximum": 3],
                            "phase": ["type": "string", "enum": ["ideation", "definition", "evaluation", "application"]]
                        ]
                    ]
                ],
                "files": [
                    "type": "array",
                    "items": [
                        "type": "object",
                        "required": ["name", "is_directory"],
                        "properties": [
                            "name": ["type": "string"],
                            "is_directory": ["type": "boolean"],
                            "phase": ["type": "string"],
                            "size": ["type": "integer"],
                            "children": [
                                "type": "array",
                                "items": [
                                    "type": "object",
                                    "required": ["name", "is_directory"],
                                    "properties": [
                                        "name": ["type": "string"],
                                        "is_directory": ["type": "boolean"],
                                        "phase": ["type": "string"],
                                        "size": ["type": "integer"]
                                    ]
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        ] as [String: Any]
    ]
}

// MARK: - Codable raw types for JSON parsing

private struct RawSpec: Codable {
    struct RawProject: Codable {
        let name: String
        let description: String
        let phase: String
        let provider: String
        let model: String
    }
    struct RawConstraint: Codable {
        let id: String
        let title: String
        let severity: String
        let status: String
        let source: String
        let evidence: String
        let axisDelta: [String: Double]
        enum CodingKeys: String, CodingKey {
            case id, title, severity, status, source, evidence
            case axisDelta = "axis_deltas"
        }
    }
    struct RawAction: Codable {
        let id: String
        let phase: String
        let actionType: String
        let artifactId: String
        let inputRefs: [String]
        let status: String
        let duration: Double?
        enum CodingKeys: String, CodingKey {
            case id, phase, status, duration
            case actionType = "action_type"
            case artifactId = "artifact_id"
            case inputRefs = "input_refs"
        }
    }
    struct RawAxis: Codable {
        let id: String
        let label: String
        let value: Double
        let maxValue: Double
        let targetValue: Double?
        enum CodingKeys: String, CodingKey {
            case id, label, value
            case maxValue = "max_value"
            case targetValue = "target_value"
        }
    }
    struct RawMilestone: Codable {
        let title: String
        let phase: String
        let status: String
        let dueDate: String?
        enum CodingKeys: String, CodingKey {
            case title, phase, status
            case dueDate = "due_date"
        }
    }
    struct RawRisk: Codable {
        let label: String
        let likelihood: Int
        let impact: Int
        let phase: String
    }
    struct RawFile: Codable {
        let name: String
        let isDirectory: Bool
        let phase: String?
        let size: Int?
        let children: [RawFile]?
        enum CodingKeys: String, CodingKey {
            case name
            case isDirectory = "is_directory"
            case phase, size, children
        }
    }

    let project: RawProject
    let artifactMarkdown: String
    let constraints: [RawConstraint]
    let actions: [RawAction]
    let hyperplotAxes: [RawAxis]
    let milestones: [RawMilestone]
    let risks: [RawRisk]
    let files: [RawFile]

    enum CodingKeys: String, CodingKey {
        case project
        case artifactMarkdown = "artifact_markdown"
        case constraints, actions
        case hyperplotAxes = "hyperplot_axes"
        case milestones, risks, files
    }

    func toDomain() -> IdeaProjectSpec {
        IdeaProjectSpec(
            project: IdeaProjectMeta(
                name: project.name,
                description: project.description,
                phase: IDEAPhase(rawValue: project.phase) ?? .ideation,
                provider: AIProviderKind(rawValue: project.provider) ?? .claude,
                model: project.model
            ),
            artifactMarkdown: artifactMarkdown,
            constraints: constraints.map { c in
                ConstraintItem(
                    id: c.id,
                    title: c.title,
                    severity: ConstraintItem.ConstraintSeverity(rawValue: c.severity) ?? .advisory,
                    status: ConstraintItem.ConstraintStatus(rawValue: c.status) ?? .pending,
                    source: c.source,
                    evidence: c.evidence,
                    axisDelta: c.axisDelta
                )
            },
            actions: actions.enumerated().map { _, a in
                ActionItem(
                    id: a.id,
                    phase: IDEAPhase(rawValue: a.phase) ?? .ideation,
                    actionType: ActionItem.ActionType(rawValue: a.actionType) ?? .generate,
                    artifactId: a.artifactId,
                    inputRefs: a.inputRefs,
                    status: ActionItem.ActionStatus(rawValue: a.status) ?? .queued,
                    duration: a.duration
                )
            },
            hyperplotAxes: hyperplotAxes.map { a in
                HyperPlotAxis(
                    id: a.id,
                    label: a.label,
                    value: a.value,
                    maxValue: a.maxValue,
                    targetValue: a.targetValue
                )
            },
            milestones: milestones.map { m in
                Milestone(
                    id: UUID(),
                    title: m.title,
                    phase: IDEAPhase(rawValue: m.phase) ?? .ideation,
                    status: Milestone.MilestoneStatus(rawValue: m.status) ?? .todo,
                    dueDate: m.dueDate
                )
            },
            risks: risks.map { r in
                RiskItem(
                    id: UUID(),
                    label: r.label,
                    likelihood: max(1, min(3, r.likelihood)),
                    impact: max(1, min(3, r.impact)),
                    phase: IDEAPhase(rawValue: r.phase) ?? .evaluation
                )
            },
            files: files.map { mapFile($0) }
        )
    }

    private func mapFile(_ f: RawFile) -> FileEntry {
        FileEntry(
            id: UUID(),
            name: f.name,
            isDirectory: f.isDirectory,
            phase: f.phase.flatMap { IDEAPhase(rawValue: $0) },
            children: f.children?.map { mapFile($0) },
            size: f.size
        )
    }
}
