// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "IDFWU",
    platforms: [
        .macOS(.v15)
    ],
    products: [
        .executable(name: "IDFWU", targets: ["IDFWU"])
    ],
    targets: [
        .executableTarget(
            name: "IDFWU",
            path: "Sources",
            resources: [
                .process("Resources"),
                .copy("Support/IDFWU.entitlements")
            ]
        )
    ]
)
