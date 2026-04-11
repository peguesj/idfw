import SwiftUI

struct DetailView: View {
    let document: ProjectDocument?

    var body: some View {
        if let document {
            DocumentContentView(document: document)
        } else {
            EmptyStateView(
                symbol: "doc.text.magnifyingglass",
                title: "No Document Selected",
                subtitle: "Choose a document from the list to view its contents.",
                actionTitle: nil,
                action: nil
            )
        }
    }
}

// MARK: - Document Content View

private struct DocumentContentView: View {
    let document: ProjectDocument

    @State private var content: String = ""
    @State private var isLoading = true
    @State private var loadError: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                Image(systemName: iconForType(document.type))
                    .foregroundStyle(.secondary)
                Text(document.name)
                    .font(.headline)
                Spacer()
                Text(document.type.rawValue)
                    .font(.caption)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(.quaternary)
                    .clipShape(RoundedRectangle(cornerRadius: 4))
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)

            Divider()

            // Content
            if isLoading {
                Spacer()
                ProgressView("Loading...")
                    .frame(maxWidth: .infinity)
                Spacer()
            } else if let loadError {
                Spacer()
                VStack(spacing: 8) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.title)
                        .foregroundStyle(.secondary)
                    Text(loadError)
                        .font(.callout)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity)
                Spacer()
            } else {
                ScrollView(.vertical) {
                    Text(content)
                        .font(.system(.body, design: .monospaced))
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(16)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .task(id: document.id) {
            await loadContent()
        }
    }

    private func loadContent() async {
        isLoading = true
        loadError = nil

        do {
            let data = try Data(contentsOf: URL(fileURLWithPath: document.path))
            if let text = String(data: data, encoding: .utf8) {
                content = text
            } else {
                loadError = "Binary file (\(formattedSize(document.size)))"
            }
        } catch {
            loadError = "Could not read file: \(error.localizedDescription)"
        }

        isLoading = false
    }

    private func iconForType(_ type: ProjectDocumentType) -> String {
        switch type {
        case .schema: "doc.badge.gearshape"
        case .force: "shield.lefthalf.filled"
        case .config: "gearshape"
        case .doc: "doc.text"
        }
    }

    private func formattedSize(_ bytes: Int64) -> String {
        if bytes < 1024 { return "\(bytes) B" }
        if bytes < 1024 * 1024 { return "\(bytes / 1024) KB" }
        return String(format: "%.1f MB", Double(bytes) / 1_048_576)
    }
}

#Preview {
    DetailView(document: nil)
}

#Preview("With Document") {
    DetailView(document: ProjectDocument(
        id: UUID(),
        name: "test.schema.json",
        path: "/tmp/test.json",
        type: .schema,
        size: 1234,
        modifiedDate: Date()
    ))
}
