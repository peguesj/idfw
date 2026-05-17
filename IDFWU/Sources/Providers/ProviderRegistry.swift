import Foundation
import Observation

/// App-wide registry of AI provider CLIs. Detects which are installed,
/// caches detections (5s TTL, mirroring open-design), and resolves a
/// provider driver by id. Injected into the SwiftUI environment.
@MainActor
@Observable
final class ProviderRegistry {
    private let providers: [ProviderID: any AIProvider] = [
        .claude:    ClaudeProvider(),
        .codex:     CodexProvider(),
        .gemini:    GeminiProvider(),
        .ghCopilot: GitHubCopilotProvider()
    ]

    /// Latest detection result per provider, surfaced to the UI.
    private(set) var detections: [ProviderID: ProviderDetection] = [:]
    private(set) var isDetecting = false
    private var lastDetectAt: Date?
    private let cacheTTL: TimeInterval = 5

    func provider(_ id: ProviderID) -> (any AIProvider)? { providers[id] }

    var availableProviders: [ProviderID] {
        ProviderID.allCases.filter { detections[$0]?.available == true }
    }

    func detection(_ id: ProviderID) -> ProviderDetection {
        detections[id] ?? .unavailable(id, detail: "not yet probed")
    }

    /// Probe all providers concurrently. No-op if probed within the TTL
    /// unless `force` is set.
    func refreshDetections(force: Bool = false) async {
        if !force, let last = lastDetectAt, Date().timeIntervalSince(last) < cacheTTL {
            return
        }
        isDetecting = true
        defer { isDetecting = false }

        let probed = await withTaskGroup(of: ProviderDetection.self) { group in
            for (_, provider) in providers {
                group.addTask { await provider.detect() }
            }
            var result: [ProviderDetection] = []
            for await detection in group { result.append(detection) }
            return result
        }

        var map: [ProviderID: ProviderDetection] = [:]
        for detection in probed { map[detection.id] = detection }
        detections = map
        lastDetectAt = Date()
    }

    /// First installed provider in canonical preference order, if any.
    var defaultProvider: ProviderID? {
        [.claude, .codex, .gemini, .ghCopilot].first { detections[$0]?.available == true }
    }
}
