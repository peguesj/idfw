import SwiftUI
import Observation

/// Observable transient toast notifier. Publish a message via `show(_:)` and
/// the attached `ProgressToast` view modifier will render it at the bottom of
/// the host view for `duration` seconds.
@MainActor
@Observable
final class ToastNotifier {
    var message: String? = nil
    private var dismissTask: Task<Void, Never>?

    /// Show a toast message that auto-dismisses after `duration` seconds.
    /// Subsequent calls cancel any pending dismissal and replace the message.
    func show(_ text: String, duration: TimeInterval = 3.0) {
        message = text
        dismissTask?.cancel()
        let nanoseconds = UInt64(duration * 1_000_000_000)
        dismissTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: nanoseconds)
            guard !Task.isCancelled else { return }
            await MainActor.run {
                self?.message = nil
            }
        }
    }
}

/// View modifier that renders a capsule-shaped toast at the bottom of the
/// host view whenever the attached `ToastNotifier` publishes a message.
struct ProgressToast: ViewModifier {
    @Bindable var notifier: ToastNotifier

    func body(content: Content) -> some View {
        content.overlay(alignment: .bottom) {
            if let msg = notifier.message {
                Text(msg)
                    .font(.callout)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(.ultraThinMaterial, in: Capsule())
                    .shadow(radius: 8, y: 4)
                    .padding(.bottom, 24)
                    .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
        .animation(.spring(response: 0.35, dampingFraction: 0.8), value: notifier.message)
    }
}

extension View {
    /// Attach a `ToastNotifier`-backed progress toast to this view.
    func progressToast(notifier: ToastNotifier) -> some View {
        modifier(ProgressToast(notifier: notifier))
    }
}
