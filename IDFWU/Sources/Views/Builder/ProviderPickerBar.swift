import SwiftUI

/// Provider + model selector with live detection status dots. Only installed
/// CLIs are selectable; absent ones show a hint.
struct ProviderPickerBar: View {
    @Environment(ProviderRegistry.self) private var registry
    @Bindable var orchestrator: BuilderOrchestrator

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "cpu")
                .foregroundStyle(.secondary)

            Picker("Provider", selection: $orchestrator.selectedProvider) {
                ForEach(ProviderID.allCases) { id in
                    let det = registry.detection(id)
                    Label {
                        Text(id.displayName)
                    } icon: {
                        Image(systemName: det.available
                              ? "circle.fill" : "circle")
                            .foregroundStyle(det.available ? .green : .secondary)
                    }
                    .tag(id)
                }
            }
            .pickerStyle(.menu)
            .fixedSize()

            Divider().frame(height: 16)

            Picker("Model", selection: $orchestrator.selectedModel) {
                ForEach(modelOptions, id: \.self) { model in
                    Text(model).tag(model)
                }
            }
            .pickerStyle(.menu)
            .fixedSize()

            Spacer()

            detectionStatus
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(.bar)
    }

    private var modelOptions: [String] {
        registry.provider(orchestrator.selectedProvider)?.capabilities().models
            ?? ["default"]
    }

    @ViewBuilder
    private var detectionStatus: some View {
        let det = registry.detection(orchestrator.selectedProvider)
        if registry.isDetecting {
            HStack(spacing: 4) {
                ProgressView().controlSize(.small)
                Text("Detecting…").font(.caption).foregroundStyle(.secondary)
            }
        } else if det.available {
            Text(det.version ?? "installed")
                .font(.caption.monospaced())
                .foregroundStyle(.secondary)
        } else {
            Text(det.detail ?? "not installed")
                .font(.caption)
                .foregroundStyle(.orange)
        }
    }
}
