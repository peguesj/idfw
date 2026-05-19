import SwiftUI

struct ConnectorsSettingsView: View {
    enum TestStatus: Equatable {
        case idle
        case testing
        case success
        case failure(String)
    }

    @AppStorage("connectors.apmUrl") private var apmUrl: String = "http://localhost:3032"

    @State private var anthropicKey: String = ""
    @State private var anthropicKeyStatus: String = ""
    @State private var anthropicTestStatus: TestStatus = .idle

    @State private var githubToken: String = ""
    @State private var githubTokenStatus: String = ""
    @State private var testStatus: TestStatus = .idle

    private let anthropicKeychainKey = "anthropic.api_key"
    private let githubKey = "github.personal_access_token"

    var body: some View {
        Form {
            Section("Anthropic") {
                SecureField("API Key (sk-ant-api03-…)", text: $anthropicKey)
                    .textFieldStyle(.roundedBorder)

                HStack {
                    Button {
                        saveAnthropicKey()
                    } label: {
                        Label("Save Key", systemImage: "key.fill")
                    }
                    .disabled(anthropicKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                    Button {
                        testAnthropicKey()
                    } label: {
                        Label("Test", systemImage: "network")
                    }
                    .disabled(anthropicTestStatus == .testing ||
                              anthropicKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)

                    Button(role: .destructive) {
                        clearAnthropicKey()
                    } label: {
                        Label("Clear", systemImage: "trash")
                    }

                    Spacer()

                    switch anthropicTestStatus {
                    case .idle:
                        if !anthropicKeyStatus.isEmpty {
                            Text(anthropicKeyStatus)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    case .testing:
                        HStack(spacing: 4) {
                            ProgressView().controlSize(.small)
                            Text("Testing…").font(.caption).foregroundStyle(.secondary)
                        }
                    case .success:
                        HStack(spacing: 4) {
                            Image(systemName: "checkmark.circle.fill").foregroundStyle(.green)
                            Text("Valid key").font(.caption).foregroundStyle(.green)
                        }
                    case .failure(let msg):
                        HStack(spacing: 4) {
                            Image(systemName: "xmark.circle.fill").foregroundStyle(.red)
                            Text(msg).font(.caption).foregroundStyle(.red).lineLimit(1)
                        }
                    }
                }

                Text("Your key is stored in the macOS Keychain and never leaves this device. Generate one at console.anthropic.com.")
                    .font(.caption)
                    .foregroundStyle(.tertiary)
            }

            Section("GitHub") {
                SecureField("Personal Access Token", text: $githubToken)
                    .textFieldStyle(.roundedBorder)

                HStack {
                    Button {
                        saveGithubToken()
                    } label: {
                        Label("Save Token", systemImage: "key.fill")
                    }

                    Button(role: .destructive) {
                        clearGithubToken()
                    } label: {
                        Label("Clear", systemImage: "trash")
                    }

                    Spacer()

                    if !githubTokenStatus.isEmpty {
                        Text(githubTokenStatus)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Section("APM") {
                TextField("APM URL", text: $apmUrl)
                    .textFieldStyle(.roundedBorder)

                HStack {
                    Button {
                        testAPMConnection()
                    } label: {
                        Label("Test Connection", systemImage: "network")
                    }
                    .disabled(testStatus == .testing)

                    statusView
                }
            }
        }
        .formStyle(.grouped)
        .padding()
        .task {
            await loadAnthropicKey()
            await loadGithubToken()
        }
    }

    @ViewBuilder
    private var statusView: some View {
        switch testStatus {
        case .idle:
            EmptyView()
        case .testing:
            HStack(spacing: 4) {
                ProgressView().controlSize(.small)
                Text("Testing...").font(.caption).foregroundStyle(.secondary)
            }
        case .success:
            HStack(spacing: 4) {
                Image(systemName: "checkmark.circle.fill").foregroundStyle(.green)
                Text("OK").font(.caption).foregroundStyle(.green)
            }
        case .failure(let msg):
            HStack(spacing: 4) {
                Image(systemName: "xmark.circle.fill").foregroundStyle(.red)
                Text(msg).font(.caption).foregroundStyle(.red).lineLimit(1)
            }
        }
    }

    // MARK: - Anthropic

    private func loadAnthropicKey() async {
        if let value = try? await KeychainHelper.shared.get(key: anthropicKeychainKey), !value.isEmpty {
            anthropicKey = value
            anthropicKeyStatus = "Loaded"
        }
    }

    private func saveAnthropicKey() {
        let value = anthropicKey.trimmingCharacters(in: .whitespacesAndNewlines)
        Task {
            do {
                try await KeychainHelper.shared.set(value, key: anthropicKeychainKey)
                await MainActor.run {
                    anthropicKeyStatus = "Saved"
                    anthropicTestStatus = .idle
                }
            } catch {
                await MainActor.run { anthropicKeyStatus = "Save failed" }
            }
        }
    }

    private func clearAnthropicKey() {
        Task {
            try? await KeychainHelper.shared.delete(key: anthropicKeychainKey)
            await MainActor.run {
                anthropicKey = ""
                anthropicKeyStatus = "Cleared"
                anthropicTestStatus = .idle
            }
        }
    }

    private func testAnthropicKey() {
        let key = anthropicKey.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !key.isEmpty else { return }
        anthropicTestStatus = .testing
        Task {
            guard let url = URL(string: "https://api.anthropic.com/v1/models") else {
                await MainActor.run { anthropicTestStatus = .failure("Invalid URL") }
                return
            }
            var req = URLRequest(url: url)
            req.setValue(key, forHTTPHeaderField: "x-api-key")
            req.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
            req.timeoutInterval = 10
            do {
                let (_, response) = try await URLSession.shared.data(for: req)
                if let http = response as? HTTPURLResponse {
                    if http.statusCode == 200 {
                        await MainActor.run { anthropicTestStatus = .success }
                    } else if http.statusCode == 401 {
                        await MainActor.run { anthropicTestStatus = .failure("Invalid key (401)") }
                    } else {
                        await MainActor.run { anthropicTestStatus = .failure("HTTP \(http.statusCode)") }
                    }
                }
            } catch {
                await MainActor.run { anthropicTestStatus = .failure(error.localizedDescription) }
            }
        }
    }

    // MARK: - GitHub

    private func loadGithubToken() async {
        do {
            if let value = try await KeychainHelper.shared.get(key: githubKey) {
                githubToken = value
            }
        } catch {
            // Keychain read failed; leave field blank.
        }
    }

    private func saveGithubToken() {
        let value = githubToken
        Task {
            do {
                try await KeychainHelper.shared.set(value, key: githubKey)
                await MainActor.run { githubTokenStatus = "Saved" }
            } catch {
                await MainActor.run { githubTokenStatus = "Save failed" }
            }
        }
    }

    private func clearGithubToken() {
        Task {
            try? await KeychainHelper.shared.delete(key: githubKey)
            await MainActor.run {
                githubToken = ""
                githubTokenStatus = "Cleared"
            }
        }
    }

    private func testAPMConnection() {
        testStatus = .testing
        let base = apmUrl.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let url = URL(string: base + "/health") else {
            testStatus = .failure("Invalid URL")
            return
        }

        Task {
            var req = URLRequest(url: url)
            req.timeoutInterval = 5
            do {
                let (_, response) = try await URLSession.shared.data(for: req)
                if let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) {
                    await MainActor.run { testStatus = .success }
                } else if let http = response as? HTTPURLResponse {
                    await MainActor.run { testStatus = .failure("HTTP \(http.statusCode)") }
                } else {
                    await MainActor.run { testStatus = .failure("No response") }
                }
            } catch {
                await MainActor.run { testStatus = .failure(error.localizedDescription) }
            }
        }
    }
}

#Preview {
    ConnectorsSettingsView()
}
