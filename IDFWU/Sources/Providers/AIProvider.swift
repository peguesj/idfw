import Foundation

/// A driver for one AI provider CLI. Mirrors open-design's `AgentAdapter`
/// contract (detect / capabilities / run) but emits IDFWU's normalized
/// `ProviderEvent` stream.
protocol AIProvider: Sendable {
    var id: ProviderID { get }
    func detect() async -> ProviderDetection
    func capabilities() -> ProviderCapabilities
    func run(_ params: ProviderRunParams) -> AsyncThrowingStream<ProviderEvent, Error>
}

extension AIProvider {
    /// Shared detection: resolve the binary, then run its `--version`.
    func defaultDetect(versionArgs: [String] = ["--version"]) async -> ProviderDetection {
        guard let path = ProviderBinaryResolver.resolve(id) else {
            return .unavailable(id, detail: "\(id.binaryName) not found on PATH")
        }
        let version = await Self.firstLine(executable: path, args: versionArgs)
        return ProviderDetection(
            id: id,
            available: true,
            executablePath: path,
            version: version ?? "installed",
            detail: nil
        )
    }

    /// Shared run: spawn via `ProviderProcess`, feed `systemPrompt` + a
    /// separator + `userPrompt` to stdin, normalize each stdout line.
    func defaultRun(
        _ params: ProviderRunParams,
        executablePath: String,
        arguments: [String],
        extraEnvironment: [String: String] = [:]
    ) -> AsyncThrowingStream<ProviderEvent, Error> {
        AsyncThrowingStream { continuation in
            let task = Task {
                let proc = ProviderProcess()
                let composedPrompt = """
                \(params.systemPrompt)

                ---

                \(params.userPrompt)
                """
                do {
                    let lines = proc.stream(
                        executable: URL(fileURLWithPath: executablePath),
                        arguments: arguments,
                        extraEnvironment: extraEnvironment,
                        currentDirectory: params.cwd,
                        stdin: composedPrompt
                    )
                    continuation.yield(ProviderEvent(.notice,
                        "\(id.displayName): \(URL(fileURLWithPath: executablePath).lastPathComponent) \(arguments.joined(separator: " "))"))
                    for try await line in lines {
                        for event in ProviderStreamParser.parse(line: line, provider: id) {
                            continuation.yield(event)
                        }
                    }
                    continuation.yield(ProviderEvent(.done, "\(id.displayName) finished"))
                    continuation.finish()
                } catch {
                    continuation.yield(ProviderEvent(.error, error.localizedDescription))
                    continuation.finish(throwing: error)
                }
            }
            continuation.onTermination = { @Sendable _ in task.cancel() }
        }
    }

    static func firstLine(executable: String, args: [String]) async -> String? {
        await withCheckedContinuation { cont in
            let proc = Process()
            proc.executableURL = URL(fileURLWithPath: executable)
            proc.arguments = args
            let pipe = Pipe()
            proc.standardOutput = pipe
            proc.standardError = Pipe()
            proc.terminationHandler = { _ in
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                let out = String(data: data, encoding: .utf8)?
                    .split(separator: "\n").first.map(String.init)?
                    .trimmingCharacters(in: .whitespaces)
                cont.resume(returning: out)
            }
            do { try proc.run() } catch { cont.resume(returning: nil) }
        }
    }
}

// MARK: - Claude Code

struct ClaudeProvider: AIProvider {
    let id: ProviderID = .claude

    func detect() async -> ProviderDetection { await defaultDetect() }

    func capabilities() -> ProviderCapabilities {
        ProviderCapabilities(
            streaming: true,
            models: ["default", "sonnet", "opus", "haiku"],
            permissionModel: "bypassPermissions (--permission-mode)"
        )
    }

    func run(_ params: ProviderRunParams) -> AsyncThrowingStream<ProviderEvent, Error> {
        guard let path = ProviderBinaryResolver.resolve(id) else {
            return unavailableStream(id)
        }
        var args = ["-p", "--output-format", "stream-json", "--verbose"]
        if let model = params.model, model != "default" { args += ["--model", model] }
        args += ["--add-dir", params.cwd.path]
        args += ["--permission-mode", "bypassPermissions"]
        return defaultRun(params, executablePath: path, arguments: args)
    }
}

// MARK: - Codex CLI

struct CodexProvider: AIProvider {
    let id: ProviderID = .codex

    func detect() async -> ProviderDetection { await defaultDetect() }

    func capabilities() -> ProviderCapabilities {
        ProviderCapabilities(
            streaming: true,
            models: ["default", "gpt-5.5", "gpt-5.4"],
            permissionModel: "--sandbox workspace-write"
        )
    }

    func run(_ params: ProviderRunParams) -> AsyncThrowingStream<ProviderEvent, Error> {
        guard let path = ProviderBinaryResolver.resolve(id) else {
            return unavailableStream(id)
        }
        var args = [
            "exec", "--json", "--skip-git-repo-check",
            "--sandbox", "workspace-write",
            "-c", "sandbox_workspace_write.network_access=true",
            "-C", params.cwd.path
        ]
        if let model = params.model, model != "default" { args += ["--model", model] }
        return defaultRun(params, executablePath: path, arguments: args)
    }
}

// MARK: - Gemini CLI

struct GeminiProvider: AIProvider {
    let id: ProviderID = .gemini

    func detect() async -> ProviderDetection { await defaultDetect() }

    func capabilities() -> ProviderCapabilities {
        ProviderCapabilities(
            streaming: true,
            models: ["default", "gemini-2.5-pro", "gemini-2.5-flash"],
            permissionModel: "--yolo (trust workspace)"
        )
    }

    func run(_ params: ProviderRunParams) -> AsyncThrowingStream<ProviderEvent, Error> {
        guard let path = ProviderBinaryResolver.resolve(id) else {
            return unavailableStream(id)
        }
        var args = ["--output-format", "stream-json", "--yolo"]
        if let model = params.model, model != "default" { args += ["--model", model] }
        return defaultRun(params, executablePath: path, arguments: args,
                          extraEnvironment: ["GEMINI_CLI_TRUST_WORKSPACE": "true"])
    }
}

// MARK: - GitHub Copilot CLI

struct GitHubCopilotProvider: AIProvider {
    let id: ProviderID = .ghCopilot

    func detect() async -> ProviderDetection {
        guard let path = ProviderBinaryResolver.resolve(id) else {
            return .unavailable(id, detail: "gh not found on PATH")
        }
        let copilot = await Self.firstLine(executable: path, args: ["copilot", "--version"])
        guard let copilot, !copilot.lowercased().contains("unknown command") else {
            return .unavailable(id, detail: "gh installed but `copilot` extension missing — `gh extension install github/gh-copilot`")
        }
        return ProviderDetection(id: id, available: true, executablePath: path,
                                 version: copilot, detail: nil)
    }

    func capabilities() -> ProviderCapabilities {
        ProviderCapabilities(streaming: false, models: ["default"],
                             permissionModel: "suggestion-only (gh copilot suggest)")
    }

    func run(_ params: ProviderRunParams) -> AsyncThrowingStream<ProviderEvent, Error> {
        guard let path = ProviderBinaryResolver.resolve(id) else {
            return unavailableStream(id)
        }
        // Copilot CLI is advisory: ask it to suggest shell steps for the idea.
        let args = ["copilot", "suggest", "-t", "shell",
                    "\(params.systemPrompt)\n\n\(params.userPrompt)"]
        return defaultRun(
            ProviderRunParams(runId: params.runId, cwd: params.cwd,
                              systemPrompt: "", userPrompt: "", model: params.model),
            executablePath: path, arguments: args)
    }
}

// MARK: - Shared unavailable stream

func unavailableStream(_ id: ProviderID) -> AsyncThrowingStream<ProviderEvent, Error> {
    AsyncThrowingStream { continuation in
        continuation.yield(ProviderEvent(.error,
            "\(id.displayName) CLI is not installed or not on PATH."))
        continuation.finish()
    }
}
