import SwiftUI
import WebKit

struct MermaidWebView: NSViewRepresentable {
    let source: String
    let theme: DiagramPayload.MermaidTheme

    func makeNSView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        let handler = context.coordinator
        config.userContentController.add(handler, name: "svgCallback")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = handler
        context.coordinator.webView = webView

        if let htmlURL = Bundle.main.url(forResource: "mermaid-renderer", withExtension: "html") {
            webView.loadFileURL(htmlURL, allowingReadAccessTo: htmlURL.deletingLastPathComponent())
        }
        return webView
    }

    func updateNSView(_ webView: WKWebView, context: Context) {
        context.coordinator.pendingSource = source
        context.coordinator.pendingTheme = theme.rawValue
        context.coordinator.renderIfReady()
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    final class Coordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
        weak var webView: WKWebView?
        var pendingSource: String?
        var pendingTheme: String?
        private var isLoaded = false

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            isLoaded = true
            renderIfReady()
        }

        func renderIfReady() {
            guard isLoaded, let source = pendingSource, let theme = pendingTheme else { return }
            pendingSource = nil
            pendingTheme = nil
            render(source: source, theme: theme)
        }

        func render(source: String, theme: String) {
            let escaped = source
                .replacingOccurrences(of: "\\", with: "\\\\")
                .replacingOccurrences(of: "`", with: "\\`")
                .replacingOccurrences(of: "\n", with: "\\n")
            let js = "renderMermaid(`\(escaped)`, `\(theme)`);"
            webView?.evaluateJavaScript(js)
        }

        func userContentController(
            _ userContentController: WKUserContentController,
            didReceive message: WKScriptMessage
        ) {
            guard message.name == "svgCallback", let svg = message.body as? String else { return }
            _ = svg // SVG received; parent can observe via NotificationCenter if needed
        }
    }
}
