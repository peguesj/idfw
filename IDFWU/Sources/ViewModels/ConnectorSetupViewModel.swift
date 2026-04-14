import Foundation
import Observation

@Observable
final class ConnectorSetupViewModel {
    var selectedKind: SourceConnectorConfig.ConnectorKind = .local
    var localPath: String = ""
    var githubURL: String = ""
    var githubRef: String = "main"
    var token: String = ""
    var isValidating = false
    var validationError: String?

    func validate() async {
        isValidating = true
        validationError = nil
        defer { isValidating = false }

        switch selectedKind {
        case .local:
            let url = URL(fileURLWithPath: localPath)
            var isDir: ObjCBool = false
            guard FileManager.default.fileExists(atPath: url.path, isDirectory: &isDir), isDir.boolValue else {
                validationError = "Path does not exist or is not a directory."
                return
            }
        case .github:
            guard let url = URL(string: githubURL),
                  url.host?.contains("github") == true else {
                validationError = "Invalid GitHub repository URL."
                return
            }
        }
    }

    func buildConfig(label: String) -> SourceConnectorConfig {
        SourceConnectorConfig(
            kind: selectedKind,
            localPath: selectedKind == .local ? URL(fileURLWithPath: localPath) : nil,
            githubRepoURL: selectedKind == .github ? URL(string: githubURL) : nil,
            githubRef: githubRef,
            authToken: token.isEmpty ? nil : token
        )
    }
}
