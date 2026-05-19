import SwiftUI

// MARK: - Command-K palette

struct CommandKPalette: View {
    @Binding var isPresented: Bool
    var projects: [BuilderProject] = []
    var onSelectProject: ((BuilderProject) -> Void)? = nil
    var onSelectSkill: ((BuilderSkill) -> Void)? = nil

    @State private var query = ""
    @FocusState private var focused: Bool

    private var filteredSkills: [BuilderSkill] {
        guard !query.isEmpty else { return Array(SampleData.skills.prefix(5)) }
        return SampleData.skills.filter {
            $0.title.lowercased().contains(query.lowercased())
            || $0.command.contains(query)
        }
    }

    private var filteredProjects: [BuilderProject] {
        guard !query.isEmpty else { return Array(projects.prefix(3)) }
        return projects.filter { $0.name.lowercased().contains(query.lowercased()) }
    }

    var body: some View {
        ZStack {
            DesignTokens.Background.overlay
                .ignoresSafeArea()
                .onTapGesture { close() }

            VStack(spacing: 0) {
                // Search input
                HStack(spacing: 10) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 14))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                    TextField("Search skills, projects, actions…", text: $query)
                        .font(.system(size: 14))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                        .textFieldStyle(.plain)
                        .focused($focused)
                    if !query.isEmpty {
                        Button(action: { query = "" }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundStyle(DesignTokens.Foreground.quaternary)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)

                Divider().background(DesignTokens.Hairline.soft)

                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        if !filteredSkills.isEmpty {
                            PaletteGroup(title: "Skills") {
                                ForEach(filteredSkills) { skill in
                                    SkillPaletteRow(skill: skill) {
                                        onSelectSkill?(skill)
                                        close()
                                    }
                                }
                            }
                        }

                        if !filteredProjects.isEmpty {
                            PaletteGroup(title: "Projects") {
                                ForEach(filteredProjects) { project in
                                    ProjectPaletteRow(project: project) {
                                        onSelectProject?(project)
                                        close()
                                    }
                                }
                            }
                        }

                        if query.isEmpty {
                            PaletteGroup(title: "Actions") {
                                ActionPaletteRow(symbol: "plus", label: "New project") {}
                                ActionPaletteRow(symbol: "gearshape", label: "Open settings") {}
                                ActionPaletteRow(symbol: "questionmark.circle", label: "Help & docs") {}
                            }
                        }

                        if filteredSkills.isEmpty && filteredProjects.isEmpty && !query.isEmpty {
                            Text("No results for \"\(query)\"")
                                .font(.system(size: 12))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                                .frame(maxWidth: .infinity, alignment: .center)
                                .padding(.vertical, 24)
                        }
                    }
                    .padding(.vertical, 6)
                }
                .frame(maxHeight: 360)
            }
            .frame(width: 540)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.Radius.xl)
                    .fill(DesignTokens.Background.raised)
                    .overlay(
                        RoundedRectangle(cornerRadius: DesignTokens.Radius.xl)
                            .strokeBorder(DesignTokens.Hairline.bold, lineWidth: 0.5)
                    )
                    .shadow(color: .black.opacity(0.6), radius: 40, y: 20)
            )
        }
        .onAppear { focused = true }
        .onKeyPress(.escape) { close(); return .handled }
    }

    private func close() {
        isPresented = false
        query = ""
    }
}

// MARK: - Palette group

private struct PaletteGroup<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 1) {
            OverlineLabel(text: title)
                .padding(.horizontal, 14)
                .padding(.top, 10)
                .padding(.bottom, 4)
            content()
        }
    }
}

// MARK: - Row types

private struct SkillPaletteRow: View {
    let skill: BuilderSkill
    let action: () -> Void
    @State private var hovered = false

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                IDEAPhaseLetter(phase: skill.phase, size: .sm, state: .active)
                VStack(alignment: .leading, spacing: 1) {
                    Text(skill.command)
                        .font(.system(size: 12, weight: .medium, design: .monospaced))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                    Text(skill.description)
                        .font(.system(size: 10))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                }
                Spacer(minLength: 0)
                Text(skill.phase.builderTitle)
                    .font(.system(size: 9))
                    .foregroundStyle(skill.phase.color)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 7)
            .background(hovered ? DesignTokens.Glass.thin : Color.clear)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .onHover { hovered = $0 }
    }
}

private struct ProjectPaletteRow: View {
    let project: BuilderProject
    let action: () -> Void
    @State private var hovered = false

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                IDEAPhaseLetter(phase: project.phase, size: .sm, state: .active)
                VStack(alignment: .leading, spacing: 1) {
                    Text(project.name)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(DesignTokens.Foreground.primary)
                    Text(project.description)
                        .font(.system(size: 10))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                        .lineLimit(1)
                }
                Spacer(minLength: 0)
                PhaseChip(phase: project.phase)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 7)
            .background(hovered ? DesignTokens.Glass.thin : Color.clear)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .onHover { hovered = $0 }
    }
}

private struct ActionPaletteRow: View {
    let symbol: String
    let label: String
    let action: () -> Void
    @State private var hovered = false

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: symbol)
                    .font(.system(size: 12))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
                    .frame(width: 20)
                Text(label)
                    .font(.system(size: 12))
                    .foregroundStyle(DesignTokens.Foreground.secondary)
                Spacer(minLength: 0)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 7)
            .background(hovered ? DesignTokens.Glass.thin : Color.clear)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .onHover { hovered = $0 }
    }
}
