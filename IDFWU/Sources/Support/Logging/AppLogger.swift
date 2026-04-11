import Foundation
import os

enum AppLogger {
    static let app = Logger(subsystem: subsystem, category: "app")
    static let network = Logger(subsystem: subsystem, category: "network")
    static let parser = Logger(subsystem: subsystem, category: "parser")
    static let persistence = Logger(subsystem: subsystem, category: "persistence")

    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.inceptionglass"
}
