"""
Unit tests for schema_bridge module
Linear Project: 4d649a6501f7
Task: TEST-001 - Unit Test Framework for Schema Bridge

Tests cover:
- SchemaUnifier class initialization
- Schema registration and discovery
- IDFW to FORCE conversion
- FORCE to IDFW conversion
- Schema validation
- Error handling
- Schema merging
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

import pytest
from jsonschema import ValidationError

from unified_framework.core.schema_bridge import (
    ConversionRule,
    SchemaDefinition,
    SchemaFormat,
    SchemaMetadata,
    SchemaNamespace,
    SchemaRegistry,
    SchemaUnifier,
    create_default_conversion_rules,
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
def sample_metadata() -> SchemaMetadata:
    """Create sample schema metadata"""
    return SchemaMetadata(
        name="test_schema",
        version="1.0.0",
        format=SchemaFormat.IDFW_DOCUMENT,
        namespace=SchemaNamespace.IDFW,
        description="Test schema for unit tests",
        tags=["test", "sample"],
    )


@pytest.fixture
def sample_schema_def(sample_metadata: SchemaMetadata) -> SchemaDefinition:
    """Create sample schema definition"""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "version": {"type": "string"},
        },
        "required": ["title"],
    }
    return SchemaDefinition(
        metadata=sample_metadata,
        schema=schema,
        examples=[{"title": "Example", "description": "Sample"}],
    )


@pytest.fixture
def empty_registry() -> SchemaRegistry:
    """Create empty schema registry"""
    return SchemaRegistry()


@pytest.fixture
def populated_registry(sample_schema_def: SchemaDefinition) -> SchemaRegistry:
    """Create registry with sample schema"""
    registry = SchemaRegistry()
    registry.register_schema(sample_schema_def)
    return registry


@pytest.fixture
def schema_unifier(populated_registry: SchemaRegistry) -> SchemaUnifier:
    """Create SchemaUnifier with populated registry"""
    return SchemaUnifier(populated_registry)


class TestSchemaMetadata:
    """Tests for SchemaMetadata class"""

    def test_create_minimal_metadata(self):
        """Test creating metadata with minimal required fields"""
        metadata = SchemaMetadata(
            name="minimal",
            version="1.0.0",
            format=SchemaFormat.IDFW_DOCUMENT,
            namespace=SchemaNamespace.IDFW,
        )
        assert metadata.name == "minimal"
        assert metadata.version == "1.0.0"
        assert metadata.format == SchemaFormat.IDFW_DOCUMENT
        assert metadata.namespace == SchemaNamespace.IDFW
        assert metadata.description is None
        assert metadata.tags == []
        assert metadata.deprecated is False
        assert metadata.replacement is None

    def test_create_full_metadata(self):
        """Test creating metadata with all fields"""
        metadata = SchemaMetadata(
            name="full",
            version="2.0.0",
            format=SchemaFormat.FORCE_TOOL,
            namespace=SchemaNamespace.FORCE,
            description="Full metadata test",
            tags=["test", "full"],
            deprecated=True,
            replacement="new_schema",
        )
        assert metadata.name == "full"
        assert metadata.version == "2.0.0"
        assert metadata.deprecated is True
        assert metadata.replacement == "new_schema"
        assert len(metadata.tags) == 2

    def test_metadata_enum_values(self):
        """Test that enum values are validated"""
        # Valid enum values should work
        metadata = SchemaMetadata(
            name="test",
            version="1.0.0",
            format=SchemaFormat.UNIFIED_COMMAND,
            namespace=SchemaNamespace.UNIFIED,
        )
        assert metadata.format == SchemaFormat.UNIFIED_COMMAND
        assert metadata.namespace == SchemaNamespace.UNIFIED


class TestSchemaDefinition:
    """Tests for SchemaDefinition class"""

    def test_create_schema_definition(self, sample_metadata: SchemaMetadata):
        """Test creating schema definition"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        schema_def = SchemaDefinition(
            metadata=sample_metadata,
            schema=schema,
        )
        assert schema_def.metadata == sample_metadata
        assert schema_def.schema_def == schema
        assert schema_def.examples == []

    def test_schema_validation_adds_schema_version(self):
        """Test that validator adds $schema if missing"""
        metadata = SchemaMetadata(
            name="test",
            version="1.0.0",
            format=SchemaFormat.IDFW_DOCUMENT,
            namespace=SchemaNamespace.IDFW,
        )
        schema = {"type": "object"}  # Missing $schema
        schema_def = SchemaDefinition(metadata=metadata, schema=schema)
        assert "$schema" in schema_def.schema_def
        assert schema_def.schema_def["$schema"] == "http://json-schema.org/draft-07/schema#"

    def test_schema_with_examples(self, sample_metadata: SchemaMetadata):
        """Test schema definition with examples"""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        examples = [{"name": "Example 1"}, {"name": "Example 2"}]
        schema_def = SchemaDefinition(
            metadata=sample_metadata,
            schema=schema,
            examples=examples,
        )
        assert len(schema_def.examples) == 2
        assert schema_def.examples[0]["name"] == "Example 1"


class TestConversionRule:
    """Tests for ConversionRule class"""

    def test_create_conversion_rule(self):
        """Test creating conversion rule"""
        rule = ConversionRule(
            source_format=SchemaFormat.IDFW_DOCUMENT,
            target_format=SchemaFormat.UNIFIED_WORKFLOW,
            field_mappings={"title": "name", "description": "description"},
        )
        assert rule.source_format == SchemaFormat.IDFW_DOCUMENT
        assert rule.target_format == SchemaFormat.UNIFIED_WORKFLOW
        assert rule.field_mappings["title"] == "name"
        assert rule.transformations == {}
        assert rule.defaults == {}

    def test_conversion_rule_with_transformations(self):
        """Test conversion rule with transformations"""
        rule = ConversionRule(
            source_format=SchemaFormat.FORCE_TOOL,
            target_format=SchemaFormat.UNIFIED_COMMAND,
            field_mappings={"name": "command_name"},
            transformations={"command_name": "lowercase"},
            defaults={"prefix": "$"},
        )
        assert rule.transformations["command_name"] == "lowercase"
        assert rule.defaults["prefix"] == "$"


class TestSchemaRegistry:
    """Tests for SchemaRegistry class"""

    def test_empty_registry_initialization(self, empty_registry: SchemaRegistry):
        """Test initializing empty registry"""
        assert len(empty_registry.schemas) == 0
        assert len(empty_registry.conversion_rules) == 0

    def test_register_schema(self, empty_registry: SchemaRegistry, sample_schema_def: SchemaDefinition):
        """Test registering a schema"""
        empty_registry.register_schema(sample_schema_def)
        assert len(empty_registry.schemas) == 1
        key = f"{sample_schema_def.metadata.namespace.value}:{sample_schema_def.metadata.name}"
        assert key in empty_registry.schemas

    def test_get_schema(self, populated_registry: SchemaRegistry, sample_schema_def: SchemaDefinition):
        """Test retrieving a schema by namespace and name"""
        schema = populated_registry.get_schema(
            sample_schema_def.metadata.namespace.value,
            sample_schema_def.metadata.name,
        )
        assert schema is not None
        assert schema.metadata.name == sample_schema_def.metadata.name

    def test_get_nonexistent_schema(self, populated_registry: SchemaRegistry):
        """Test retrieving nonexistent schema returns None"""
        schema = populated_registry.get_schema("nonexistent", "schema")
        assert schema is None

    def test_list_all_schemas(self, populated_registry: SchemaRegistry):
        """Test listing all schemas without filters"""
        schemas = populated_registry.list_schemas()
        assert len(schemas) >= 1

    def test_list_schemas_by_namespace(self):
        """Test filtering schemas by namespace"""
        registry = SchemaRegistry()

        # Register schemas in different namespaces
        idfw_schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="idfw_test",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={"type": "object"},
        )
        force_schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="force_test",
                version="1.0.0",
                format=SchemaFormat.FORCE_TOOL,
                namespace=SchemaNamespace.FORCE,
            ),
            schema={"type": "object"},
        )

        registry.register_schema(idfw_schema)
        registry.register_schema(force_schema)

        # Filter by namespace
        idfw_schemas = registry.list_schemas(namespace=SchemaNamespace.IDFW)
        assert len(idfw_schemas) == 1
        assert idfw_schemas[0].metadata.namespace == SchemaNamespace.IDFW

    def test_list_schemas_by_format(self):
        """Test filtering schemas by format"""
        registry = SchemaRegistry()

        # Register schemas with different formats
        doc_schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="doc",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={"type": "object"},
        )
        tool_schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="tool",
                version="1.0.0",
                format=SchemaFormat.FORCE_TOOL,
                namespace=SchemaNamespace.FORCE,
            ),
            schema={"type": "object"},
        )

        registry.register_schema(doc_schema)
        registry.register_schema(tool_schema)

        # Filter by format
        tool_schemas = registry.list_schemas(format=SchemaFormat.FORCE_TOOL)
        assert len(tool_schemas) == 1
        assert tool_schemas[0].metadata.format == SchemaFormat.FORCE_TOOL

    def test_register_conversion_rule(self, empty_registry: SchemaRegistry):
        """Test registering conversion rule"""
        rule = ConversionRule(
            source_format=SchemaFormat.IDFW_DOCUMENT,
            target_format=SchemaFormat.UNIFIED_WORKFLOW,
            field_mappings={"title": "name"},
        )
        empty_registry.register_conversion_rule(rule)
        assert len(empty_registry.conversion_rules) == 1

    def test_get_conversion_rule(self, empty_registry: SchemaRegistry):
        """Test retrieving conversion rule"""
        rule = ConversionRule(
            source_format=SchemaFormat.IDFW_DOCUMENT,
            target_format=SchemaFormat.UNIFIED_WORKFLOW,
            field_mappings={"title": "name"},
        )
        empty_registry.register_conversion_rule(rule)

        retrieved = empty_registry.get_conversion_rule(
            SchemaFormat.IDFW_DOCUMENT,
            SchemaFormat.UNIFIED_WORKFLOW,
        )
        assert retrieved is not None
        assert retrieved.source_format == SchemaFormat.IDFW_DOCUMENT
        assert retrieved.target_format == SchemaFormat.UNIFIED_WORKFLOW

    def test_get_nonexistent_conversion_rule(self, empty_registry: SchemaRegistry):
        """Test retrieving nonexistent conversion rule returns None"""
        rule = empty_registry.get_conversion_rule(
            SchemaFormat.IDFW_DOCUMENT,
            SchemaFormat.FORCE_TOOL,
        )
        assert rule is None


class TestSchemaUnifier:
    """Tests for SchemaUnifier class"""

    def test_initialization(self, populated_registry: SchemaRegistry):
        """Test SchemaUnifier initialization"""
        unifier = SchemaUnifier(populated_registry)
        assert unifier.registry == populated_registry

    def test_validate_valid_data(self, schema_unifier: SchemaUnifier, sample_schema_def: SchemaDefinition):
        """Test validating valid data against schema"""
        data = {"title": "Test Document", "description": "Test description"}
        is_valid, error = schema_unifier.validate(
            data,
            sample_schema_def.metadata.namespace.value,
            sample_schema_def.metadata.name,
        )
        assert is_valid is True
        assert error is None

    def test_validate_invalid_data(self, schema_unifier: SchemaUnifier, sample_schema_def: SchemaDefinition):
        """Test validating invalid data against schema"""
        data = {"description": "Missing required title field"}
        is_valid, error = schema_unifier.validate(
            data,
            sample_schema_def.metadata.namespace.value,
            sample_schema_def.metadata.name,
        )
        assert is_valid is False
        assert error is not None
        assert "required" in error.lower() or "title" in error.lower()

    def test_validate_nonexistent_schema(self, schema_unifier: SchemaUnifier):
        """Test validating against nonexistent schema"""
        data = {"any": "data"}
        is_valid, error = schema_unifier.validate(data, "nonexistent", "schema")
        assert is_valid is False
        assert "not found" in error.lower()

    def test_convert_with_field_mappings(self):
        """Test converting data with field mappings"""
        registry = SchemaRegistry()
        rule = ConversionRule(
            source_format=SchemaFormat.IDFW_DOCUMENT,
            target_format=SchemaFormat.UNIFIED_WORKFLOW,
            field_mappings={
                "title": "name",
                "description": "description",
                "variables": "parameters",
            },
        )
        registry.register_conversion_rule(rule)

        unifier = SchemaUnifier(registry)
        source_data = {
            "title": "Test Document",
            "description": "Test description",
            "variables": {"key": "value"},
        }

        result = unifier.convert(
            source_data,
            SchemaFormat.IDFW_DOCUMENT,
            SchemaFormat.UNIFIED_WORKFLOW,
        )

        assert result["name"] == "Test Document"
        assert result["description"] == "Test description"
        assert result["parameters"] == {"key": "value"}

    def test_convert_with_defaults(self):
        """Test converting data with default values"""
        registry = SchemaRegistry()
        rule = ConversionRule(
            source_format=SchemaFormat.IDFW_DOCUMENT,
            target_format=SchemaFormat.UNIFIED_WORKFLOW,
            field_mappings={"title": "name"},
            defaults={"version": "1.0.0", "type": "document_workflow"},
        )
        registry.register_conversion_rule(rule)

        unifier = SchemaUnifier(registry)
        source_data = {"title": "Test"}

        result = unifier.convert(
            source_data,
            SchemaFormat.IDFW_DOCUMENT,
            SchemaFormat.UNIFIED_WORKFLOW,
        )

        assert result["name"] == "Test"
        assert result["version"] == "1.0.0"
        assert result["type"] == "document_workflow"

    def test_convert_with_transformations(self):
        """Test converting data with transformations"""
        registry = SchemaRegistry()
        rule = ConversionRule(
            source_format=SchemaFormat.FORCE_TOOL,
            target_format=SchemaFormat.UNIFIED_COMMAND,
            field_mappings={"name": "command_name"},
            transformations={"command_name": "lowercase"},
        )
        registry.register_conversion_rule(rule)

        unifier = SchemaUnifier(registry)
        source_data = {"name": "SampleTool"}

        result = unifier.convert(
            source_data,
            SchemaFormat.FORCE_TOOL,
            SchemaFormat.UNIFIED_COMMAND,
        )

        assert result["command_name"] == "sampletool"

    def test_convert_without_rule_raises_error(self, schema_unifier: SchemaUnifier):
        """Test converting without conversion rule raises error"""
        data = {"any": "data"}

        with pytest.raises(ValueError, match="No conversion rule found"):
            schema_unifier.convert(
                data,
                SchemaFormat.IDFW_DOCUMENT,
                SchemaFormat.FORCE_TOOL,
            )

    def test_apply_transformation_uppercase(self, schema_unifier: SchemaUnifier):
        """Test uppercase transformation"""
        result = schema_unifier._apply_transformation("test", "uppercase")
        assert result == "TEST"

    def test_apply_transformation_lowercase(self, schema_unifier: SchemaUnifier):
        """Test lowercase transformation"""
        result = schema_unifier._apply_transformation("TEST", "lowercase")
        assert result == "test"

    def test_apply_transformation_to_list(self, schema_unifier: SchemaUnifier):
        """Test to_list transformation"""
        result = schema_unifier._apply_transformation("single", "to_list")
        assert result == ["single"]

        result = schema_unifier._apply_transformation(["already", "list"], "to_list")
        assert result == ["already", "list"]

    def test_apply_transformation_to_string(self, schema_unifier: SchemaUnifier):
        """Test to_string transformation"""
        result = schema_unifier._apply_transformation(123, "to_string")
        assert result == "123"

    def test_apply_transformation_to_int(self, schema_unifier: SchemaUnifier):
        """Test to_int transformation"""
        result = schema_unifier._apply_transformation("42", "to_int")
        assert result == 42

    def test_apply_transformation_to_float(self, schema_unifier: SchemaUnifier):
        """Test to_float transformation"""
        result = schema_unifier._apply_transformation("3.14", "to_float")
        assert result == 3.14

    def test_apply_unknown_transformation(self, schema_unifier: SchemaUnifier, caplog):
        """Test unknown transformation returns value unchanged"""
        with caplog.at_level(logging.WARNING):
            result = schema_unifier._apply_transformation("test", "unknown_transform")
            assert result == "test"
            assert "Unknown transformation" in caplog.text

    def test_merge_schemas_single(self):
        """Test merging single schema"""
        registry = SchemaRegistry()
        unifier = SchemaUnifier(registry)

        schema_def = SchemaDefinition(
            metadata=SchemaMetadata(
                name="test",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
                tags=["test"],
            ),
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )

        merged = unifier.merge_schemas([schema_def], "merged_test")

        assert merged.metadata.name == "merged_test"
        assert merged.metadata.namespace == SchemaNamespace.UNIFIED
        assert "name" in merged.schema_def["properties"]
        assert "name" in merged.schema_def["required"]

    def test_merge_schemas_multiple(self):
        """Test merging multiple schemas"""
        registry = SchemaRegistry()
        unifier = SchemaUnifier(registry)

        schema1 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema1",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
                tags=["tag1"],
            ),
            schema={
                "type": "object",
                "properties": {"field1": {"type": "string"}},
                "required": ["field1"],
            },
        )

        schema2 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema2",
                version="1.0.0",
                format=SchemaFormat.FORCE_TOOL,
                namespace=SchemaNamespace.FORCE,
                tags=["tag2"],
            ),
            schema={
                "type": "object",
                "properties": {"field2": {"type": "number"}},
                "required": ["field2"],
            },
        )

        merged = unifier.merge_schemas([schema1, schema2], "merged_multiple")

        assert "field1" in merged.schema_def["properties"]
        assert "field2" in merged.schema_def["properties"]
        assert "field1" in merged.schema_def["required"]
        assert "field2" in merged.schema_def["required"]
        assert set(merged.metadata.tags) == {"tag1", "tag2"}

    def test_merge_schemas_empty_raises_error(self, schema_unifier: SchemaUnifier):
        """Test merging empty schema list raises error"""
        with pytest.raises(ValueError, match="No schemas provided"):
            schema_unifier.merge_schemas([], "empty")

    def test_merge_schemas_deduplicates_required(self):
        """Test merging removes duplicate required fields"""
        registry = SchemaRegistry()
        unifier = SchemaUnifier(registry)

        schema1 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema1",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {"common": {"type": "string"}},
                "required": ["common"],
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
                "properties": {"common": {"type": "string"}},
                "required": ["common"],
            },
        )

        merged = unifier.merge_schemas([schema1, schema2], "merged_dedup")

        # Check that 'common' appears only once in required
        assert merged.schema_def["required"].count("common") == 1

    def test_discover_schemas_exact_match(self):
        """Test discovering schemas with exact field match"""
        registry = SchemaRegistry()

        schema_def = SchemaDefinition(
            metadata=SchemaMetadata(
                name="exact_match",
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
                "required": ["title"],
            },
        )
        registry.register_schema(schema_def)

        unifier = SchemaUnifier(registry)
        data = {"title": "Test", "description": "Test description"}

        matches = unifier.discover_schemas(data)

        assert len(matches) > 0
        assert matches[0][0].metadata.name == "exact_match"
        assert matches[0][1] > 0  # Has confidence score

    def test_discover_schemas_partial_match(self):
        """Test discovering schemas with partial field match"""
        registry = SchemaRegistry()

        schema_def = SchemaDefinition(
            metadata=SchemaMetadata(
                name="partial_match",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "author": {"type": "string"},
                },
                "required": ["title"],
            },
        )
        registry.register_schema(schema_def)

        unifier = SchemaUnifier(registry)
        data = {"title": "Test"}  # Missing description and author

        matches = unifier.discover_schemas(data)

        assert len(matches) > 0
        assert 0 < matches[0][1] < 1.0  # Partial confidence score

    def test_discover_schemas_sorted_by_confidence(self):
        """Test that discovered schemas are sorted by confidence"""
        registry = SchemaRegistry()

        # Schema with more matching fields
        schema1 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="better_match",
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
                "required": ["name"],
            },
        )

        # Schema with fewer matching fields
        schema2 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="worse_match",
                version="1.0.0",
                format=SchemaFormat.FORCE_TOOL,
                namespace=SchemaNamespace.FORCE,
            ),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "number"},
                    "extra": {"type": "string"},
                    "another": {"type": "boolean"},
                },
                "required": ["name"],
            },
        )

        registry.register_schema(schema1)
        registry.register_schema(schema2)

        unifier = SchemaUnifier(registry)
        data = {"name": "Test", "value": 42}

        matches = unifier.discover_schemas(data)

        assert len(matches) == 2
        # First match should have higher confidence
        assert matches[0][1] >= matches[1][1]

    def test_discover_schemas_no_match(self, schema_unifier: SchemaUnifier):
        """Test discovering schemas with no matching fields"""
        data = {"completely": "different", "fields": "here"}
        matches = schema_unifier.discover_schemas(data)
        # May have low-score matches or no matches depending on registered schemas
        # Just verify it doesn't crash and returns a list
        assert isinstance(matches, list)

    def test_calculate_match_score_perfect(self, schema_unifier: SchemaUnifier):
        """Test match score calculation for perfect match"""
        schema_def = SchemaDefinition(
            metadata=SchemaMetadata(
                name="test",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )

        data = {"name": "Perfect Match"}
        score = schema_unifier._calculate_match_score(data, schema_def)

        assert score == 1.0

    def test_calculate_match_score_partial(self, schema_unifier: SchemaUnifier):
        """Test match score calculation for partial match"""
        schema_def = SchemaDefinition(
            metadata=SchemaMetadata(
                name="test",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name"],
            },
        )

        data = {"name": "Partial Match"}  # Missing description
        score = schema_unifier._calculate_match_score(data, schema_def)

        assert 0 < score < 1.0

    def test_calculate_match_score_no_properties(self, schema_unifier: SchemaUnifier):
        """Test match score for schema without properties"""
        schema_def = SchemaDefinition(
            metadata=SchemaMetadata(
                name="test",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={"type": "object"},  # No properties defined
        )

        data = {"any": "data"}
        score = schema_unifier._calculate_match_score(data, schema_def)

        assert score == 0.0


class TestDefaultConversionRules:
    """Tests for default conversion rules"""

    def test_create_default_rules(self):
        """Test creating default conversion rules"""
        rules = create_default_conversion_rules()

        assert len(rules) > 0
        assert all(isinstance(rule, ConversionRule) for rule in rules)

    def test_default_rules_idfw_to_unified(self):
        """Test IDFW Document to Unified Workflow rule exists"""
        rules = create_default_conversion_rules()

        idfw_rule = next(
            (r for r in rules
             if r.source_format == SchemaFormat.IDFW_DOCUMENT
             and r.target_format == SchemaFormat.UNIFIED_WORKFLOW),
            None,
        )

        assert idfw_rule is not None
        assert "title" in idfw_rule.field_mappings
        assert idfw_rule.field_mappings["title"] == "name"

    def test_default_rules_force_to_unified(self):
        """Test FORCE Tool to Unified Command rule exists"""
        rules = create_default_conversion_rules()

        force_rule = next(
            (r for r in rules
             if r.source_format == SchemaFormat.FORCE_TOOL
             and r.target_format == SchemaFormat.UNIFIED_COMMAND),
            None,
        )

        assert force_rule is not None
        assert "name" in force_rule.field_mappings
        assert force_rule.transformations.get("command_name") == "lowercase"

    def test_default_rules_idfw_project_to_unified(self):
        """Test IDFW Project to Unified Workflow rule exists"""
        rules = create_default_conversion_rules()

        project_rule = next(
            (r for r in rules
             if r.source_format == SchemaFormat.IDFW_PROJECT
             and r.target_format == SchemaFormat.UNIFIED_WORKFLOW),
            None,
        )

        assert project_rule is not None
        assert "tasks" in project_rule.field_mappings
        assert project_rule.field_mappings["tasks"] == "steps"


class TestInitializeSchemabridge:
    """Tests for initialize_schema_bridge function"""

    def test_initialize_without_schema_dir(self):
        """Test initializing schema bridge without directory"""
        unifier = initialize_schema_bridge()

        assert isinstance(unifier, SchemaUnifier)
        assert isinstance(unifier.registry, SchemaRegistry)
        # Should have default conversion rules
        assert len(unifier.registry.conversion_rules) > 0

    def test_initialize_with_nonexistent_dir(self, tmp_path: Path):
        """Test initializing with nonexistent directory"""
        nonexistent = tmp_path / "nonexistent"
        unifier = initialize_schema_bridge(nonexistent)

        assert isinstance(unifier, SchemaUnifier)
        # Should still have default conversion rules
        assert len(unifier.registry.conversion_rules) > 0

    def test_default_rules_registered(self):
        """Test that default conversion rules are registered"""
        unifier = initialize_schema_bridge()

        # Check for IDFW Document -> Unified Workflow rule
        rule = unifier.registry.get_conversion_rule(
            SchemaFormat.IDFW_DOCUMENT,
            SchemaFormat.UNIFIED_WORKFLOW,
        )
        assert rule is not None

        # Check for FORCE Tool -> Unified Command rule
        rule = unifier.registry.get_conversion_rule(
            SchemaFormat.FORCE_TOOL,
            SchemaFormat.UNIFIED_COMMAND,
        )
        assert rule is not None


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_full_conversion_workflow(self):
        """Test complete conversion workflow from registration to conversion"""
        # Initialize
        unifier = initialize_schema_bridge()

        # Register source schema
        source_schema = SchemaDefinition(
            metadata=SchemaMetadata(
                name="source_doc",
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
                "required": ["title"],
            },
        )
        unifier.registry.register_schema(source_schema)

        # Validate source data
        source_data = {"title": "Test Document", "description": "Test description"}
        is_valid, error = unifier.validate(
            source_data,
            source_schema.metadata.namespace.value,
            source_schema.metadata.name,
        )
        assert is_valid, f"Validation failed: {error}"

        # Convert data
        converted = unifier.convert(
            source_data,
            SchemaFormat.IDFW_DOCUMENT,
            SchemaFormat.UNIFIED_WORKFLOW,
        )

        # Verify conversion
        assert "name" in converted
        assert converted["name"] == "Test Document"
        assert "version" in converted  # From defaults

    def test_schema_discovery_and_conversion(self):
        """Test discovering schema and then converting"""
        unifier = initialize_schema_bridge()

        # Register test schema
        schema_def = SchemaDefinition(
            metadata=SchemaMetadata(
                name="discoverable",
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
                },
                "required": ["title"],
            },
        )
        unifier.registry.register_schema(schema_def)

        # Discover matching schemas
        data = {
            "title": "Discoverable Document",
            "description": "For discovery",
            "variables": {"key": "value"},
        }
        matches = unifier.discover_schemas(data)

        assert len(matches) > 0
        best_match = matches[0][0]

        # Verify we can validate against discovered schema
        is_valid, _ = unifier.validate(
            data,
            best_match.metadata.namespace,
            best_match.metadata.name,
        )
        assert is_valid

    def test_merge_and_validate(self):
        """Test merging schemas and validating against merged schema"""
        unifier = initialize_schema_bridge()

        # Create schemas to merge
        schema1 = SchemaDefinition(
            metadata=SchemaMetadata(
                name="schema1",
                version="1.0.0",
                format=SchemaFormat.IDFW_DOCUMENT,
                namespace=SchemaNamespace.IDFW,
            ),
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
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
                "properties": {"version": {"type": "string"}},
                "required": ["version"],
            },
        )

        # Merge schemas
        merged = unifier.merge_schemas([schema1, schema2], "merged")

        # Register merged schema
        unifier.registry.register_schema(merged)

        # Validate data against merged schema
        data = {"name": "Test", "version": "1.0.0"}
        is_valid, _ = unifier.validate(
            data,
            merged.metadata.namespace,
            merged.metadata.name,
        )
        assert is_valid

        # Validate incomplete data
        incomplete_data = {"name": "Test"}  # Missing version
        is_valid, error = unifier.validate(
            incomplete_data,
            merged.metadata.namespace,
            merged.metadata.name,
        )
        assert is_valid is False