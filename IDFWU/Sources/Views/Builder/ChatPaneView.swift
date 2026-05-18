import SwiftUI

// MARK: - Chat pane (left main area)

struct ChatPaneView: View {
    let project: BuilderProject
    var messages: [TranscriptMessage]
    @Binding var inputText: String
    var onSend: (String) -> Void
    var onGateExpand: ((DecisionGate.Full) -> Void)? = nil
    var onPinGate: ((DecisionGate.Full) -> Void)? = nil

    @State private var showSlashPalette = false

    var body: some View {
        VStack(spacing: 0) {
            chatHeader
            Divider().background(DesignTokens.Hairline.soft)
            transcript
            Divider().background(DesignTokens.Hairline.soft)
            composer
        }
        .background(DesignTokens.Background.base)
    }

    // MARK: Header

    private var chatHeader: some View {
        HStack(spacing: 10) {
            VStack(alignment: .leading, spacing: 2) {
                HStack(spacing: 6) {
                    Text(project.name)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                    StatusPill(label: "live", color: .live)
                }
                HStack(spacing: 4) {
                    PhaseChip(phase: project.phase)
                    Text("·")
                        .foregroundStyle(DesignTokens.Foreground.quaternary)
                    Text(project.llmModel)
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                }
            }
            Spacer(minLength: 0)
            ProviderChip(kind: project.provider, active: true)
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 12)
    }

    // MARK: Transcript

    private var transcript: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 2) {
                    ForEach(messages) { msg in
                        MessageRow(
                            message: msg,
                            project: project,
                            onGateExpand: onGateExpand,
                            onPinGate: onPinGate
                        )
                        .id(msg.id)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
            .onChange(of: messages.count) { _, _ in
                if let last = messages.last {
                    withAnimation { proxy.scrollTo(last.id, anchor: .bottom) }
                }
            }
        }
    }

    // MARK: Composer

    private var composer: some View {
        VStack(spacing: 0) {
            if showSlashPalette {
                SlashPalette(
                    query: String(inputText.dropFirst()),
                    currentPhase: project.phase
                ) { skill in
                    inputText = ""
                    showSlashPalette = false
                    onSend(skill.command)
                }
                .transition(.move(edge: .bottom).combined(with: .opacity))
            }

            composerInput
        }
        .animation(.easeOut(duration: 0.15), value: showSlashPalette)
    }

    @State private var composerFocused = false

    private var composerInput: some View {
        HStack(alignment: .bottom, spacing: 10) {
            ZStack(alignment: .topLeading) {
                if inputText.isEmpty {
                    Text("Message · / for skills")
                        .font(.system(size: 13))
                        .foregroundStyle(DesignTokens.Foreground.quaternary)
                        .padding(.top, 9)
                        .padding(.leading, 2)
                        .allowsHitTesting(false)
                }
                TextEditor(text: $inputText)
                    .font(.system(size: 13))
                    .foregroundStyle(DesignTokens.Foreground.primary)
                    .scrollContentBackground(.hidden)
                    .background(Color.clear)
                    .frame(minHeight: 34, maxHeight: 120)
                    .onChange(of: inputText) { _, newVal in
                        showSlashPalette = newVal.hasPrefix("/")
                    }
            }

            Button(action: sendMessage) {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.system(size: 22))
                    .foregroundStyle(
                        inputText.isEmpty
                        ? DesignTokens.Foreground.quaternary
                        : project.phase.color
                    )
            }
            .buttonStyle(.plain)
            .disabled(inputText.isEmpty)
            .keyboardShortcut(.return, modifiers: .command)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(
            RoundedRectangle(cornerRadius: 0)
                .fill(DesignTokens.Background.base)
        )
        .overlay(alignment: .top) {
            // Phase glow strip at composer top
            LinearGradient(
                colors: [project.phase.color.opacity(0.25), .clear],
                startPoint: .leading,
                endPoint: .trailing
            )
            .frame(height: 1)
        }
    }

    private func sendMessage() {
        guard !inputText.isEmpty else { return }
        let text = inputText
        inputText = ""
        showSlashPalette = false
        onSend(text)
    }
}

// MARK: - Message row dispatcher

private struct MessageRow: View {
    let message: TranscriptMessage
    let project: BuilderProject
    var onGateExpand: ((DecisionGate.Full) -> Void)?
    var onPinGate: ((DecisionGate.Full) -> Void)?

    var body: some View {
        switch message.kind {
        case .user(let m):
            UserMessageBubble(message: m)
        case .agent(let m):
            AgentMessageRow(message: m)
        case .system(let m):
            SystemMessageRow(text: m.text)
        case .phaseTransition(let m):
            PhaseTransitionRow(transition: m)
        case .toolCall(let m):
            ToolCallRow(message: m)
        case .fileWrite(let m):
            FileWriteRow(message: m)
        case .gateRef(let m):
            GateRefRow(message: m)
        case .gate(let g):
            GateInlineCard(gate: g,
                          onPin: { onPinGate?(g) },
                          onExpand: { onGateExpand?(g) })
                .padding(.vertical, 6)
        }
    }
}

// MARK: - User message bubble

private struct UserMessageBubble: View {
    let message: UserMessage
    var body: some View {
        HStack {
            Spacer(minLength: 60)
            Text(message.text)
                .font(.system(size: 13))
                .foregroundStyle(DesignTokens.Foreground.primary)
                .padding(.horizontal, 14)
                .padding(.vertical, 9)
                .background(
                    RoundedRectangle(cornerRadius: 14)
                        .fill(DesignTokens.Background.raised)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .strokeBorder(DesignTokens.Hairline.bold, lineWidth: 0.5)
                        )
                )
        }
        .padding(.vertical, 3)
    }
}

// MARK: - Agent message

private struct AgentMessageRow: View {
    let message: AgentMessage
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            MessageAvatar(isBot: true, providerKind: message.providerKind)
            VStack(alignment: .leading, spacing: 4) {
                if message.isThinking {
                    ThinkingIndicator(providerKind: message.providerKind)
                } else {
                    Text(message.text)
                        .font(.system(size: 13))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                        .textSelection(.enabled)
                }
            }
            Spacer(minLength: 40)
        }
        .padding(.vertical, 4)
    }
}

private struct ThinkingIndicator: View {
    let providerKind: AIProviderKind
    @State private var dotOffset: Int = 0

    var body: some View {
        HStack(spacing: 4) {
            ProviderGlyph(kind: providerKind, size: 11)
            Text("Thinking")
                .font(.system(size: 11))
                .foregroundStyle(DesignTokens.Foreground.tertiary)
            HStack(spacing: 3) {
                ForEach(0..<3) { i in
                    Circle()
                        .fill(DesignTokens.Foreground.tertiary)
                        .frame(width: 3, height: 3)
                        .opacity(dotOffset == i ? 1.0 : 0.3)
                }
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(
            Capsule().fill(DesignTokens.Glass.thin)
                .overlay(Capsule().strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5))
        )
        .onAppear {
            withAnimation(.linear(duration: 0.6).repeatForever()) {
                dotOffset = (dotOffset + 1) % 3
            }
        }
    }
}

// MARK: - System message

private struct SystemMessageRow: View {
    let text: String
    var body: some View {
        HStack {
            Spacer()
            Text(text)
                .font(.system(size: 10))
                .foregroundStyle(DesignTokens.Foreground.quaternary)
                .padding(.horizontal, 12)
                .padding(.vertical, 4)
                .background(Capsule().fill(DesignTokens.Glass.thin))
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Phase transition

private struct PhaseTransitionRow: View {
    let transition: PhaseTransition
    var body: some View {
        HStack(spacing: 10) {
            LinearGradient(
                colors: [.clear, transition.to.color.opacity(0.5)],
                startPoint: .leading,
                endPoint: .trailing
            )
            .frame(height: 1)

            HStack(spacing: 6) {
                IDEAPhaseLetter(phase: transition.to, size: .sm, state: .active)
                Text(transition.label)
                    .font(.system(size: 10, weight: .semibold))
                    .foregroundStyle(transition.to.color)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill(transition.to.color.opacity(0.10))
                    .overlay(Capsule().strokeBorder(transition.to.color.opacity(0.25), lineWidth: 0.5))
            )

            LinearGradient(
                colors: [transition.to.color.opacity(0.5), .clear],
                startPoint: .leading,
                endPoint: .trailing
            )
            .frame(height: 1)
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Tool call row (collapsible)

private struct ToolCallRow: View {
    let message: ToolCallMessage
    @State private var expanded: Bool = true

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Button(action: { withAnimation(.easeOut(duration: 0.15)) { expanded.toggle() } }) {
                HStack(spacing: 8) {
                    Image(systemName: statusIcon)
                        .font(.system(size: 11))
                        .foregroundStyle(statusColor)
                    Text(message.tool)
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundStyle(DesignTokens.Foreground.secondary)
                    if let summary = message.summary {
                        Text("·")
                            .foregroundStyle(DesignTokens.Foreground.quaternary)
                        Text(summary)
                            .font(.system(size: 10))
                            .foregroundStyle(DesignTokens.Foreground.tertiary)
                            .lineLimit(1)
                    }
                    Spacer(minLength: 0)
                    if !message.children.isEmpty {
                        Image(systemName: expanded ? "chevron.up" : "chevron.down")
                            .font(.system(size: 9, weight: .bold))
                            .foregroundStyle(DesignTokens.Foreground.quaternary)
                    }
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .fill(DesignTokens.Glass.thin)
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .strokeBorder(DesignTokens.Hairline.soft, lineWidth: 0.5)
                        )
                )
            }
            .buttonStyle(.plain)

            if expanded && !message.children.isEmpty {
                VStack(alignment: .leading, spacing: 3) {
                    ForEach(message.children) { child in
                        HStack(spacing: 6) {
                            Rectangle()
                                .fill(DesignTokens.Hairline.bold)
                                .frame(width: 1)
                                .padding(.leading, 14)
                            HStack(spacing: 6) {
                                Image(systemName: "arrow.turn.down.right")
                                    .font(.system(size: 9))
                                    .foregroundStyle(DesignTokens.Foreground.quaternary)
                                Text(child.tool)
                                    .font(.system(size: 10, design: .monospaced))
                                    .foregroundStyle(DesignTokens.Foreground.tertiary)
                                Spacer()
                                Image(systemName: child.status == .done ? "checkmark" : "circle")
                                    .font(.system(size: 9))
                                    .foregroundStyle(child.status == .done
                                        ? DesignTokens.Gate.passed
                                        : DesignTokens.Foreground.quaternary)
                            }
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                        }
                    }
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(.vertical, 3)
    }

    private var statusIcon: String {
        switch message.status {
        case .running: return "circle.fill"
        case .done:    return "checkmark.circle.fill"
        case .failed:  return "xmark.circle.fill"
        }
    }

    private var statusColor: Color {
        switch message.status {
        case .running: return DesignTokens.Gate.pending
        case .done:    return DesignTokens.Gate.passed
        case .failed:  return DesignTokens.Gate.failed
        }
    }
}

// MARK: - File write row

private struct FileWriteRow: View {
    let message: FileWriteMessage
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "doc.badge.plus")
                .font(.system(size: 11))
                .foregroundStyle(DesignTokens.Phase.ideation)
            Text(message.path)
                .font(.system(size: 10, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.secondary)
                .lineLimit(1)
            if let lines = message.lineCount {
                Text("·")
                    .foregroundStyle(DesignTokens.Foreground.quaternary)
                Text("\(lines) lines")
                    .font(.system(size: 10))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(DesignTokens.Phase.ideation.opacity(0.06))
                .overlay(
                    RoundedRectangle(cornerRadius: 6)
                        .strokeBorder(DesignTokens.Phase.ideation.opacity(0.15), lineWidth: 0.5)
                )
        )
        .padding(.vertical, 2)
    }
}

// MARK: - Gate ref row (resolution pill)

private struct GateRefRow: View {
    let message: GateRefMessage
    var body: some View {
        HStack {
            Spacer()
            HStack(spacing: 6) {
                Image(systemName: resolutionSymbol)
                    .font(.system(size: 10))
                Text(resolutionLabel)
                    .font(.system(size: 10, weight: .semibold))
            }
            .foregroundStyle(resolutionColor)
            .padding(.horizontal, 12)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill(resolutionColor.opacity(0.10))
                    .overlay(Capsule().strokeBorder(resolutionColor.opacity(0.25), lineWidth: 0.5))
            )
            Spacer()
        }
        .padding(.vertical, 4)
    }

    private var resolutionLabel: String {
        switch message.resolution {
        case .approve:         return "Gate approved"
        case .requestChanges:  return "Changes requested"
        case .waive:           return "Gate waived"
        case .reject:          return "Gate rejected"
        }
    }

    private var resolutionSymbol: String {
        switch message.resolution {
        case .approve:         return "checkmark.circle"
        case .requestChanges:  return "pencil.circle"
        case .waive:           return "minus.circle"
        case .reject:          return "xmark.circle"
        }
    }

    private var resolutionColor: Color {
        switch message.resolution {
        case .approve:         return DesignTokens.Gate.passed
        case .requestChanges:  return DesignTokens.Gate.pending
        case .waive:           return DesignTokens.Gate.waived
        case .reject:          return DesignTokens.Gate.failed
        }
    }
}

// MARK: - Slash palette

struct SlashPalette: View {
    let query: String
    let currentPhase: IDEAPhase
    var onSelect: (BuilderSkill) -> Void

    private var filteredSkills: [BuilderSkill] {
        let skills = SampleData.skills
        if query.isEmpty { return Array(skills.prefix(8)) }
        return skills.filter { $0.title.lowercased().contains(query.lowercased())
            || $0.command.contains(query) }
            .prefix(8)
            .sorted { $0.phase == currentPhase && $1.phase != currentPhase }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            OverlineLabel(text: "Skills")
                .padding(.horizontal, 14)
                .padding(.top, 8)
                .padding(.bottom, 4)

            ForEach(filteredSkills) { skill in
                Button(action: { onSelect(skill) }) {
                    HStack(spacing: 10) {
                        IDEAPhaseLetter(phase: skill.phase, size: .sm,
                                        state: skill.phase == currentPhase ? .active : .todo)
                        VStack(alignment: .leading, spacing: 1) {
                            Text(skill.command)
                                .font(.system(size: 12, weight: .medium, design: .monospaced))
                                .foregroundStyle(DesignTokens.Foreground.primary)
                            Text(skill.description)
                                .font(.system(size: 10))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                        }
                        Spacer()
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 6)
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                .background(Color.clear)
                .onHover { hovered in
                    // highlight on hover handled by buttonStyle
                }
            }
        }
        .padding(.bottom, 8)
        .background(
            RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                .fill(DesignTokens.Background.raised)
                .overlay(
                    RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                        .strokeBorder(DesignTokens.Hairline.bold, lineWidth: 0.5)
                )
                .shadow(color: .black.opacity(0.4), radius: 12, y: -4)
        )
        .padding(.horizontal, 8)
    }
}
