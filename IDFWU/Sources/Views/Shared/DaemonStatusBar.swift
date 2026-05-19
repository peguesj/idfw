import SwiftUI

/// Persistent bottom status bar (Xcode/VS Code style) showing the `/idea`
/// daemon connection. Reads `DaemonController` from the environment.
struct DaemonStatusBar: View {
    @Environment(DaemonController.self) private var daemon

    var body: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(indicatorColor)
                .frame(width: 8, height: 8)
            Text(daemon.displayText)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(1)

            Spacer()

            if daemon.isConnected {
                Button {
                    if let url = URL(string: "\(daemon.baseURL)/ui") {
                        NSWorkspace.shared.open(url)
                    }
                } label: {
                    Label("Dashboard", systemImage: "chart.line.uptrend.xyaxis")
                        .labelStyle(.titleAndIcon)
                }
                .buttonStyle(.borderless)
                .controlSize(.small)
            }

            Button {
                daemon.reconnect()
            } label: {
                Image(systemName: "arrow.clockwise")
            }
            .buttonStyle(.borderless)
            .controlSize(.small)
            .help("Reconnect / start the IDEA daemon")
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 5)
        .background(.bar)
        .overlay(alignment: .top) { Divider() }
    }

    private var indicatorColor: Color {
        switch daemon.state {
        case .connected:                return .green
        case .connecting, .starting:    return .orange
        case .error:                    return .red
        case .disconnected:             return .secondary
        }
    }
}
