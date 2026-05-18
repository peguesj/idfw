import SwiftUI

// MARK: - Hero Prompt (empty state / entry point)

struct HeroPromptView: View {
    @Binding var inputText: String
    var onSubmit: (String) -> Void
    var onSkillTap: (BuilderSkill) -> Void

    @State private var isFocused = false
    @State private var orb1Phase: Double = 0
    @State private var orb2Phase: Double = 2.1
    @State private var orb3Phase: Double = 4.2

    private let examplePrompts = [
        "Build a real-time chat app with E2E encryption",
        "Create an AI-powered code review tool",
        "Design a distributed task queue with priority lanes",
        "Build a privacy-first location sharing service",
    ]

    var body: some View {
        ZStack {
            DesignTokens.Background.base
                .ignoresSafeArea()

            ambientOrbs

            VStack(spacing: 0) {
                Spacer()

                VStack(spacing: 28) {
                    headingSection
                    composerSection
                    exampleChips
                }

                Spacer()
                Spacer()
            }
            .padding(.horizontal, 48)
            .frame(maxWidth: 680)
            .frame(maxWidth: .infinity)
        }
        .onAppear { startOrbAnimation() }
    }

    // MARK: - Ambient orbs

    private var ambientOrbs: some View {
        ZStack {
            // Orb 1 — ideation warm peach
            orbShape(phase: DesignTokens.Phase.ideation, animPhase: orb1Phase,
                     offsetX: -180, offsetY: -120, size: 320)
            // Orb 2 — definition blue
            orbShape(phase: DesignTokens.Phase.definition, animPhase: orb2Phase,
                     offsetX: 200, offsetY: -60, size: 280)
            // Orb 3 — application green
            orbShape(phase: DesignTokens.Phase.application, animPhase: orb3Phase,
                     offsetX: 60, offsetY: 140, size: 200)
        }
    }

    private func orbShape(phase: Color, animPhase: Double, offsetX: CGFloat, offsetY: CGFloat, size: CGFloat) -> some View {
        Ellipse()
            .fill(phase.opacity(0.08))
            .frame(width: size, height: size * 0.7)
            .offset(x: offsetX + cos(animPhase) * 20, y: offsetY + sin(animPhase) * 15)
            .blur(radius: 60)
    }

    // MARK: Heading

    private var headingSection: some View {
        VStack(spacing: 8) {
            BrandMark(size: 48)
                .padding(.bottom, 4)
            Text("What do you want to build?")
                .font(.system(size: 28, weight: .bold, design: .default))
                .foregroundStyle(DesignTokens.Foreground.primary)
                .multilineTextAlignment(.center)
            Text("Describe your idea. IDFWU will guide it through Discover → Define → Plan → Execute.")
                .font(.system(size: 14))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
                .multilineTextAlignment(.center)
                .lineLimit(2)
        }
    }

    // MARK: Composer

    private var composerSection: some View {
        VStack(spacing: 0) {
            ZStack(alignment: .bottomTrailing) {
                // Glow border when focused
                if isFocused {
                    RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                        .strokeBorder(
                            LinearGradient(
                                colors: [
                                    DesignTokens.Phase.ideation.opacity(0.6),
                                    DesignTokens.Phase.definition.opacity(0.6),
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            lineWidth: 1.5
                        )
                        .shadow(color: DesignTokens.Phase.definition.opacity(0.25), radius: 20)
                        .animation(.easeOut(duration: 0.2), value: isFocused)
                }

                VStack(spacing: 0) {
                    ZStack(alignment: .topLeading) {
                        if inputText.isEmpty {
                            Text("Describe your idea or paste a problem statement…")
                                .font(.system(size: 14))
                                .foregroundStyle(DesignTokens.Foreground.quaternary)
                                .padding(.top, 14)
                                .padding(.leading, 16)
                                .allowsHitTesting(false)
                        }
                        TextEditor(text: $inputText)
                            .font(.system(size: 14))
                            .foregroundStyle(DesignTokens.Foreground.primary)
                            .scrollContentBackground(.hidden)
                            .background(Color.clear)
                            .frame(minHeight: 80, maxHeight: 160)
                            .padding(.horizontal, 12)
                            .padding(.top, 10)
                            .onAppear {
                                // Attempt to remove focus ring via AppKit
                            }
                    }

                    Divider()
                        .background(DesignTokens.Hairline.soft)

                    // Composer toolbar
                    HStack(spacing: 8) {
                        ProviderChip(kind: .claude, active: true)
                        Spacer(minLength: 0)
                        Text(inputText.isEmpty ? "" : "\(inputText.count) chars")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundStyle(DesignTokens.Foreground.quaternary)
                        Button(action: submit) {
                            HStack(spacing: 4) {
                                Image(systemName: "arrow.up")
                                    .font(.system(size: 11, weight: .bold))
                                Text("Build")
                                    .font(.system(size: 12, weight: .semibold))
                            }
                            .foregroundStyle(inputText.isEmpty
                                ? DesignTokens.Foreground.quaternary
                                : Color(red: 0.08, green: 0.09, blue: 0.12))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 6)
                            .background(
                                Capsule()
                                    .fill(inputText.isEmpty
                                        ? DesignTokens.Background.raised
                                        : DesignTokens.Phase.definition)
                            )
                        }
                        .buttonStyle(.plain)
                        .disabled(inputText.isEmpty)
                        .keyboardShortcut(.return, modifiers: .command)
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                }
                .background(
                    RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                        .fill(DesignTokens.Background.raised)
                        .overlay(
                            RoundedRectangle(cornerRadius: DesignTokens.Radius.lg)
                                .strokeBorder(
                                    isFocused ? DesignTokens.Hairline.phase : DesignTokens.Hairline.soft,
                                    lineWidth: 0.5
                                )
                        )
                )
            }
        }
        .onTapGesture { isFocused = true }
    }

    // MARK: Example chips

    private var exampleChips: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(examplePrompts, id: \.self) { prompt in
                    Button(action: {
                        inputText = prompt
                        isFocused = true
                    }) {
                        Text(prompt)
                            .font(.system(size: 11))
                            .foregroundStyle(DesignTokens.Foreground.secondary)
                            .lineLimit(1)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(
                                Capsule()
                                    .fill(DesignTokens.Glass.thin)
                                    .overlay(Capsule().strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5))
                            )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 2)
        }
    }

    // MARK: - Actions

    private func submit() {
        guard !inputText.isEmpty else { return }
        onSubmit(inputText)
    }

    private func startOrbAnimation() {
        let timer = Timer.publish(every: 0.05, on: .main, in: .common).autoconnect()
        _ = timer.sink { _ in
            orb1Phase += 0.015
            orb2Phase += 0.012
            orb3Phase += 0.018
        }
    }
}

#Preview {
    HeroPromptView(
        inputText: .constant(""),
        onSubmit: { _ in },
        onSkillTap: { _ in }
    )
    .frame(width: 900, height: 600)
    .preferredColorScheme(.dark)
}
