import Foundation

enum AccessibilityIdentifiers {
    enum Projects {
        static let list = "projects.list"
        static let row = "projects.row"
        static let addButton = "projects.addButton"
    }

    enum ConnectorSetup {
        static let sheet = "connectorSetup.sheet"
        static let nameField = "connectorSetup.nameField"
        static let kindPicker = "connectorSetup.kindPicker"
        static let localPathField = "connectorSetup.localPathField"
        static let githubURLField = "connectorSetup.githubURLField"
        static let saveButton = "connectorSetup.saveButton"
    }

    enum SchemaDetail {
        static let container = "schemaDetail.container"
        static let overviewTab = "schemaDetail.overviewTab"
        static let diagramsTab = "schemaDetail.diagramsTab"
        static let gatesTab = "schemaDetail.gatesTab"
        static let rawJSONTab = "schemaDetail.rawJSONTab"
    }

    enum Diagram {
        static let container = "diagram.container"
        static let canvas = "diagram.canvas"
        static let exportButton = "diagram.exportButton"
    }

    enum Gate {
        static let container = "gate.container"
        static let row = "gate.row"
    }

    enum Document {
        static let container = "document.container"
    }

    enum EventStream {
        static let panel = "eventStream.panel"
        static let row = "eventStream.row"
    }
}
