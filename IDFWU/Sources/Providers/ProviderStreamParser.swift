import Foundation

/// Normalizes each provider's native stdout line into `ProviderEvent`s.
///
/// Provider stream formats drift between CLI versions, so this parser is
/// deliberately defensive: it uses `JSONSerialization` (not fixed `Codable`
/// structs), inspects well-known keys, and falls back to surfacing raw text
/// rather than dropping output.
enum ProviderStreamParser {

    /// Parse one stdout/stderr line for `provider` into zero or more events.
    static func parse(line rawLine: String, provider: ProviderID) -> [ProviderEvent] {
        let line = rawLine.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !line.isEmpty else { return [] }

        if line.hasPrefix(ProviderProcess.stderrSentinel) {
            let msg = String(line.dropFirst(ProviderProcess.stderrSentinel.count))
            guard !msg.isEmpty else { return [] }
            let lowered = msg.lowercased()
            // The spawned CLI is itself a Claude Code / Codex session whose
            // own SessionStart/SessionEnd lifecycle hooks emit telemetry on
            // stderr. That is NOT IDFWU build output — drop it so the build
            // console shows the build, not the nested session's plumbing.
            if Self.isNestedSessionNoise(lowered) { return [] }
            let isError = lowered.contains("error") || lowered.contains("exit status")
                || lowered.contains("denied") || lowered.contains("fatal")
            return [ProviderEvent(isError ? .error : .notice, msg)]
        }

        guard let data = line.data(using: .utf8),
              let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            // Non-JSON line (e.g. plain-text mode) — surface verbatim.
            return [ProviderEvent(.text, line)]
        }

        switch provider {
        case .claude:    return parseClaude(obj)
        case .codex:     return parseCodex(obj)
        case .gemini:    return parseGemini(obj)
        case .ghCopilot: return parseGeneric(obj)
        }
    }

    // MARK: - Claude  (`--output-format stream-json`)

    private static func parseClaude(_ obj: [String: Any]) -> [ProviderEvent] {
        let type = (obj["type"] as? String) ?? (obj["subtype"] as? String) ?? ""

        if type == "assistant" || type == "message",
           let message = obj["message"] as? [String: Any],
           let content = message["content"] as? [[String: Any]] {
            return content.compactMap { block in
                switch block["type"] as? String {
                case "text":
                    return (block["text"] as? String).map { ProviderEvent(.text, $0) }
                case "thinking":
                    return (block["thinking"] as? String).map { ProviderEvent(.thinking, $0) }
                case "tool_use":
                    let name = (block["name"] as? String) ?? "tool"
                    return ProviderEvent(.toolCall, name)
                default:
                    return nil
                }
            }
        }
        if type == "result" {
            let summary = (obj["result"] as? String) ?? "run complete"
            return [ProviderEvent(.done, summary)]
        }
        if type == "error" || obj["error"] != nil {
            return [ProviderEvent(.error, describe(obj["error"]) ?? "claude error")]
        }
        if let text = obj["text"] as? String { return [ProviderEvent(.text, text)] }
        return []
    }

    // MARK: - Codex  (`exec --json`)

    private static func parseCodex(_ obj: [String: Any]) -> [ProviderEvent] {
        let type = (obj["type"] as? String) ?? (obj["msg"] as? String) ?? ""
        if type.contains("reasoning"), let t = textValue(obj) {
            return [ProviderEvent(.thinking, t)]
        }
        if type.contains("agent_message") || type.contains("message") || type == "item.completed",
           let t = textValue(obj) {
            return [ProviderEvent(.text, t)]
        }
        if type.contains("exec") || type.contains("command") || type.contains("patch")
            || type.contains("tool") {
            let cmd = (obj["command"] as? String)
                ?? describe(obj["call"]) ?? describe(obj["arguments"]) ?? type
            return [ProviderEvent(.toolCall, cmd)]
        }
        if type.contains("file") {
            let path = (obj["path"] as? String) ?? "file"
            let kind: ProviderEvent.Kind = type.contains("delete") ? .fileDelete : .fileWrite
            return [ProviderEvent(kind, path)]
        }
        if type.contains("complete") || type.contains("turn.completed") || type == "task_complete" {
            return [ProviderEvent(.done, "codex run complete")]
        }
        if type.contains("error") || obj["error"] != nil {
            return [ProviderEvent(.error, describe(obj["error"]) ?? "codex error")]
        }
        if let t = textValue(obj) { return [ProviderEvent(.text, t)] }
        return []
    }

    // MARK: - Gemini  (`--output-format stream-json`)

    private static func parseGemini(_ obj: [String: Any]) -> [ProviderEvent] {
        let type = (obj["type"] as? String) ?? ""
        if type.contains("thought") { return [ProviderEvent(.thinking, textValue(obj) ?? "")] }
        if type.contains("tool") {
            return [ProviderEvent(.toolCall, (obj["name"] as? String) ?? "tool")]
        }
        if type.contains("error") { return [ProviderEvent(.error, describe(obj["error"]) ?? "gemini error")] }
        if type.contains("finish") || type.contains("complete") {
            return [ProviderEvent(.done, "gemini run complete")]
        }
        if let t = textValue(obj) { return [ProviderEvent(.text, t)] }
        return parseGeneric(obj)
    }

    // MARK: - Generic fallback

    private static func parseGeneric(_ obj: [String: Any]) -> [ProviderEvent] {
        if let err = obj["error"] { return [ProviderEvent(.error, describe(err) ?? "error")] }
        if let t = textValue(obj) { return [ProviderEvent(.text, t)] }
        return [ProviderEvent(.notice, describe(obj) ?? "")]
    }

    // MARK: - Helpers

    private static func textValue(_ obj: [String: Any]) -> String? {
        for key in ["text", "content", "message", "delta", "output", "result", "data"] {
            if let s = obj[key] as? String, !s.isEmpty { return s }
            if let nested = obj[key] as? [String: Any], let s = nested["text"] as? String { return s }
        }
        return nil
    }

    private static func describe(_ value: Any?) -> String? {
        guard let value else { return nil }
        if let s = value as? String { return s }
        if let dict = value as? [String: Any] {
            if let m = dict["message"] as? String { return m }
            if let data = try? JSONSerialization.data(withJSONObject: dict),
               let s = String(data: data, encoding: .utf8) { return s }
        }
        return String(describing: value)
    }

    /// True when a stderr line is the nested CLI session's own Claude Code /
    /// Codex lifecycle-hook telemetry or Python-resolver chatter — irrelevant
    /// to the IDFWU build and pure console noise.
    private static func isNestedSessionNoise(_ lowered: String) -> Bool {
        let markers = [
            "sessionend hook", "sessionstart hook", "stop hook",
            "hook cancelled", "hook failed", "hook canceled",
            "session_end", "session_report", "session_start",
            "run_hook.sh", "/.claude/hooks/", "/hooks/codex/",
            "asdf", "could not find python", "using system python",
            "explicit python path not found", "falling back to system python",
            "importing unified framework", "no module named 'gql'",
            "this may cause issues"
        ]
        return markers.contains { lowered.contains($0) }
    }
}
