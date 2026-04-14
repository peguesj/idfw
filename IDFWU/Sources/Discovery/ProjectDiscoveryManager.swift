import Foundation
import Observation
import os.log

private let logger = Logger(subsystem: "com.idfw.idfwu", category: "Discovery")

@MainActor
@Observable
final class ProjectDiscoveryManager {
    var projects: [DiscoveredProject] = []
    var isLoading = false
    var activeProviderName: String = "none"
    var lastRefresh: Date?

    /// Optional scan-root store. When set, `refresh()` rebuilds the local
    /// filesystem provider using the store's current roots/depth/markers.
    var scanRootStore: ScanRootStore?

    private let daemonProvider: DaemonProjectProvider
    private let customProviders: [any ProjectProvider]?
    private var autoRefreshTask: Task<Void, Never>?

    init(providers: [any ProjectProvider]? = nil) {
        self.customProviders = providers
        self.daemonProvider = DaemonProjectProvider()
    }

    func refresh() async {
        isLoading = true
        defer { isLoading = false }

        let providers = buildProviders()
        logger.info("Refresh: \(providers.count) providers, store=\(self.scanRootStore != nil)")

        for provider in providers {
            let available = await provider.isAvailable()
            logger.info("Provider \(provider.name): available=\(available)")
            guard available else { continue }
            do {
                let discovered = try await provider.discover()
                logger.info("Provider \(provider.name): discovered \(discovered.count) projects")
                projects = discovered
                activeProviderName = provider.name
                lastRefresh = Date()
                return
            } catch {
                logger.error("Provider \(provider.name) error: \(String(describing: error))")
                continue
            }
        }

        // All providers failed — keep existing data
        logger.warning("All providers failed, keeping \(self.projects.count) existing projects")
        activeProviderName = "none"
    }

    func startAutoRefresh(interval: TimeInterval = 30) {
        stopAutoRefresh()
        autoRefreshTask = Task { [weak self] in
            // Wait one interval before the first auto-refresh cycle so the
            // initial manual refresh() from IDFWUApp.task isn't duplicated.
            try? await Task.sleep(nanoseconds: UInt64(interval * 1_000_000_000))
            while !Task.isCancelled {
                await self?.refresh()
                try? await Task.sleep(nanoseconds: UInt64(interval * 1_000_000_000))
            }
        }
    }

    func stopAutoRefresh() {
        autoRefreshTask?.cancel()
        autoRefreshTask = nil
    }

    // MARK: - Private

    private func buildProviders() -> [any ProjectProvider] {
        if let customProviders { return customProviders }

        let localProvider: LocalFilesystemProvider
        if let store = scanRootStore {
            var roots = store.activeRootURLs
            logger.info("ScanRootStore has \(store.roots.count) roots, \(roots.count) active URLs")
            // Guarantee at least ~/Developer is scanned even if the store is
            // empty (SPM debug builds may have an empty UserDefaults domain).
            if roots.isEmpty {
                let devDir = FileManager.default.homeDirectoryForCurrentUser
                    .appendingPathComponent("Developer")
                roots = [devDir]
                logger.info("Falling back to ~/Developer")
            }
            localProvider = LocalFilesystemProvider(
                scanRoots: roots,
                markers: store.markers,
                maxDepth: store.maxDepth
            )
        } else {
            logger.info("No ScanRootStore set, using default LocalFilesystemProvider")
            localProvider = LocalFilesystemProvider()
        }

        return [daemonProvider, localProvider]
    }
}
