import SwiftUI

struct SchemaDetailView: View {
    let schemaDocument: SchemaDocument
    @State private var viewModel = SchemaDetailViewModel()
    @State private var selectedTab: Tab = .overview

    enum Tab: Hashable {
        case overview, diagrams, gates, rawJSON
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            overviewTab
                .tabItem { Label("Overview", systemImage: "doc.text") }
                .tag(Tab.overview)

            if !viewModel.diagrams.isEmpty {
                diagramsTab
                    .tabItem { Label("Diagrams", systemImage: "chart.bar.doc.horizontal") }
                    .tag(Tab.diagrams)
            }

            if !viewModel.gates.isEmpty {
                gatesTab
                    .tabItem { Label("Gates", systemImage: "checkmark.shield") }
                    .tag(Tab.gates)
            }

            rawJSONTab
                .tabItem { Label("Raw JSON", systemImage: "curlybraces") }
                .tag(Tab.rawJSON)
        }
        .padding()
        .onAppear {
            viewModel.load(from: schemaDocument)
        }
        .accessibilityIdentifier(AccessibilityIdentifiers.SchemaDetail.container)
    }

    @ViewBuilder
    private var overviewTab: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if let doc = viewModel.document {
                    LabeledContent("Type", value: doc.schemaType.displayName)
                    LabeledContent("Doc ID", value: doc.docId)
                    if let title = doc.title {
                        LabeledContent("Title", value: title)
                    }
                    if let desc = doc.payload["description"] as? String {
                        DocumentView(markdown: desc)
                    }
                }
            }
            .padding()
            .liquidGlassCard()
        }
    }

    @ViewBuilder
    private var diagramsTab: some View {
        ScrollView {
            VStack(spacing: 16) {
                ForEach(viewModel.diagrams) { diagram in
                    DiagramView(payload: diagram)
                }
            }
            .padding()
        }
    }

    @ViewBuilder
    private var gatesTab: some View {
        GateView(gates: $viewModel.gates) { gate, status in
            viewModel.markGate(gate, status: status)
        }
    }

    @ViewBuilder
    private var rawJSONTab: some View {
        ScrollView {
            if let prettyJSON = prettyPrintedJSON {
                Text(prettyJSON)
                    .font(.system(.body, design: .monospaced))
                    .textSelection(.enabled)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .liquidGlassCard()
            }
        }
    }

    private var prettyPrintedJSON: String? {
        guard let obj = try? JSONSerialization.jsonObject(with: schemaDocument.jsonPayload),
              let data = try? JSONSerialization.data(withJSONObject: obj, options: [.prettyPrinted, .sortedKeys]) else {
            return nil
        }
        return String(data: data, encoding: .utf8)
    }
}
