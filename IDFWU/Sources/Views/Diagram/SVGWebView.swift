import SwiftUI
import WebKit

/// Hosts a complete SVG string in a `WKWebView` via `loadHTMLString`.
/// Reuses the `MermaidWebView` NSViewRepresentable/Coordinator idiom but
/// without a bundled HTML asset (PlantUML already emits a standalone SVG),
/// which also sidesteps the missing-`mermaid-renderer.html` resource bug.
struct SVGWebView: NSViewRepresentable {
    let svg: String

    func makeNSView(context: Context) -> WKWebView {
        let webView = WKWebView(frame: .zero, configuration: WKWebViewConfiguration())
        webView.navigationDelegate = context.coordinator
        webView.setValue(false, forKey: "drawsBackground")
        return webView
    }

    func updateNSView(_ webView: WKWebView, context: Context) {
        webView.loadHTMLString(Self.wrap(svg), baseURL: nil)
    }

    func makeCoordinator() -> Coordinator { Coordinator() }
    final class Coordinator: NSObject, WKNavigationDelegate {}

    private static func wrap(_ svg: String) -> String {
        """
        <!doctype html><html><head><meta charset="utf-8">
        <style>
          html,body{margin:0;height:100%;background:transparent}
          body{display:flex;align-items:center;justify-content:center;overflow:auto}
          svg{max-width:100%;height:auto}
        </style></head>
        <body>\(svg)</body></html>
        """
    }
}
