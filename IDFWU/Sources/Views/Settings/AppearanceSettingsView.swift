import SwiftUI
import AppKit

struct AppearanceSettingsView: View {
    enum AppearanceOption: String, CaseIterable, Identifiable {
        case system, light, dark
        var id: String { rawValue }
        var label: String {
            switch self {
            case .system: "System"
            case .light: "Light"
            case .dark: "Dark"
            }
        }
    }

    @AppStorage("appearance") private var appearanceRaw: String = AppearanceOption.system.rawValue

    @AppStorage("appearance.accent.red") private var accentRed: Double = 0.20
    @AppStorage("appearance.accent.green") private var accentGreen: Double = 0.55
    @AppStorage("appearance.accent.blue") private var accentBlue: Double = 0.95
    @AppStorage("appearance.accent.alpha") private var accentAlpha: Double = 1.0

    private static let defaultAccent = Color(.sRGB, red: 0.20, green: 0.55, blue: 0.95, opacity: 1.0)

    private var appearanceBinding: Binding<AppearanceOption> {
        Binding(
            get: { AppearanceOption(rawValue: appearanceRaw) ?? .system },
            set: { newValue in
                appearanceRaw = newValue.rawValue
                applyAppearance(newValue)
            }
        )
    }

    private var accentBinding: Binding<Color> {
        Binding(
            get: {
                Color(.sRGB, red: accentRed, green: accentGreen, blue: accentBlue, opacity: accentAlpha)
            },
            set: { newColor in
                let ns = NSColor(newColor).usingColorSpace(.sRGB) ?? NSColor(newColor)
                accentRed = Double(ns.redComponent)
                accentGreen = Double(ns.greenComponent)
                accentBlue = Double(ns.blueComponent)
                accentAlpha = Double(ns.alphaComponent)
            }
        )
    }

    var body: some View {
        Form {
            Section("Theme") {
                Picker("Appearance", selection: appearanceBinding) {
                    ForEach(AppearanceOption.allCases) { option in
                        Text(option.label).tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }

            Section("Accent Color") {
                ColorPicker("Accent color", selection: accentBinding, supportsOpacity: true)
                HStack {
                    Text("Preview")
                    Spacer()
                    RoundedRectangle(cornerRadius: 6)
                        .fill(accentBinding.wrappedValue)
                        .frame(width: 60, height: 24)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(.secondary.opacity(0.5), lineWidth: 0.5)
                        )
                }
            }

            Section {
                Button(role: .destructive) {
                    resetDefaults()
                } label: {
                    Label("Reset to Defaults", systemImage: "arrow.counterclockwise")
                }
            }
        }
        .formStyle(.grouped)
        .padding()
        .onAppear {
            applyAppearance(AppearanceOption(rawValue: appearanceRaw) ?? .system)
        }
    }

    private func applyAppearance(_ option: AppearanceOption) {
        switch option {
        case .system:
            NSApp.appearance = nil
        case .light:
            NSApp.appearance = NSAppearance(named: .aqua)
        case .dark:
            NSApp.appearance = NSAppearance(named: .darkAqua)
        }
    }

    private func resetDefaults() {
        appearanceRaw = AppearanceOption.system.rawValue
        accentRed = 0.20
        accentGreen = 0.55
        accentBlue = 0.95
        accentAlpha = 1.0
        applyAppearance(.system)
        _ = Self.defaultAccent
    }
}

#Preview {
    AppearanceSettingsView()
}
