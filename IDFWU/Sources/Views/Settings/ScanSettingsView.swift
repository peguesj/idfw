import SwiftUI

struct ScanSettingsView: View {
    @AppStorage("scan.autoRefreshSeconds") private var autoRefreshSeconds: Double = 30
    @AppStorage("scan.refreshOnFocus") private var refreshOnFocus: Bool = true
    @AppStorage("scan.defaultDepth") private var defaultDepth: Int = 2

    var body: some View {
        Form {
            Section("Auto Refresh") {
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text("Interval")
                        Spacer()
                        Text("\(Int(autoRefreshSeconds))s")
                            .foregroundStyle(.secondary)
                            .monospacedDigit()
                    }
                    Slider(value: $autoRefreshSeconds, in: 15...300, step: 5) {
                        Text("Interval")
                    } minimumValueLabel: {
                        Text("15s").font(.caption2).foregroundStyle(.secondary)
                    } maximumValueLabel: {
                        Text("5m").font(.caption2).foregroundStyle(.secondary)
                    }
                }

                Toggle("Refresh scan on app focus", isOn: $refreshOnFocus)
            }

            Section("Default Depth") {
                Stepper(
                    "Default scan depth: \(defaultDepth)",
                    value: $defaultDepth,
                    in: 1...5
                )
                Text("Per-root depth overrides win when set. This global default applies to any root that does not specify its own depth.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .formStyle(.grouped)
        .padding()
    }
}

#Preview {
    ScanSettingsView()
}
