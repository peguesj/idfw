import Foundation

extension Data {
    /// Returns a copy of this Data with JSONC-style comments stripped.
    /// Removes single-line comments (//) and block comments (/* ... */).
    /// Respects string literals so comments inside quoted strings are preserved.
    func strippingJSONCComments() -> Data {
        guard let source = String(data: self, encoding: .utf8) else {
            return self
        }

        var result = String()
        result.reserveCapacity(source.count)

        var index = source.startIndex
        let end = source.endIndex

        while index < end {
            let char = source[index]

            // String literal — copy verbatim until closing quote
            if char == "\"" {
                result.append(char)
                index = source.index(after: index)
                while index < end {
                    let inner = source[index]
                    result.append(inner)
                    if inner == "\\" {
                        // Skip escaped character
                        index = source.index(after: index)
                        if index < end {
                            result.append(source[index])
                            index = source.index(after: index)
                        }
                        continue
                    }
                    if inner == "\"" {
                        index = source.index(after: index)
                        break
                    }
                    index = source.index(after: index)
                }
                continue
            }

            // Check for comment start
            if char == "/" {
                let next = source.index(after: index)
                if next < end {
                    let nextChar = source[next]

                    // Single-line comment
                    if nextChar == "/" {
                        // Skip until end of line
                        var scan = source.index(after: next)
                        while scan < end && source[scan] != "\n" {
                            scan = source.index(after: scan)
                        }
                        // Preserve the newline
                        if scan < end {
                            result.append("\n")
                            scan = source.index(after: scan)
                        }
                        index = scan
                        continue
                    }

                    // Block comment
                    if nextChar == "*" {
                        var scan = source.index(after: next)
                        while scan < end {
                            if source[scan] == "*" {
                                let afterStar = source.index(after: scan)
                                if afterStar < end && source[afterStar] == "/" {
                                    scan = source.index(after: afterStar)
                                    break
                                }
                            }
                            scan = source.index(after: scan)
                        }
                        // Replace block comment with a space to preserve token separation
                        result.append(" ")
                        index = scan
                        continue
                    }
                }
            }

            result.append(char)
            index = source.index(after: index)
        }

        return Data(result.utf8)
    }
}
