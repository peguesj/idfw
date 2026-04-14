import SwiftUI

struct SchemaTypeBadge: View {
    let schemaType: IDEASchemaType

    var body: some View {
        Text(schemaType.displayName)
            .font(.caption2.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .foregroundStyle(schemaType.accentColor)
            .background(
                schemaType.accentColor.opacity(0.15),
                in: Capsule()
            )
            .overlay {
                Capsule()
                    .strokeBorder(schemaType.accentColor.opacity(0.3), lineWidth: 0.5)
            }
    }
}

#Preview {
    HStack(spacing: 8) {
        ForEach(IDEASchemaType.allCases, id: \.self) { type in
            SchemaTypeBadge(schemaType: type)
        }
    }
    .padding()
}
