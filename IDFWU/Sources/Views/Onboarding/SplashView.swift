import SwiftUI

struct SplashView: View {
    @Binding var isPresented: Bool
    @AppStorage("lastSplashVersion") private var lastSplashVersion: String = ""
    @State private var buttonsEnabled = false

    private var currentVersion: String {
        (Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String) ?? "0"
    }

    var body: some View {
        ZStack {
            AnimatedGradientBackground()
                .ignoresSafeArea()

            VStack(spacing: 24) {
                Spacer()

                Image(systemName: "cube.transparent.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 96, height: 96)
                    .foregroundStyle(Color.accentColor)
                    .shadow(color: Color.accentColor.opacity(0.4), radius: 20)

                Text("IDFWU — Project Manager")
                    .font(.system(size: 32, weight: .bold, design: .rounded))
                    .foregroundStyle(.primary)

                Text("Version \(currentVersion)")
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .monospacedDigit()

                Text("Manage IDFW-enabled projects across your workspace roots")
                    .font(.title3)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)

                Spacer()

                HStack(spacing: 16) {
                    Button("Skip") {
                        dismiss()
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.large)
                    .disabled(!buttonsEnabled)

                    Button("Get Started") {
                        dismiss()
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    .keyboardShortcut(.defaultAction)
                    .disabled(!buttonsEnabled)
                }
                .padding(.bottom, 40)
            }
            .padding()
        }
        .task {
            try? await Task.sleep(for: .seconds(2))
            buttonsEnabled = true
        }
    }

    private func dismiss() {
        lastSplashVersion = currentVersion
        withAnimation(.easeOut(duration: 0.25)) {
            isPresented = false
        }
    }
}

private struct AnimatedGradientBackground: View {
    var body: some View {
        TimelineView(.animation) { context in
            let t = context.date.timeIntervalSinceReferenceDate
            let phase = (t.truncatingRemainder(dividingBy: 8.0)) / 8.0
            let hueA = phase
            let hueB = (phase + 0.33).truncatingRemainder(dividingBy: 1.0)

            LinearGradient(
                colors: [
                    Color(hue: hueA, saturation: 0.55, brightness: 0.35),
                    Color(hue: hueB, saturation: 0.55, brightness: 0.20)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }
}
