import SwiftUI

struct DetailView: View {
    let document: ProjectDocument?

    var body: some View {
        if let document {
            DocumentContentView(document: document)
        } else {
            EmptyStateView(
                symbol: "doc.text.magnifyingglass",
                title: "No Artifact Selected",
                subtitle: "Choose an IDEA artifact from the lifecycle column to view its contents.",
                actionTitle: nil,
                action: nil
            )
        }
    }
}

// MARK: - Content dispatch

private enum RenderMode {
    case markdown(AttributedString)
    case mermaid(String)
    case plantUML(String)
    case json(String)                // pretty-printed JSON
    case plainText(String)
    case binary(String)              // message to display when file is not text
    case loading
    case error(String)
}

private struct DocumentContentView: View {
    let document: ProjectDocument

    @State private var mode: RenderMode = .loading

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            Divider()
            content
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .task(id: document.id) {
            await loadContent()
        }
    }

    // MARK: Header

    private var header: some View {
        HStack(spacing: 8) {
            // Phase badge
            ZStack {
                RoundedRectangle(cornerRadius: 5)
                    .fill(document.phase.accentColor.opacity(0.18))
                    .frame(width: 22, height: 22)
                Text(document.phase.letter)
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(document.phase.accentColor)
            }

            Image(systemName: iconForType(document.type))
                .foregroundStyle(.secondary)

            VStack(alignment: .leading, spacing: 1) {
                Text(document.name)
                    .font(.headline)
                    .lineLimit(1)
                Text("\(document.phase.title) · \(document.type.rawValue)")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Button {
                NSWorkspace.shared.selectFile(document.path, inFileViewerRootedAtPath: "")
            } label: {
                Label("Reveal", systemImage: "folder")
                    .labelStyle(.iconOnly)
            }
            .buttonStyle(.borderless)
            .help("Reveal in Finder")
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
    }

    // MARK: Content dispatch

    @ViewBuilder
    private var content: some View {
        switch mode {
        case .loading:
            VStack {
                Spacer()
                ProgressView("Loading…")
                Spacer()
            }
            .frame(maxWidth: .infinity)

        case .error(let message):
            errorState(message)

        case .binary(let message):
            errorState(message)

        case .markdown(let attributed):
            ScrollView(.vertical) {
                Text(attributed)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(20)
            }

        case .mermaid(let source):
            MermaidWebView(source: source, theme: .default_)
                .frame(maxWidth: .infinity, maxHeight: .infinity)

        case .plantUML(let source):
            // No PlantUML renderer bundled yet — fall back to monospace source
            // with a small hint so users know why it isn't rendered.
            VStack(alignment: .leading, spacing: 0) {
                HStack(spacing: 6) {
                    Image(systemName: "info.circle")
                    Text("PlantUML source (visual rendering not bundled)")
                }
                .font(.caption)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                Divider()
                ScrollView(.vertical) {
                    Text(source)
                        .font(.system(.body, design: .monospaced))
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(16)
                }
            }

        case .json(let pretty):
            ScrollView([.vertical, .horizontal]) {
                Text(pretty)
                    .font(.system(.body, design: .monospaced))
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(16)
            }

        case .plainText(let text):
            ScrollView([.vertical, .horizontal]) {
                Text(text)
                    .font(.system(.body, design: .monospaced))
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(16)
            }
        }
    }

    @ViewBuilder
    private func errorState(_ message: String) -> some View {
        VStack(spacing: 8) {
            Spacer()
            Image(systemName: "exclamationmark.triangle")
                .font(.title)
                .foregroundStyle(.secondary)
            Text(message)
                .font(.callout)
                .foregroundStyle(.secondary)
            Spacer()
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: Loading

    private func loadContent() async {
        mode = .loading

        let path = document.path
        let name = document.name.lowercased()

        let raw: Data
        do {
            raw = try Data(contentsOf: URL(fileURLWithPath: path))
        } catch {
            mode = .error("Could not read file: \(error.localizedDescription)")
            return
        }

        guard let text = String(data: raw, encoding: .utf8) else {
            mode = .binary("Binary file (\(formattedSize(document.size)))")
            return
        }

        // Dispatch based on extension.
        if name.hasSuffix(".md") || name.hasSuffix(".markdown") {
            let attributed = renderMarkdown(text)
            mode = .markdown(attributed)
            return
        }

        if name.hasSuffix(".mmd") || name.hasSuffix(".mermaid") {
            mode = .mermaid(text)
            return
        }

        if name.hasSuffix(".puml") || name.hasSuffix(".plantuml") {
            mode = .plantUML(text)
            return
        }

        if name.hasSuffix(".json") || name.hasSuffix(".jsonc") {
            mode = .json(prettyPrintJSON(text) ?? text)
            return
        }

        mode = .plainText(text)
    }

    // MARK: Renderers

    /// Render a markdown string into an AttributedString using Foundation's
    /// built-in parser (`.full` interpretation preserves headings, lists,
    /// emphasis, and code spans).
    private func renderMarkdown(_ source: String) -> AttributedString {
        let options = AttributedString.MarkdownParsingOptions(
            allowsExtendedAttributes: true,
            interpretedSyntax: .full,
            failurePolicy: .returnPartiallyParsedIfPossible
        )
        if let attributed = try? AttributedString(markdown: source, options: options) {
            return attributed
        }
        return AttributedString(source)
    }

    /// Pretty-print a JSON/JSONC string. Strips single-line comments before
    /// parsing so IDFW JSONC files (which use `// ...`) render cleanly.
    private func prettyPrintJSON(_ source: String) -> String? {
        let stripped = source
            .components(separatedBy: "\n")
            .map { line -> String in
                if let range = line.range(of: "//") {
                    // Leave `://` (URLs) alone — only strip comments that start
                    // at whitespace / start-of-line.
                    let prefix = line[line.startIndex..<range.lowerBound]
                    if prefix.trimmingCharacters(in: .whitespaces).isEmpty
                        || !prefix.hasSuffix(":") {
                        return String(prefix)
                    }
                }
                return line
            }
            .joined(separator: "\n")

        guard let data = stripped.data(using: .utf8),
              let object = try? JSONSerialization.jsonObject(with: data, options: [.fragmentsAllowed]),
              let pretty = try? JSONSerialization.data(
                withJSONObject: object,
                options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
              ),
              let result = String(data: pretty, encoding: .utf8)
        else {
            return nil
        }
        return result
    }

    private func iconForType(_ type: ProjectDocumentType) -> String {
        switch type {
        case .schema:  "doc.badge.gearshape"
        case .force:   "shield.lefthalf.filled"
        case .config:  "gearshape"
        case .doc:     "doc.text"
        case .diagram: "chart.bar.doc.horizontal"
        case .idea:    "sparkles"
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
