import Foundation
import Observation

/// Owns the lifecycle of the `/idea` AG-UI FastAPI daemon (the server behind
/// `http://localhost:<port>/api/v3/*`). It can start the daemon bundled
/// inside the app (`Contents/Resources/idfw-daemon`), fall back to a
/// system Python that can import the `~/.claude/skills/idea` package, or
/// simply attach to an already-running instance.
///
/// The real daemon is `python -m idea.cli start <slug>` (FastAPI/uvicorn,
/// loopback, port allocated 4040–4099 and written to
/// `~/.claude/skills/idea/.server-registry.json`) — NOT `idfw start`
/// (that is a Redis orchestrator with no HTTP server).
@MainActor
@Observable
final class DaemonController {

    enum State: Equatable {
        case disconnected
        case starting
        case connecting
        case connected(port: Int)
        case error(String)
    }

    private(set) var state: State = .disconnected
    private(set) var managedBySelf = false
    private let slug = "default"

    private var daemonProcess: Process?
    private var probeTask: Task<Void, Never>?

    var isConnected: Bool {
        if case .connected = state { return true }
        return false
    }

    var port: Int {
        if case .connected(let p) = state { return p }
        return registryPort() ?? 4040
    }

    var baseURL: URL { URL(string: "http://localhost:\(port)")! }

    var displayText: String {
        switch state {
        case .disconnected:      return "Daemon offline"
        case .starting:          return "Starting daemon…"
        case .connecting:        return "Connecting to daemon…"
        case .connected(let p):  return "Daemon · localhost:\(p)\(managedBySelf ? " (managed)" : "")"
        case .error(let m):      return "Daemon error: \(m)"
        }
    }

    // MARK: - Lifecycle

    /// Probe for an existing daemon; if none, start the bundled one.
    func connectOrStart() {
        probeTask?.cancel()
        probeTask = Task { [weak self] in
            guard let self else { return }
            self.state = .connecting
            if await self.probeHealth(retries: 3, delayMs: 300) { return }
            await self.start()
        }
    }

    func start() async {
        guard daemonProcess == nil else { return }
        guard let launch = resolveLaunch() else {
            state = .error("daemon runtime not found (bundle missing & ~/.claude/skills/idea absent)")
            return
        }
        state = .starting
        let proc = Process()
        proc.executableURL = launch.python
        proc.arguments = ["-m", "idea.cli", "start", slug]
        var env = ProcessInfo.processInfo.environment
        env["HOME"] = NSHomeDirectory()
        if let pp = launch.pythonPath { env["PYTHONPATH"] = pp }
        proc.environment = env
        proc.standardOutput = Pipe()
        proc.standardError = Pipe()
        do {
            try proc.run()
            daemonProcess = proc
            managedBySelf = true
        } catch {
            state = .error("spawn failed: \(error.localizedDescription)")
            return
        }
        // Daemon binds + writes the registry within ~1–3s.
        if await probeHealth(retries: 20, delayMs: 500) == false {
            state = .error("daemon did not become healthy")
        }
    }

    func stop() {
        probeTask?.cancel()
        if let proc = daemonProcess, proc.isRunning {
            proc.terminate()
        }
        daemonProcess = nil
        managedBySelf = false
        state = .disconnected
    }

    func reconnect() {
        connectOrStart()
    }

    // MARK: - Health

    @discardableResult
    private func probeHealth(retries: Int, delayMs: Int) async -> Bool {
        for _ in 0..<retries {
            if Task.isCancelled { return false }
            let p = registryPort() ?? 4040
            if let ok = await healthOK(port: p), ok {
                state = .connected(port: p)
                return true
            }
            try? await Task.sleep(nanoseconds: UInt64(delayMs) * 1_000_000)
        }
        return false
    }

    private func healthOK(port: Int) async -> Bool? {
        guard let url = URL(string: "http://localhost:\(port)/api/v3/health") else { return nil }
        var req = URLRequest(url: url)
        req.timeoutInterval = 2
        let cfg = URLSessionConfiguration.ephemeral
        cfg.timeoutIntervalForRequest = 2
        let session = URLSession(configuration: cfg)
        guard let (_, resp) = try? await session.data(for: req),
              let http = resp as? HTTPURLResponse else { return false }
        return (200...299).contains(http.statusCode)
    }

    // MARK: - Port discovery (the daemon writes its real port here)

    private func registryPort() -> Int? {
        let registry = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".claude/skills/idea/.server-registry.json")
        guard let data = try? Data(contentsOf: registry),
              let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
        else { return nil }
        // Registry shape: { "<slug>": { "port": N, ... }, ... } or { "<slug>": N }
        if let entry = obj[slug] as? [String: Any], let p = entry["port"] as? Int { return p }
        if let p = obj[slug] as? Int { return p }
        for value in obj.values {
            if let e = value as? [String: Any], let p = e["port"] as? Int { return p }
        }
        return nil
    }

    // MARK: - Runtime resolution (DRTW: bundled uv venv → system python → none)

    private struct Launch { let python: URL; let pythonPath: String? }

    private func resolveLaunch() -> Launch? {
        let fm = FileManager.default

        // 1. Bundled relocatable venv (built by Scripts/bundle-daemon.sh).
        if let res = Bundle.main.resourceURL {
            let daemonDir = res.appendingPathComponent("idfw-daemon")
            for name in ["venv/bin/python3.12", "venv/bin/python3", "venv/bin/python"] {
                let py = daemonDir.appendingPathComponent(name)
                if fm.isExecutableFile(atPath: py.path) {
                    return Launch(python: py, pythonPath: daemonDir.path)
                }
            }
        }

        // 2. System python that can import the installed /idea skill package.
        let skill = fm.homeDirectoryForCurrentUser.appendingPathComponent(".claude/skills/idea")
        if fm.fileExists(atPath: skill.appendingPathComponent("cli.py").path) {
            for cand in ["/opt/homebrew/bin/python3", "/usr/local/bin/python3", "/usr/bin/python3"]
            where fm.isExecutableFile(atPath: cand) {
                // PYTHONPATH = parent of the `idea` package dir so `import idea` works.
                return Launch(python: URL(fileURLWithPath: cand),
                              pythonPath: skill.deletingLastPathComponent().path)
            }
        }
        return nil
    }
}
