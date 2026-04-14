import SwiftUI
import AppKit

extension Color {
    /// Returns true if the contrast ratio against the given background meets WCAG AA (4.5:1 for normal text).
    func meetsWCAGAA(against background: Color) -> Bool {
        contrastRatio(with: background) >= 4.5
    }

    /// Returns true if the contrast ratio meets WCAG AAA (7:1 for normal text).
    func meetsWCAGAAA(against background: Color) -> Bool {
        contrastRatio(with: background) >= 7.0
    }

    /// Picks either white or black for maximum contrast against this color.
    func accessibleForeground() -> Color {
        luminance() > 0.179 ? .black : .white
    }
}
