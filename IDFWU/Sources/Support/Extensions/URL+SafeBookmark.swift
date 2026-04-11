import Foundation

extension URL {
    /// Create a security-scoped bookmark for this URL.
    func createSecurityScopedBookmark() throws -> Data {
        try bookmarkData(
            options: .withSecurityScope,
            includingResourceValuesForKeys: nil,
            relativeTo: nil
        )
    }

    /// Resolve a security-scoped bookmark back to a URL.
    static func resolveSecurityScopedBookmark(_ data: Data) throws -> (URL, Bool) {
        var isStale = false
        let url = try URL(
            resolvingBookmarkData: data,
            options: .withSecurityScope,
            relativeTo: nil,
            bookmarkDataIsStale: &isStale
        )
        return (url, isStale)
    }

    /// Convenience: start + stop security scope around a closure.
    func accessSecurityScoped<T>(_ body: (URL) throws -> T) rethrows -> T {
        let didStart = startAccessingSecurityScopedResource()
        defer { if didStart { stopAccessingSecurityScopedResource() } }
        return try body(self)
    }
}
