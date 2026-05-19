import SwiftUI

/// Live, auto-scrolling stream of normalized provider events — the build
/// "console" the user watches their idea become real in.
struct BuilderTranscriptView: View {
    let events: [ProviderEvent]

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 6) {
                    ForEach(events) { event in
                        row(event).id(event.id)
                    }
                }
                .padding(12)
            }
            .onChange(of: events.count) { _, _ in
                if let last = events.last {
                    withAnimation(.easeOut(duration: 0.15)) {
                        proxy.scrollTo(last.id, anchor: .bottom)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func row(_ event: ProviderEvent) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: event.symbol)
                .font(.caption)
                .foregroundStyle(color(for: event.kind))
                .frame(width: 16)
            Text(event.text)
                .font(textFont(for: event.kind))
                .foregroundStyle(event.kind == .error ? .red : .primary)
                .textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(.vertical, event.kind == .notice ? 1 : 2)
    }

    private func textFont(for kind: ProviderEvent.Kind) -> Font {
        switch kind {
        case .toolCall, .toolResult, .fileWrite, .fileDelete:
            return .system(.caption, design: .monospaced)
        case .notice:
            return .caption
        default:
            return .callout
        }
    }

    private func color(for kind: ProviderEvent.Kind) -> Color {
        switch kind {
        case .thinking:   return .purple
        case .text:       return .primary
        case .toolCall:   return .blue
        case .toolResult: return .teal
        case .fileWrite:  return .green
        case .fileDelete: return .red
        case .notice:     return .secondary
        case .error:      return .red
        case .done:       return .green
        }
    }
}
