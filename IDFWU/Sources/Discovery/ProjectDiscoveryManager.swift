import Foundation
import Observation

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

        for provider in providers {
            guard await provider.isAvailable() else { continue }
            do {
                let discovered = try await provider.discover()
                projects = discovered
                activeProviderName = provider.name
                lastRefresh = Date()
                return
            } catch {
                continue
            }
        }

        // All providers failed — keep existing data
        activeProviderName = "none"
    }

    func startAutoRefresh(interval: TimeInterval = 30) {
        stopAutoRefresh()
        autoRefreshTask = Task { [weak self] in
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
            localProvider = LocalFilesystemProvider(
                scanRoots: store.activeRootURLs,
                markers: store.markers,
                maxDepth: store.maxDepth
            )
        } else {
            localProvider = LocalFilesystemProvider()
        }

        return [daemonProvider, localProvider]
    }
}
