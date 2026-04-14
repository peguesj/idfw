import SwiftUI
import SwiftData

@main
struct IDFWUApp: App {
    @State private var router = NavigationRouter()
    @State private var scanRootStore = ScanRootStore.shared
    @State private var discoveryManager = ProjectDiscoveryManager()
    @State private var eventStreamState = EventStreamState()
    @State private var eventStreamVM = EventStreamViewModel()
    @State private var toastNotifier = ToastNotifier()
    @State private var recentProjectsStore = RecentProjectsStore.shared
    @AppStorage("lastSplashVersion") private var lastSplashVersion: String = ""
    @State private var showSplash = false

    private let sseURL = URL(string: "http://localhost:4040/api/v3/events")!

    private var currentShortVersion: String {
        (Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String) ?? "0"
    }

    var body: some Scene {
        WindowGroup(id: "main") {
            ZStack {
                RootView()
                    .environment(router)
                    .environment(scanRootStore)
                    .environment(discoveryManager)
                    .environment(toastNotifier)
                    .environment(recentProjectsStore)
                    .environment(\.eventStreamState, eventStreamState)
                    .task {
                        discoveryManager.scanRootStore = scanRootStore
                        await discoveryManager.refresh()
                        await connectEventStream()
                    }

                if showSplash {
                    SplashView(isPresented: $showSplash)
                        .transition(.opacity)
                        .zIndex(1)
                }
            }
            .onAppear {
                if lastSplashVersion != currentShortVersion {
                    showSplash = true
                }
            }
        }
        .modelContainer(for: [])
        .defaultSize(width: 1100, height: 720)
        .windowResizability(.contentMinSize)
        .handlesExternalEvents(matching: Set(["main"]))
        .commands {
            AppCommands(router: router)
        }

        Settings {
            SettingsView()
                .environment(scanRootStore)
                .environment(discoveryManager)
        }

        MenuBarExtra("IDFWU", systemImage: "cube.transparent.fill") {
            MenuBarView(router: router)
                .environment(toastNotifier)
                .environment(recentProjectsStore)
                .environment(scanRootStore)
        }
        .menuBarExtraStyle(.window)

        Window("IDFWU Help", id: "help") {
            HelpWindowView()
        }
        .defaultSize(width: 780, height: 540)
        .keyboardShortcut("?", modifiers: [.command])
        .commands {
            AppCommands(router: router)
        }
    }

    @MainActor
    private func connectEventStream() async {
        eventStreamState.connectionState = .connecting
        eventStreamVM.connect(to: sseURL)

        // Sync VM state to environment state
        Task {
            // Brief delay to let the connection establish
            try? await Task.sleep(nanoseconds: 500_000_000)
            switch eventStreamVM.connectionState {
            case .connected:
                eventStreamState.connectionState = .connected
                eventStreamState.lastEventTimestamp = Date()
            case .error:
                eventStreamState.connectionState = .disconnected
            case .connecting:
                eventStreamState.connectionState = .connecting
            case .disconnected:
                eventStreamState.connectionState = .disconnected
            }

            // Keep syncing periodically
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 2_000_000_000)
                switch eventStreamVM.connectionState {
                case .connected:
                    eventStreamState.connectionState = .connected
                    if !eventStreamVM.events.isEmpty {
                        eventStreamState.lastEventTimestamp = Date()
                    }
                case .error:
                    eventStreamState.connectionState = .disconnected
                case .connecting:
                    eventStreamState.connectionState = .connecting
                case .disconnected:
                    eventStreamState.connectionState = .disconnected
                }
            }
        }
    }
}

private struct WindowMinSize: ViewModifier {
    func body(content: Content) -> some View {
        content.frame(minWidth: 900, minHeight: 600)
    }
}
