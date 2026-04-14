import SwiftUI

struct ConnectorSetupSheet: View {
    @Environment(\.dismiss) private var dismiss
    @State private var viewModel = ConnectorSetupViewModel()
    @State private var projectName = ""

    var onSave: (String, SourceConnectorConfig) -> Void

    var body: some View {
        VStack(spacing: 0) {
            Form {
                Section("Project") {
                    TextField("Project Name", text: $projectName)
                        .accessibilityIdentifier(AccessibilityIdentifiers.ConnectorSetup.nameField)
                }

                Section("Connector") {
                    Picker("Source", selection: $viewModel.selectedKind) {
                        Text("Local Directory").tag(SourceConnectorConfig.ConnectorKind.local)
                        Text("GitHub Repository").tag(SourceConnectorConfig.ConnectorKind.github)
                    }
                    .pickerStyle(.segmented)
                    .accessibilityIdentifier(AccessibilityIdentifiers.ConnectorSetup.kindPicker)

                    switch viewModel.selectedKind {
                    case .local:
                        TextField("Path", text: $viewModel.localPath)
                            .accessibilityIdentifier(AccessibilityIdentifiers.ConnectorSetup.localPathField)
                    case .github:
                        TextField("GitHub URL", text: $viewModel.githubURL)
                            .accessibilityIdentifier(AccessibilityIdentifiers.ConnectorSetup.githubURLField)
                        TextField("Branch / Ref", text: $viewModel.githubRef)
                        SecureField("Token (optional)", text: $viewModel.token)
                    }
                }

                if let error = viewModel.validationError {
                    Section {
                        Label(error, systemImage: "exclamationmark.triangle")
                            .foregroundStyle(.red)
                    }
                }
            }
            .formStyle(.grouped)

            HStack {
                Button("Cancel") { dismiss() }
                    .keyboardShortcut(.cancelAction)

                Spacer()

                Button("Save") {
                    let config = viewModel.buildConfig(label: projectName)
                    onSave(projectName, config)
                    dismiss()
                }
                .keyboardShortcut(.defaultAction)
                .disabled(projectName.isEmpty || viewModel.isValidating)
                .accessibilityIdentifier(AccessibilityIdentifiers.ConnectorSetup.saveButton)
            }
            .padding()
        }
        .frame(minWidth: 420, minHeight: 340)
        .accessibilityIdentifier(AccessibilityIdentifiers.ConnectorSetup.sheet)
    }
}
