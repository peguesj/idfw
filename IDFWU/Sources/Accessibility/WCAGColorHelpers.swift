import SwiftUI
import AppKit

extension Color {
    /// Relative luminance per WCAG 2.1 definition.
    func luminance() -> CGFloat {
        let nsColor = NSColor(self).usingColorSpace(.sRGB) ?? NSColor(self)
        let r = linearize(nsColor.redComponent)
        let g = linearize(nsColor.greenComponent)
        let b = linearize(nsColor.blueComponent)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    }

    /// WCAG contrast ratio between two colors (range 1...21).
    func contrastRatio(with other: Color) -> CGFloat {
        let l1 = luminance()
        let l2 = other.luminance()
        let lighter = max(l1, l2)
        let darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
    }

    private func linearize(_ component: CGFloat) -> CGFloat {
        component <= 0.04045
            ? component / 12.92
            : pow((component + 0.055) / 1.055, 2.4)
    }
}
