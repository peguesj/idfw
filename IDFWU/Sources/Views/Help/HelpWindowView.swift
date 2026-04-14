import SwiftUI

struct HelpWindowView: View {
    @State private var viewModel = HelpViewModel()

    var body: some View {
        NavigationSplitView {
            List(HelpSection.allCases, selection: Binding(
                get: { viewModel.selected },
                set: { newValue in
                    if let newValue {
                        viewModel.selected = newValue
                    }
                }
            )) { section in
                Label(section.displayName, systemImage: section.systemImage)
                    .tag(section)
            }
            .navigationTitle("Help")
            .frame(minWidth: 220)
        } detail: {
            ScrollView {
                Text(viewModel.content)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(24)
            }
            .navigationTitle(viewModel.selected.displayName)
        }
        .frame(minWidth: 780, minHeight: 540)
        .task {
            viewModel.load()
        }
    }
}
