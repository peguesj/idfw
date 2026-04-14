import Foundation
import Observation

enum DiagramRenderState: Equatable {
    case idle
    case rendering
    case rendered(String)
    case failed(String)

    static func == (lhs: DiagramRenderState, rhs: DiagramRenderState) -> Bool {
        switch (lhs, rhs) {
        case (.idle, .idle), (.rendering, .rendering): return true
        case let (.rendered(a), .rendered(b)): return a == b
        case let (.failed(a), .failed(b)): return a == b
        default: return false
        }
    }
}

@Observable
final class DiagramViewModel {
    var payload: DiagramPayload?
    var renderState: DiagramRenderState = .idle

    func render(evaluator: @escaping (String, DiagramPayload.MermaidTheme) async throws -> String) async {
        guard let payload else { return }
        renderState = .rendering
        do {
            let svg = try await evaluator(payload.mermaidSource, payload.theme)
            renderState = .rendered(svg)
        } catch {
            renderState = .failed(error.localizedDescription)
        }
    }
}
