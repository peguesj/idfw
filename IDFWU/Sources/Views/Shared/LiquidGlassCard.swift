import SwiftUI

struct LiquidGlassCard: ViewModifier {
    var cornerRadius: CGFloat = 12

    func body(content: Content) -> some View {
        content
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: cornerRadius))
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color.white.opacity(0.08),
                                Color.clear,
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .allowsHitTesting(false)
            }
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius)
                    .strokeBorder(Color(nsColor: .separatorColor), lineWidth: 1)
            }
    }
}

extension View {
    func liquidGlassCard(cornerRadius: CGFloat = 12) -> some View {
        modifier(LiquidGlassCard(cornerRadius: cornerRadius))
    }
}

#Preview {
    VStack {
        Text("Liquid Glass Card")
            .padding(24)
            .liquidGlassCard()
    }
    .padding()
    .frame(width: 300, height: 200)
    .background(Color.black.opacity(0.8))
}
