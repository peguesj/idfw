import Foundation

enum IDEADocumentParserError: LocalizedError {
    case invalidJSON
    case unrecognizedSchema
    case notADictionary

    var errorDescription: String? {
        switch self {
        case .invalidJSON:
            return "The data is not valid JSON."
        case .unrecognizedSchema:
            return "Could not determine the IDEA schema type from the document."
        case .notADictionary:
            return "Top-level JSON value is not a dictionary."
        }
    }
}

enum IDEADocumentParser {
    /// Parse a RawDocument into a typed IDEADocument.
    /// Strips JSONC comments before parsing. Uses the RawDocument's detectedType if present,
    /// otherwise resolves via SchemaTypeResolver.
    static func parse(_ raw: RawDocument) throws -> IDEADocument {
        let cleanData = raw.data.strippingJSONCComments()

        guard let jsonObject = try? JSONSerialization.jsonObject(with: cleanData) else {
            throw IDEADocumentParserError.invalidJSON
        }

        guard let dictionary = jsonObject as? [String: Any] else {
            throw IDEADocumentParserError.notADictionary
        }

        let schemaType: IDEASchemaType
        if let detected = raw.detectedType {
            schemaType = detected
        } else if let resolved = SchemaTypeResolver.resolve(from: dictionary) {
            schemaType = resolved
        } else {
            throw IDEADocumentParserError.unrecognizedSchema
        }

        return IDEADocument.from(type: schemaType, payload: dictionary)
    }
}
