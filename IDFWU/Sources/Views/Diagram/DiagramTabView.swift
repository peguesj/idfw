import SwiftUI

/// Unified diagram surface with a Code | Preview | Split pill, used for
/// mermaid, PlantUML, and WebSequenceDiagrams. The pill is a native
/// segmented `Picker` (DRTW: built-in control, no custom widget).
struct DiagramTabView: View {
    enum Kind { case mermaid, plantUML }   // .wsd routes to .plantUML

    enum Tab: String, CaseIterable, Identifiable {
        case code = "Code", preview = "Preview", split = "Split"
        var id: String { rawValue }
        var symbol: String {
            switch self {
            case .code:    return "chevron.left.forwardslash.chevron.right"
            case .preview: return "eye"
            case .split:   return "rectangle.split.2x1"
            }
        }
    }

    let source: String
    let kind: Kind

    @State private var tab: Tab = .preview
    @State private var svg: String?
    @State private var renderError: String?
    @State private var isRendering = false
    private let renderer = PlantUMLRenderer()

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Picker("", selection: $tab) {
                    ForEach(Tab.allCases) { t in
                        Label(t.rawValue, systemImage: t.symbol).tag(t)
                    }
                }
                .pickerStyle(.segmented)
                .labelsHidden()
                .fixedSize()
                Spacer()
                if isRendering { ProgressView().controlSize(.small) }
            }
            .padding(8)

            Divider()

            Group {
                switch tab {
                case .code:    codePane
                case .preview: previewPane
                case .split:   HSplitView { codePane; previewPane }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .task(id: source) { await renderIfNeeded() }
    }

    private var codePane: some View {
        ScrollView([.vertical, .horizontal]) {
            Text(source)
                .font(.system(.body, design: .monospaced))
                .textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(16)
        }
    }

    @ViewBuilder
    private var previewPane: some View {
        switch kind {
        case .mermaid:
            MermaidWebView(source: source, theme: .default_)
        case .plantUML:
            if let svg {
                SVGWebView(svg: svg)
            } else if let renderError {
                diagramError(renderError)
            } else {
                VStack { Spacer(); ProgressView("Rendering…"); Spacer() }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
    }

    private func diagramError(_ message: String) -> some View {
        VStack(spacing: 8) {
            Spacer()
            Image(systemName: "exclamationmark.triangle")
                .font(.title).foregroundStyle(.secondary)
            Text(message)
                .font(.callout).foregroundStyle(.secondary)
                .multilineTextAlignment(.center).padding(.horizontal, 24)
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func renderIfNeeded() async {
        guard kind == .plantUML else { return }
        isRendering = true
        defer { isRendering = false }
        do {
            svg = try await renderer.renderSVG(source: source)
            renderError = nil
        } catch {
            renderError = error.localizedDescription
            svg = nil
        }
    }
}
