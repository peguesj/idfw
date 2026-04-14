import SwiftUI

struct EventStreamPanel: View {
    @Bindable var viewModel: EventStreamViewModel

    var body: some View {
        VStack(spacing: 0) {
            connectionHeader
                .padding()

            Divider()

            if viewModel.events.isEmpty {
                ContentUnavailableView(
                    "No Events",
                    systemImage: "antenna.radiowaves.left.and.right",
                    description: Text("Events will appear here when connected.")
                )
            } else {
                ScrollViewReader { proxy in
                    List(viewModel.events) { event in
                        EventRowView(event: event)
                            .id(event.id)
                    }
                    .onChange(of: viewModel.events.count) {
                        if let last = viewModel.events.last {
                            proxy.scrollTo(last.id, anchor: .bottom)
                        }
                    }
                }
            }
        }
        .frame(minWidth: 280)
        .accessibilityIdentifier(AccessibilityIdentifiers.EventStream.panel)
    }

    private var connectionHeader: some View {
        HStack {
            Circle()
                .fill(statusColor)
                .frame(width: 8, height: 8)
            Text(statusText)
                .font(.caption.weight(.medium))
            Spacer()
            if case .connected = viewModel.connectionState {
                Button("Disconnect") { viewModel.disconnect() }
                    .buttonStyle(.plain)
                    .font(.caption)
            }
        }
        .liquidGlassCard()
    }

    private var statusColor: Color {
        switch viewModel.connectionState {
        case .disconnected: return .gray
        case .connecting:   return .orange
        case .connected:    return .green
        case .error:        return .red
        }
    }

    private var statusText: String {
        switch viewModel.connectionState {
        case .disconnected:     return "Disconnected"
        case .connecting:       return "Connecting..."
        case .connected:        return "Connected"
        case .error(let msg):   return "Error: \(msg)"
        }
    }
}
