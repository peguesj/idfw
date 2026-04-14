import AppKit
import Foundation

@MainActor
final class AboutPanelController {
    static let shared = AboutPanelController()

    private init() {}

    static func show() {
        shared.present()
    }

    private func present() {
        let shortVersion = (Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String) ?? "1.0"
        let buildNumber = (Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String) ?? "1"

        let options: [NSApplication.AboutPanelOptionKey: Any] = [
            .applicationName: "IDFWU",
            .applicationVersion: shortVersion,
            .version: buildNumber,
            .credits: Self.loadCredits(),
            NSApplication.AboutPanelOptionKey(rawValue: "Copyright"): "\u{00A9} 2026 Pegues Innovations"
        ]

        NSApp.orderFrontStandardAboutPanel(options: options)
    }

    private static func loadCredits() -> NSAttributedString {
        if let url = Bundle.main.url(forResource: "Credits", withExtension: "rtf"),
           let data = try? Data(contentsOf: url),
           let attributed = try? NSAttributedString(
               data: data,
               options: [.documentType: NSAttributedString.DocumentType.rtf],
               documentAttributes: nil
           ) {
            return attributed
        }
        return NSAttributedString(string: "IDFW Project Manager\nPegues Innovations")
    }
}
