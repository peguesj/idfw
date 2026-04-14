import SwiftUI

struct LoadingOverlay: View {
    var message: String?

    var body: some View {
        ZStack {
            Rectangle()
                .fill(.ultraThinMaterial)

            VStack(spacing: 12) {
                ProgressView()
                    .controlSize(.large)

                if let message {
                    Text(message)
                        .font(.callout)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .ignoresSafeArea()
    }
}

extension View {
    func loadingOverlay(isPresented: Bool, message: String? = nil) -> some View {
        overlay {
            if isPresented {
                LoadingOverlay(message: message)
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.2), value: isPresented)
    }
}

#Preview {
    Text("Content behind overlay")
        .frame(width: 400, height: 300)
        .loadingOverlay(isPresented: true, message: "Loading schemas...")
}
