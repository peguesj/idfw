import Foundation

enum RevEngClient {
    static func send(projectName: String, projectPath: String) async {
        guard let url = URL(string: "http://localhost:4040/api/v3/state/default") else { return }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload: [String: Any] = [
            "type": "CUSTOM",
            "name": "idea_rev_eng",
            "data": [
                "project_name": projectName,
                "project_path": projectPath,
                "action": "reverse_engineer"
            ]
        ]

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            let (_, response) = try await URLSession.shared.data(for: request)
            if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
                print("[RevEng] Server returned \(http.statusCode)")
            }
        } catch {
            print("[RevEng] Failed: \(error.localizedDescription)")
        }
    }
}
