import Foundation

/// Spawns a provider CLI as a child process, pipes the prompt to stdin, and
/// streams stdout line-by-line as an `AsyncThrowingStream`. Cancellation
/// terminates the process.
///
/// This is the Swift analogue of open-design's `execFile(binary, args,
/// { stdio: ['pipe','pipe','pipe'] })` + stdin-write pattern. Prompts always
/// go via stdin to avoid argv length limits.
///
/// `@unchecked Sendable`: the `Process` reference is guarded by an `NSLock`
/// and only touched from the launch closure and `cancel()`.
final class ProviderProcess: @unchecked Sendable {
    private let lock = NSLock()
    private var process: Process?

    /// Emitted alongside stdout lines so the parser can distinguish CLI log
    /// noise (stderr) from protocol output (stdout).
    static let stderrSentinel = "\u{1B}IDFWU_STDERR\u{1B}"

    func stream(
        executable: URL,
        arguments: [String],
        extraEnvironment: [String: String],
        currentDirectory: URL,
        stdin: String
    ) -> AsyncThrowingStream<String, Error> {
        AsyncThrowingStream { continuation in
            let proc = Process()
            proc.executableURL = executable
            proc.arguments = arguments

            var env = ProcessInfo.processInfo.environment
            for (key, value) in extraEnvironment { env[key] = value }
            proc.environment = env
            proc.currentDirectoryURL = currentDirectory

            let outPipe = Pipe()
            let errPipe = Pipe()
            let inPipe = Pipe()
            proc.standardOutput = outPipe
            proc.standardError = errPipe
            proc.standardInput = inPipe

            lock.lock(); self.process = proc; lock.unlock()

            proc.terminationHandler = { finished in
                if finished.terminationStatus != 0 {
                    continuation.yield(
                        "\(ProviderProcess.stderrSentinel)exit status \(finished.terminationStatus)"
                    )
                }
                continuation.finish()
            }

            do {
                try proc.run()
            } catch {
                continuation.finish(throwing: error)
                return
            }

            // Feed the prompt to stdin then close it so the CLI starts work.
            if let data = stdin.data(using: .utf8) {
                inPipe.fileHandleForWriting.write(data)
            }
            try? inPipe.fileHandleForWriting.close()

            let outTask = Task {
                do {
                    for try await line in outPipe.fileHandleForReading.bytes.lines {
                        continuation.yield(line)
                    }
                } catch {
                    continuation.finish(throwing: error)
                }
            }

            let errTask = Task {
                for try await line in errPipe.fileHandleForReading.bytes.lines {
                    continuation.yield(ProviderProcess.stderrSentinel + line)
                }
            }

            continuation.onTermination = { @Sendable _ in
                outTask.cancel()
                errTask.cancel()
                self.cancel()
            }
        }
    }

    func cancel() {
        lock.lock()
        let proc = process
        lock.unlock()
        if let proc, proc.isRunning {
            proc.terminate()
        }
    }
}

/// Resolves a provider binary on `PATH` (plus common GUI-launch locations,
/// since apps launched from Finder get a minimal `PATH`).
enum ProviderBinaryResolver {
    private static let extraDirs = [
        "/opt/homebrew/bin", "/usr/local/bin", "/usr/bin",
        "\(NSHomeDirectory())/.local/bin",
        "\(NSHomeDirectory())/.bun/bin",
        "\(NSHomeDirectory())/.npm-global/bin",
        "\(NSHomeDirectory())/.volta/bin"
    ]

    static func resolve(_ id: ProviderID) -> String? {
        let env = ProcessInfo.processInfo.environment
        if let override = env[id.binaryOverrideEnvKey], !override.isEmpty,
           FileManager.default.isExecutableFile(atPath: override) {
            return override
        }
        let pathDirs = (env["PATH"] ?? "").split(separator: ":").map(String.init)
        let searchDirs = pathDirs + extraDirs
        for name in [id.binaryName] + id.fallbackBinaries {
            for dir in searchDirs {
                let candidate = (dir as NSString).appendingPathComponent(name)
                if FileManager.default.isExecutableFile(atPath: candidate) {
                    return candidate
                }
            }
        }
        return nil
    }
}
