import SwiftUI

struct DiagramView: View {
    let payload: DiagramPayload
    @State private var viewModel = DiagramViewModel()
    @State private var zoomScale: CGFloat = 1.0

    var body: some View {
        VStack(spacing: 0) {
            toolbar

            Group {
                switch viewModel.renderState {
                case .idle:
                    ContentUnavailableView("Diagram Not Rendered", systemImage: "chart.bar.doc.horizontal")
                case .rendering:
                    ProgressView("Rendering...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                case .rendered:
                    MermaidWebView(source: payload.mermaidSource, theme: payload.theme)
                        .scaleEffect(zoomScale)
                case .failed(let message):
                    ContentUnavailableView {
                        Label("Render Failed", systemImage: "exclamationmark.triangle")
                    } description: {
                        Text(message)
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .liquidGlassCard()
        }
        .onAppear {
            viewModel.payload = payload
        }
        .accessibilityIdentifier(AccessibilityIdentifiers.Diagram.container)
    }

    private var toolbar: some View {
        HStack {
            if let title = payload.title {
                Text(title).font(.headline)
            }
            Spacer()
            Button { zoomScale = max(0.25, zoomScale - 0.25) } label: {
                Image(systemName: "minus.magnifyingglass")
            }
            Button { zoomScale = min(4.0, zoomScale + 0.25) } label: {
                Image(systemName: "plus.magnifyingglass")
            }
            Button {
                exportSVG()
            } label: {
                Image(systemName: "square.and.arrow.up")
            }
            .accessibilityIdentifier(AccessibilityIdentifiers.Diagram.exportButton)
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }

    private func exportSVG() {
        guard case .rendered(let svg) = viewModel.renderState else { return }
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.svg]
        panel.nameFieldStringValue = (payload.title ?? "diagram") + ".svg"
        if panel.runModal() == .OK, let url = panel.url {
            try? svg.write(to: url, atomically: true, encoding: .utf8)
        }
    }
}
