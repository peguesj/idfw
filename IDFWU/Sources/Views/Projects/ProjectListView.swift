import SwiftUI
import SwiftData

struct ProjectListView: View {
    @Environment(\.modelContext) private var modelContext
    @State private var viewModel = ProjectListViewModel()
    @State private var showingAddSheet = false

    var body: some View {
        List(viewModel.projects, id: \.id) { project in
            NavigationLink(value: project) {
                ProjectRowView(project: project)
            }
        }
        .overlay {
            if viewModel.projects.isEmpty && !viewModel.isLoading {
                ContentUnavailableView(
                    "No Projects",
                    systemImage: "folder.badge.plus",
                    description: Text("Add a project to get started.")
                )
            }
        }
        .navigationTitle("Projects")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    showingAddSheet = true
                } label: {
                    Label("Add Project", systemImage: "plus")
                }
                .accessibilityIdentifier(AccessibilityIdentifiers.Projects.addButton)
            }
        }
        .sheet(isPresented: $showingAddSheet) {
            ConnectorSetupSheet { name, config in
                viewModel.addProject(name: name, config: config, context: modelContext)
            }
        }
        .onAppear {
            viewModel.fetch(context: modelContext)
        }
        .accessibilityIdentifier(AccessibilityIdentifiers.Projects.list)
    }
}
