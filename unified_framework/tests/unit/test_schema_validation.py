"""
Unit tests for schema validation functionality
Linear Project: 4d649a6501f7
Task: TEST-001 - Unit Test Framework for Schema Bridge

Tests cover:
- JSON Schema validation
- Custom validation rules
- Schema compatibility checks
- Validation error messages
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
import jsonschema
from jsonschema import ValidationError, SchemaError

from unified_framework.core.schema_bridge import (
    SchemaDefinition,
    SchemaFormat,
    SchemaMetadata,
    SchemaNamespace,
    SchemaRegistry,
    SchemaUnifier,
    initialize_schema_bridge,
)


# Fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "schemas"


@pytest.fixture
def sample_idfw_document() -> Dict[str, Any]:
    """Load sample IDFW document fixture"""
    with open(FIXTURES_DIR / "sample_idfw_document.json") as f:
        return json.load(f)


@pytest.fixture
def sample_force_tool() -> Dict[str, Any]:
    """Load sample FORCE tool fixture"""
    with open(FIXTURES_DIR / "sample_force_tool.json") as f:
        return json.load(f)


@pytest.fixture
def invalid_schema() -> Dict[str, Any]:
    """Load invalid schema fixture"""
    with open(FIXTURES_DIR / "invalid_schema.json") as f:
        return json.load(f)


@pytest.fixture
def strict_schema() -> SchemaDefinition:
    """Create a strict schema for validation testing"""
    return SchemaDefinition(
        metadata=SchemaMetadata(
            name="strict_test",
            version="1.0.0",
            format=SchemaFormat.IDFW_DOCUMENT,
            namespace=SchemaNamespace.IDFW,
            description="Strict schema for validation tests",
        ),
        schema={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100,
                },
                "description": {
                    "type": "string",
                },
                "version": {
                    "type": "string",
                    "pattern": r"^\d+\.\d+\.\d+$",
                },
                "status": {
                    "type": "string",
                    "enum": ["draft", "review", "published"],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True,
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "author": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                    },
                    "required": ["author"],
                },
            },
            "required": ["title", "version", "status"],
            "additionalProperties": False,
        },
    )


@pytest.fixture
def permissive_schema() -> SchemaDefinition:
    """Create a permissive schema for validation testing"""
    return SchemaDefinition(
        metadata=SchemaMetadata(
            name="permissive_test",
            version="1.0.0",
            format=SchemaFormat.UNIFIED_WORKFLOW,
            namespace=SchemaNamespace.UNIFIED,
            description="Permissive schema for validation tests",
        ),
        schema={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "data": {},  # Any type allowed
            },
            "required": [],
            "additionalProperties": True,
        },
    )


class TestBasicValidation:
    """Tests for basic JSON Schema validation"""

    def test_validate_valid_simple_data(self, strict_schema: SchemaDefinition):
        """Test validating simple valid data"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Valid Document",
            "version": "1.0.0",
            "status": "draft",
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is True
        assert error is None

    def test_validate_missing_required_field(self, strict_schema: SchemaDefinition):
        """Test validation fails when required field is missing"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Missing Fields",
            # Missing 'version' and 'status' (required)
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        assert "version" in error.lower() or "required" in error.lower()

    def test_validate_wrong_type(self, strict_schema: SchemaDefinition):
        """Test validation fails when field has wrong type"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": 123,  # Should be string, not number
            "version": "1.0.0",
            "status": "draft",
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        assert "type" in error.lower() or "string" in error.lower()

    def test_validate_additional_properties_forbidden(self, strict_schema: SchemaDefinition):
        """Test validation fails with additional properties when forbidden"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Valid Document",
            "version": "1.0.0",
            "status": "draft",
            "extra_field": "not allowed",  # additionalProperties: false
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        assert "additional" in error.lower() or "extra_field" in error.lower()

    def test_validate_additional_properties_allowed(self, permissive_schema: SchemaDefinition):
        """Test validation passes with additional properties when allowed"""
        registry = SchemaRegistry()
        registry.register_schema(permissive_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "name": "Test",
            "extra_field": "allowed",
            "another_field": 123,
        }

        is_valid, error = unifier.validate(
            data,
            permissive_schema.metadata.namespace,
            permissive_schema.metadata.name,
        )

        assert is_valid is True
        assert error is None


class TestStringValidation:
    """Tests for string validation constraints"""

    def test_validate_string_min_length(self, strict_schema: SchemaDefinition):
        """Test string minimum length validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "",  # minLength: 1, so empty string fails
            "version": "1.0.0",
            "status": "draft",
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_string_max_length(self, strict_schema: SchemaDefinition):
        """Test string maximum length validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "x" * 101,  # maxLength: 100, so 101 chars fails
            "version": "1.0.0",
            "status": "draft",
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_string_pattern(self, strict_schema: SchemaDefinition):
        """Test string pattern (regex) validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        # Invalid version format (should be x.y.z)
        data = {
            "title": "Test",
            "version": "1.0",  # Should be x.y.z format
            "status": "draft",
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_string_enum(self, strict_schema: SchemaDefinition):
        """Test string enum validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        # Invalid status value (not in enum)
        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "invalid_status",  # Not in ["draft", "review", "published"]
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None


class TestArrayValidation:
    """Tests for array validation constraints"""

    def test_validate_array_items_type(self, strict_schema: SchemaDefinition):
        """Test array items type validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "draft",
            "tags": ["valid", 123, "string"],  # 123 is not a string
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_array_unique_items(self, strict_schema: SchemaDefinition):
        """Test array unique items validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "draft",
            "tags": ["tag1", "tag2", "tag1"],  # Duplicate "tag1"
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None

    def test_validate_array_valid(self, strict_schema: SchemaDefinition):
        """Test valid array passes validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "draft",
            "tags": ["tag1", "tag2", "tag3"],  # All unique strings
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is True
        assert error is None


class TestNestedObjectValidation:
    """Tests for nested object validation"""

    def test_validate_nested_object_valid(self, strict_schema: SchemaDefinition):
        """Test valid nested object passes validation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "draft",
            "metadata": {
                "author": "Test Author",
                "created_at": "2025-09-29T00:00:00Z",
            },
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is True
        assert error is None

    def test_validate_nested_object_missing_required(self, strict_schema: SchemaDefinition):
        """Test nested object fails when required field is missing"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "draft",
            "metadata": {
                # Missing 'author' (required)
                "created_at": "2025-09-29T00:00:00Z",
            },
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        assert "author" in error.lower() or "required" in error.lower()

    def test_validate_nested_object_wrong_type(self, strict_schema: SchemaDefinition):
        """Test nested object fails when field has wrong type"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "draft",
            "metadata": {
                "author": 123,  # Should be string
                "created_at": "2025-09-29T00:00:00Z",
            },
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None


class TestSchemaCompatibility:
    """Tests for schema compatibility checks"""

    def test_compatible_schemas_same_properties(self):
        """Test schemas with same properties are compatible"""
        schema1 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema1",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "number"},
                },
            },
        )

        schema2 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema2",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "number"},
                },
            },
        )

        # Data that validates against both schemas
        data = {"name": "test", "value": 42}

        registry = SchemaRegistry()
        registry.register_schema(schema1)
        registry.register_schema(schema2)
        unifier = SchemaUnifier(registry)

        is_valid1, _ = unifier.validate(data, schema1.metadata.namespace.value, schema1.metadata.name)
        is_valid2, _ = unifier.validate(data, schema2.metadata.namespace.value, schema2.metadata.name)

        assert is_valid1 is True
        assert is_valid2 is True

    def test_incompatible_schemas_different_types(self):
        """Test schemas with different types for same field are incompatible"""
        schema1 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema1",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                },
            },
        )

        schema2 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema2",
                version="1.0.0",
                format=SchemaFormat.FORCE_TOOL,
                namespace=SchemaNamespace.FORCE,
            ),
            schema={
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                },
            },
        )

        # Data that validates against schema1 (number)
        data1 = {"value": 42}

        # Data that validates against schema2 (string)
        data2 = {"value": "42"}

        registry = SchemaRegistry()
        registry.register_schema(schema1)
        registry.register_schema(schema2)
        unifier = SchemaUnifier(registry)

        # data1 should only validate against schema1
        is_valid1, _ = unifier.validate(data1, schema1.metadata.namespace.value, schema1.metadata.name)
        is_valid2, _ = unifier.validate(data1, schema2.metadata.namespace.value, schema2.metadata.name)

        assert is_valid1 is True
        assert is_valid2 is False

        # data2 should only validate against schema2
        is_valid1, _ = unifier.validate(data2, schema1.metadata.namespace.value, schema1.metadata.name)
        is_valid2, _ = unifier.validate(data2, schema2.metadata.namespace.value, schema2.metadata.name)

        assert is_valid1 is False
        assert is_valid2 is True

    def test_backward_compatible_schema_evolution(self):
        """Test backward compatible schema evolution (adding optional fields)"""
        # Original schema (v1)
        schema_v1 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="evolving",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        )

        # Evolved schema (v2) - adds optional field
        schema_v2 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="evolving_v2",
                version="2.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},  # New optional field
                },
                "required": ["name"],
            },
        )

        # Data from v1 (without new field)
        old_data = {"name": "Test"}

        registry = SchemaRegistry()
        registry.register_schema(schema_v1)
        registry.register_schema(schema_v2)
        unifier = SchemaUnifier(registry)

        # Old data should validate against both schemas (backward compatible)
        is_valid_v1, _ = unifier.validate(old_data, schema_v1.metadata.namespace.value, schema_v1.metadata.name)
        is_valid_v2, _ = unifier.validate(old_data, schema_v2.metadata.namespace.value, schema_v2.metadata.name)

        assert is_valid_v1 is True
        assert is_valid_v2 is True


class TestValidationErrorMessages:
    """Tests for validation error message quality"""

    def test_error_message_missing_required(self, strict_schema: SchemaDefinition):
        """Test error message clearly indicates missing required field"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {"title": "Test"}  # Missing required 'version' and 'status'

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        # Error should mention the missing field
        assert "version" in error or "status" in error or "required" in error.lower()

    def test_error_message_type_mismatch(self, strict_schema: SchemaDefinition):
        """Test error message clearly indicates type mismatch"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": 123,  # Should be string
            "version": "1.0.0",
            "status": "draft",
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        # Error should mention type issue
        assert "type" in error.lower() or "string" in error.lower()

    def test_error_message_pattern_violation(self, strict_schema: SchemaDefinition):
        """Test error message for pattern violation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "invalid_version",  # Doesn't match x.y.z pattern
            "status": "draft",
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        # Error should mention pattern
        assert "pattern" in error.lower() or "format" in error.lower()

    def test_error_message_enum_violation(self, strict_schema: SchemaDefinition):
        """Test error message for enum violation"""
        registry = SchemaRegistry()
        registry.register_schema(strict_schema)
        unifier = SchemaUnifier(registry)

        data = {
            "title": "Test",
            "version": "1.0.0",
            "status": "invalid",  # Not in enum
        }

        is_valid, error = unifier.validate(
            data,
            strict_schema.metadata.namespace,
            strict_schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None
        # Error should mention enum or valid values
        assert "enum" in error.lower() or "not one of" in error.lower()


class TestRealWorldSchemas:
    """Tests using real-world schema examples"""

    def test_validate_sample_idfw_document(self, sample_idfw_document: Dict[str, Any]):
        """Test validating sample IDFW document"""
        # Create schema based on IDFW document structure
        schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="idfw_document_schema",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "variables": {"type": "object"},
                    "sections": {"type": "array"},
                    "metadata": {"type": "object"},
                },
                "required": ["title", "description"],
            },
        )

        registry = SchemaRegistry()
        registry.register_schema(schema)
        unifier = SchemaUnifier(registry)

        is_valid, error = unifier.validate(
            sample_idfw_document,
            schema.metadata.namespace.value,
            schema.metadata.name,
        )

        assert is_valid is True, f"Validation failed: {error}"
        assert error is None

    def test_validate_sample_force_tool(self, sample_force_tool: Dict[str, Any]):
        """Test validating sample FORCE tool"""
        # Create schema based on FORCE tool structure
        schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="force_tool_schema",
                version="1.0.0",
                format=SchemaFormat.FORCE_TOOL,
                namespace=SchemaNamespace.FORCE,
            ),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "parameters": {"type": "object"},
                    "execution": {"type": "object"},
                    "metadata": {"type": "object"},
                },
                "required": ["name", "description", "parameters"],
            },
        )

        registry = SchemaRegistry()
        registry.register_schema(schema)
        unifier = SchemaUnifier(registry)

        is_valid, error = unifier.validate(
            sample_force_tool,
            schema.metadata.namespace.value,
            schema.metadata.name,
        )

        assert is_valid is True, f"Validation failed: {error}"
        assert error is None

    def test_validate_invalid_schema_fixture(self, invalid_schema: Dict[str, Any]):
        """Test that invalid schema fixture fails validation"""
        # Create a proper schema to validate against
        schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="proper_schema",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["title", "description"],
            },
        )

        registry = SchemaRegistry()
        registry.register_schema(schema)
        unifier = SchemaUnifier(registry)

        is_valid, error = unifier.validate(
            invalid_schema,
            schema.metadata.namespace.value,
            schema.metadata.name,
        )

        assert is_valid is False
        assert error is not None


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_validate_empty_object(self, permissive_schema: SchemaDefinition):
        """Test validating empty object"""
        registry = SchemaRegistry()
        registry.register_schema(permissive_schema)
        unifier = SchemaUnifier(registry)

        data = {}

        is_valid, error = unifier.validate(
            data,
            permissive_schema.metadata.namespace.value,
            permissive_schema.metadata.name,
        )

        assert is_valid is True  # No required fields
        assert error is None

    def test_validate_null_values(self):
        """Test validating null values"""
        schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="nullable_test",
                version="1.0.0",
                format=SchemaFormat.UNIFIED_WORKFLOW,
                namespace=SchemaNamespace.UNIFIED,
            ),
            schema={
                "type": "object",
                "properties": {
                    "nullable_field": {"type": ["string", "null"]},
                    "required_field": {"type": "string"},
                },
                "required": ["required_field"],
            },
        )

        registry = SchemaRegistry()
        registry.register_schema(schema)
        unifier = SchemaUnifier(registry)

        # Null value in nullable field should pass
        data = {"nullable_field": None, "required_field": "present"}

        is_valid, error = unifier.validate(data, schema.metadata.namespace.value, schema.metadata.name)

        assert is_valid is True, f"Validation failed: {error}"
        assert error is None

    def test_validate_deeply_nested_structure(self):
        """Test validating deeply nested object structure"""
        schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="deeply_nested",
                version="1.0.0",
                format=SchemaFormat.UNIFIED_WORKFLOW,
                namespace=SchemaNamespace.UNIFIED,
            ),
            schema={
                "type": "object",
                "properties": {
                    "level1": {
                        "type": "object",
                        "properties": {
                            "level2": {
                                "type": "object",
                                "properties": {
                                    "level3": {
                                        "type": "object",
                                        "properties": {
                                            "value": {"type": "string"},
                                        },
                                        "required": ["value"],
                                    },
                                },
                                "required": ["level3"],
                            },
                        },
                        "required": ["level2"],
                    },
                },
                "required": ["level1"],
            },
        )

        registry = SchemaRegistry()
        registry.register_schema(schema)
        unifier = SchemaUnifier(registry)

        # Valid deeply nested structure
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep",
                    },
                },
            },
        }

        is_valid, error = unifier.validate(data, schema.metadata.namespace.value, schema.metadata.name)

        assert is_valid is True, f"Validation failed: {error}"
        assert error is None

    def test_validate_large_array(self):
        """Test validating large array"""
        schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="large_array",
                version="1.0.0",
                format=SchemaFormat.UNIFIED_WORKFLOW,
                namespace=SchemaNamespace.UNIFIED,
            ),
            schema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                },
            },
        )

        registry = SchemaRegistry()
        registry.register_schema(schema)
        unifier = SchemaUnifier(registry)

        # Large array with 1000 items
        data = {"items": list(range(1000))}

        is_valid, error = unifier.validate(data, schema.metadata.namespace.value, schema.metadata.name)

        assert is_valid is True, f"Validation failed: {error}"
        assert error is None