import SwiftUI

// MARK: - HyperPlot tab (radar chart)

struct HyperPlotTabView: View {
    let axes: [HyperPlotAxis]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                OverlineLabel(text: "Constraint Radar")
                    .padding(.horizontal, 16)
                    .padding(.top, 14)

                HyperPlotRadar(axes: axes)
                    .frame(height: 280)
                    .padding(.horizontal, 20)

                VStack(alignment: .leading, spacing: 6) {
                    OverlineLabel(text: "Axes")
                        .padding(.horizontal, 16)
                    ForEach(axes) { axis in
                        HStack(spacing: 10) {
                            Text(axis.label)
                                .font(.system(size: 11))
                                .foregroundStyle(DesignTokens.Foreground.secondary)
                                .frame(width: 90, alignment: .leading)
                            GeometryReader { geo in
                                ZStack(alignment: .leading) {
                                    Capsule()
                                        .fill(DesignTokens.Hairline.bold)
                                        .frame(height: 4)
                                    // Target
                                    if let target = axis.targetValue {
                                        Capsule()
                                            .fill(DesignTokens.Phase.evaluation.opacity(0.30))
                                            .frame(width: geo.size.width * (target / axis.maxValue), height: 4)
                                    }
                                    // Actual
                                    Capsule()
                                        .fill(DesignTokens.Phase.definition)
                                        .frame(width: geo.size.width * axis.normalizedValue, height: 4)
                                }
                            }
                            .frame(height: 4)
                            Text(String(format: "%.0f", axis.value))
                                .font(.system(size: 10, design: .monospaced))
                                .foregroundStyle(DesignTokens.Foreground.tertiary)
                                .frame(width: 24, alignment: .trailing)
                        }
                        .padding(.horizontal, 16)
                    }
                }
                .padding(.bottom, 16)
            }
        }
    }
}

// MARK: - Radar canvas

private struct HyperPlotRadar: View {
    let axes: [HyperPlotAxis]

    var body: some View {
        Canvas { ctx, size in
            let center = CGPoint(x: size.width / 2, y: size.height / 2)
            let radius = min(size.width, size.height) / 2 - 28
            let count = axes.count
            guard count > 0 else { return }

            // Draw concentric rings (4 rings at 25%, 50%, 75%, 100%)
            for ring in [0.25, 0.50, 0.75, 1.0] {
                var path = Path()
                for i in 0..<count {
                    let angle = angleFor(index: i, total: count)
                    let pt = polarPoint(center: center, angle: angle, r: radius * ring)
                    if i == 0 { path.move(to: pt) } else { path.addLine(to: pt) }
                }
                path.closeSubpath()
                ctx.stroke(path, with: .color(DesignTokens.Hairline.bold), lineWidth: 0.5)
            }

            // Draw axis spokes
            for i in 0..<count {
                let angle = angleFor(index: i, total: count)
                var spoke = Path()
                spoke.move(to: center)
                spoke.addLine(to: polarPoint(center: center, angle: angle, r: radius))
                ctx.stroke(spoke, with: .color(DesignTokens.Hairline.soft), lineWidth: 0.5)
            }

            // Draw target polygon
            if axes.contains(where: { $0.targetValue != nil }) {
                var targetPath = Path()
                for (i, axis) in axes.enumerated() {
                    let angle = angleFor(index: i, total: count)
                    let r = radius * axis.normalizedTarget
                    let pt = polarPoint(center: center, angle: angle, r: r)
                    if i == 0 { targetPath.move(to: pt) } else { targetPath.addLine(to: pt) }
                }
                targetPath.closeSubpath()
                ctx.fill(targetPath, with: .color(DesignTokens.Phase.evaluation.opacity(0.10)))
                ctx.stroke(targetPath, with: .color(DesignTokens.Phase.evaluation.opacity(0.40)), lineWidth: 1)
            }

            // Draw actual polygon
            var actualPath = Path()
            for (i, axis) in axes.enumerated() {
                let angle = angleFor(index: i, total: count)
                let r = radius * axis.normalizedValue
                let pt = polarPoint(center: center, angle: angle, r: r)
                if i == 0 { actualPath.move(to: pt) } else { actualPath.addLine(to: pt) }
            }
            actualPath.closeSubpath()
            ctx.fill(actualPath, with: .color(DesignTokens.Phase.definition.opacity(0.20)))
            ctx.stroke(actualPath, with: .color(DesignTokens.Phase.definition.opacity(0.80)), lineWidth: 1.5)

            // Vertex dots + labels
            for (i, axis) in axes.enumerated() {
                let angle = angleFor(index: i, total: count)
                let r = radius * axis.normalizedValue
                let dotPt = polarPoint(center: center, angle: angle, r: r)
                let dotRect = CGRect(x: dotPt.x - 3, y: dotPt.y - 3, width: 6, height: 6)
                ctx.fill(Path(ellipseIn: dotRect), with: .color(DesignTokens.Phase.definition))

                // Labels on rim
                let labelPt = polarPoint(center: center, angle: angle, r: radius + 16)
                ctx.draw(Text(axis.label)
                    .font(.system(size: 9, weight: .medium))
                    .foregroundColor(DesignTokens.Foreground.tertiary),
                         at: labelPt)
            }
        }
        .background(DesignTokens.Background.base)
        .clipShape(RoundedRectangle(cornerRadius: DesignTokens.Radius.md))
    }

    private func angleFor(index: Int, total: Int) -> Double {
        (Double(index) / Double(total)) * 2 * .pi - .pi / 2
    }

    private func polarPoint(center: CGPoint, angle: Double, r: Double) -> CGPoint {
        CGPoint(x: center.x + cos(angle) * r, y: center.y + sin(angle) * r)
    }
}

// MARK: - Telemetry tab (sub-tabs: Graph / Timeline / Live)

struct TelemetryTabView: View {
    let nodes: [GraphNode]
    let edges: [GraphEdge]
    let events: [BuilderEvent]

    enum SubTab: String, CaseIterable { case graph = "Graph", timeline = "Timeline", live = "Live" }
    @State private var subTab: SubTab = .timeline

    var body: some View {
        VStack(spacing: 0) {
            // Sub-tab strip
            HStack(spacing: 0) {
                ForEach(SubTab.allCases, id: \.self) { tab in
                    Button(action: { subTab = tab }) {
                        Text(tab.rawValue)
                            .font(.system(size: 11, weight: subTab == tab ? .semibold : .regular))
                            .foregroundStyle(subTab == tab
                                ? DesignTokens.Foreground.primary
                                : DesignTokens.Foreground.tertiary)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 7)
                    }
                    .buttonStyle(.plain)
                }
                Spacer()
            }
            .padding(.horizontal, 8)
            .background(DesignTokens.Background.sunken)
            .overlay(alignment: .bottom) {
                Rectangle().fill(DesignTokens.Hairline.soft).frame(height: 0.5)
            }

            switch subTab {
            case .graph:
                AgentGraphView(nodes: nodes, edges: edges)
                    .frame(maxHeight: 520)
            case .timeline:
                EventTimelineView(events: events)
            case .live:
                LiveTailView(events: events)
            }
        }
    }
}

// MARK: - Agent graph (force-directed)

struct AgentGraphView: View {
    let nodes: [GraphNode]
    let edges: [GraphEdge]

    @State private var positions: [String: CGPoint] = [:]
    @State private var velocities: [String: CGSize] = [:]
    @State private var alpha: Double = 1.0
    @State private var selectedNodeID: String? = nil
    @State private var isDragging: String? = nil
    @State private var canvasSize: CGSize = .zero

    // Force parameters (matching JS design)
    private let chargeK: Double = -260
    private let springK: Double = 0.06
    private let centerK: Double = 0.02
    private let damping: Double = 0.78
    private let alphaCooling: Double = 0.992
    private let targetLength: Double = 90

    var body: some View {
        GeometryReader { geo in
            ZStack {
                DesignTokens.Background.base

                // Edges
                ForEach(edges) { edge in
                    if let src = positions[edge.sourceID],
                       let dst = positions[edge.targetID] {
                        Path { p in
                            p.move(to: src)
                            p.addLine(to: dst)
                        }
                        .stroke(DesignTokens.Hairline.bold, lineWidth: 1)
                    }
                }

                // Nodes
                ForEach(nodes) { node in
                    if let pos = positions[node.id] {
                        GraphNodeView(node: node, selected: selectedNodeID == node.id)
                            .position(pos)
                            .gesture(
                                DragGesture()
                                    .onChanged { value in
                                        isDragging = node.id
                                        positions[node.id] = value.location
                                        velocities[node.id] = .zero
                                    }
                                    .onEnded { _ in isDragging = nil }
                            )
                            .onTapGesture {
                                selectedNodeID = selectedNodeID == node.id ? nil : node.id
                            }
                    }
                }

                // Node inspector
                if let nodeID = selectedNodeID,
                   let node = nodes.first(where: { $0.id == nodeID }) {
                    NodeInspectorPanel(node: node)
                        .frame(maxWidth: 180)
                        .padding(10)
                        .background(
                            RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                                .fill(DesignTokens.Background.raised)
                                .overlay(
                                    RoundedRectangle(cornerRadius: DesignTokens.Radius.md)
                                        .strokeBorder(DesignTokens.Hairline.bold, lineWidth: 0.5)
                                )
                                .shadow(color: .black.opacity(0.5), radius: 12)
                        )
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottomLeading)
                        .padding(12)
                }
            }
            .onChange(of: geo.size, initial: true) { _, newSize in
                guard newSize != .zero else { return }
                canvasSize = newSize
                if positions.isEmpty {
                    initializePositions(in: newSize)
                    startSimulation()
                }
            }
        }
    }

    private func initializePositions(in size: CGSize) {
        for (i, node) in nodes.enumerated() {
            let angle = (Double(i) / Double(nodes.count)) * 2 * .pi
            let r = min(size.width, size.height) * 0.25
            positions[node.id] = CGPoint(
                x: size.width / 2 + cos(angle) * r,
                y: size.height / 2 + sin(angle) * r
            )
            velocities[node.id] = .zero
        }
    }

    private func startSimulation() {
        Task { @MainActor in
            while self.alpha > 0.001 {
                try? await Task.sleep(nanoseconds: 16_666_667)
                if self.canvasSize == .zero { continue }
                self.tick()
            }
        }
    }

    private func tick() {
        let center = CGPoint(x: canvasSize.width / 2, y: canvasSize.height / 2)
        var newPositions = positions
        var newVelocities = velocities

        for node in nodes {
            guard isDragging != node.id else { continue }
            var vx = newVelocities[node.id]?.width ?? 0
            var vy = newVelocities[node.id]?.height ?? 0
            guard var pos = newPositions[node.id] else { continue }

            // Charge repulsion (all pairs)
            for other in nodes where other.id != node.id {
                guard let otherPos = newPositions[other.id] else { continue }
                let dx = pos.x - otherPos.x
                let dy = pos.y - otherPos.y
                let distSq = max(dx * dx + dy * dy, 1)
                let force = chargeK / distSq
                vx += dx * force * alpha
                vy += dy * force * alpha
            }

            // Spring edges
            for edge in edges where edge.sourceID == node.id || edge.targetID == node.id {
                let otherID = edge.sourceID == node.id ? edge.targetID : edge.sourceID
                guard let otherPos = newPositions[otherID] else { continue }
                let dx = otherPos.x - pos.x
                let dy = otherPos.y - pos.y
                let dist = max(sqrt(dx * dx + dy * dy), 0.1)
                let force = (dist - targetLength) * springK * alpha
                vx += dx / dist * force
                vy += dy / dist * force
            }

            // Centering force
            vx += (center.x - pos.x) * centerK * alpha
            vy += (center.y - pos.y) * centerK * alpha

            // Apply damping
            vx *= damping
            vy *= damping

            pos.x += vx
            pos.y += vy

            // Clamp to canvas
            pos.x = max(20, min(canvasSize.width - 20, pos.x))
            pos.y = max(20, min(canvasSize.height - 20, pos.y))

            newVelocities[node.id] = CGSize(width: vx, height: vy)
            newPositions[node.id] = pos
        }

        positions = newPositions
        velocities = newVelocities
        alpha *= alphaCooling
    }
}

// MARK: - Graph node view

private struct GraphNodeView: View {
    let node: GraphNode
    var selected: Bool

    private var sz: CGFloat {
        switch node.kind {
        case .agent:    return 22
        case .skill:    return 17
        case .tool:     return 10
        case .artifact: return 8
        }
    }

    var body: some View {
        ZStack {
            if node.kind == .agent || node.kind == .skill {
                Circle()
                    .fill(nodeColor.opacity(0.18))
                    .overlay(Circle().strokeBorder(nodeColor.opacity(selected ? 0.8 : 0.4), lineWidth: selected ? 1.5 : 0.5))
                    .frame(width: sz * 2, height: sz * 2)
                    .shadow(color: selected ? nodeColor.opacity(0.5) : .clear, radius: 8)
            } else {
                RoundedRectangle(cornerRadius: 2)
                    .fill(nodeColor.opacity(0.25))
                    .frame(width: sz, height: sz)
            }

            if node.kind == .agent {
                Image(systemName: "brain")
                    .font(.system(size: 9))
                    .foregroundStyle(nodeColor)
            }
        }
        .overlay(alignment: .bottom) {
            if node.kind == .skill {
                Text(node.label)
                    .font(.system(size: 8, design: .monospaced))
                    .foregroundStyle(DesignTokens.Foreground.tertiary)
                    .lineLimit(1)
                    .fixedSize()
                    .offset(y: sz + 10)
            }
        }
    }

    private var nodeColor: Color {
        switch node.status {
        case .running: return node.phase?.color ?? DesignTokens.Gate.pending
        case .done:    return DesignTokens.Gate.passed
        case .failed:  return DesignTokens.Gate.failed
        case .pending: return DesignTokens.Foreground.tertiary
        }
    }
}

// MARK: - Node inspector panel

private struct NodeInspectorPanel: View {
    let node: GraphNode

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            OverlineLabel(text: node.kind == .agent ? "Agent" : node.kind == .skill ? "Skill" : "Tool")
            Text(node.label)
                .font(.system(size: 11, weight: .semibold, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.primary)
                .lineLimit(2)
            HStack(spacing: 6) {
                StatusDot(color: node.status == .running ? DesignTokens.Gate.pending
                          : node.status == .done ? DesignTokens.Gate.passed
                          : DesignTokens.Gate.failed,
                          live: node.status == .running)
                Text(node.status.rawValue)
                    .font(.system(size: 10))
                    .foregroundStyle(DesignTokens.Foreground.secondary)
            }
            if let phase = node.phase {
                PhaseChip(phase: phase)
            }
        }
    }
}

// MARK: - Event timeline

struct EventTimelineView: View {
    let events: [BuilderEvent]
    @State private var scrubPosition: Double = 1.0

    private var maxTimestamp: Double { events.map(\.timestamp).max() ?? 60 }

    var body: some View {
        VStack(spacing: 0) {
            // Scrubber
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text("t=\(String(format: "%.1f", scrubPosition * maxTimestamp))s")
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundStyle(DesignTokens.Foreground.tertiary)
                    Spacer()
                    Text("\(Int(maxTimestamp))s total")
                        .font(.system(size: 10))
                        .foregroundStyle(DesignTokens.Foreground.quaternary)
                }
                Slider(value: $scrubPosition, in: 0...1)
                    .tint(DesignTokens.Phase.definition)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(DesignTokens.Background.sunken)
            .overlay(alignment: .bottom) {
                Rectangle().fill(DesignTokens.Hairline.soft).frame(height: 0.5)
            }

            // Event list
            let cutoff = scrubPosition * maxTimestamp
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 2) {
                    ForEach(events.filter { $0.timestamp <= cutoff }) { event in
                        EventRow(event: event)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
            }
        }
    }
}

private struct EventRow: View {
    let event: BuilderEvent

    var body: some View {
        HStack(spacing: 8) {
            Text(String(format: "%.1f", event.timestamp))
                .font(.system(size: 9, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.quaternary)
                .frame(width: 32, alignment: .trailing)

            Circle()
                .fill(kindColor)
                .frame(width: 5, height: 5)

            Text(event.label)
                .font(.system(size: 10, design: .monospaced))
                .foregroundStyle(DesignTokens.Foreground.secondary)
                .lineLimit(1)

            Spacer(minLength: 0)

            if let tokens = event.tokens {
                Text("\(tokens)t")
                    .font(.system(size: 9))
                    .foregroundStyle(DesignTokens.Foreground.quaternary)
            }
        }
        .padding(.vertical, 2)
    }

    private var kindColor: Color {
        switch event.kind {
        case .phaseTransition: return event.phase?.color ?? DesignTokens.Foreground.tertiary
        case .gate:            return DesignTokens.Gate.pending
        case .tool:            return DesignTokens.Phase.definition
        case .llm:             return DesignTokens.Provider.claude
        case .file:            return DesignTokens.Phase.application
        case .skill:           return DesignTokens.Phase.evaluation
        }
    }
}

// MARK: - Live tail

struct LiveTailView: View {
    let events: [BuilderEvent]
    @State private var counter = 0

    private var tailLines: [String] {
        events.map { e in
            let ts = String(format: "%06.2f", e.timestamp)
            let actor = e.actor.map { " [\($0)]" } ?? ""
            return "[\(ts)]\(actor) \(e.label)"
        }
    }

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 2) {
                    ForEach(Array(tailLines.enumerated()), id: \.offset) { idx, line in
                        HStack(spacing: 0) {
                            Text(line)
                                .font(.system(size: 10, design: .monospaced))
                                .foregroundStyle(idx == tailLines.count - 1
                                    ? DesignTokens.Foreground.primary
                                    : DesignTokens.Foreground.tertiary)
                            if idx == tailLines.count - 1 {
                                Rectangle()
                                    .fill(DesignTokens.Phase.application)
                                    .frame(width: 6, height: 11)
                                    .opacity(counter % 2 == 0 ? 1 : 0)
                            }
                        }
                        .id(idx)
                    }
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .background(DesignTokens.Background.base)
            .onAppear {
                proxy.scrollTo(tailLines.count - 1, anchor: .bottom)
                // Blinking cursor
                Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
                    MainActor.assumeIsolated { counter += 1 }
                }
            }
        }
    }
}
