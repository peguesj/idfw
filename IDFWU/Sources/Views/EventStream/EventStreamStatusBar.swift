import SwiftUI

struct EventStreamStatusBar: View {
    @Environment(\.eventStreamState) private var client

    private var statusColor: Color {
        switch client.connectionState {
        case .connected:     .green
        case .connecting:    .orange
        case .reconnecting:  .orange
        case .disconnected:  .red
        }
    }

    private var statusText: String {
        switch client.connectionState {
        case .connected:     "Connected"
        case .connecting:    "Connecting..."
        case .reconnecting:  "Reconnecting..."
        case .disconnected:  "Disconnected"
        }
    }

    var body: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(statusColor)
                .frame(width: 8, height: 8)
                .shadow(color: statusColor.opacity(0.6), radius: 3)

            Text(statusText)
                .font(.caption)
                .foregroundStyle(.secondary)

            Spacer()

            if let timestamp = client.lastEventTimestamp {
                Text(timestamp, style: .relative)
                    .font(.caption2)
                    .foregroundStyle(.quaternary)
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Event stream \(statusText)")
    }
}

#Preview("Connected") {
    let client = EventStreamState()
    client.connectionState = .connected
    client.lastEventTimestamp = Date().addingTimeInterval(-12)
    return EventStreamStatusBar()
        .environment(\.eventStreamState, client)
        .padding()
        .frame(width: 260)
}

#Preview("Disconnected") {
    EventStreamStatusBar()
        .environment(\.eventStreamState, EventStreamState())
        .padding()
        .frame(width: 260)
}
