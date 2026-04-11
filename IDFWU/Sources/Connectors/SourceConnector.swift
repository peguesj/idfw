import Foundation

protocol SourceConnector: Sendable {
    var config: SourceConnectorConfig { get }
    func documents() -> AsyncThrowingStream<RawDocument, Error>
    func validate() async throws
}
