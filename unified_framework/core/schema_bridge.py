"""
Schema Bridge for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module provides schema bridging functionality between IDFW and FORCE schemas.
Includes conversion functions, validation, and schema registry.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

import jsonschema
import yaml
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Configure logging
logger = logging.getLogger(__name__)


class SchemaFormat(str, Enum):
    """Schema format types"""
    IDFW_DOCUMENT = "idfw_document"
    IDFW_DIAGRAM = "idfw_diagram"
    IDFW_VARIABLE = "idfw_variable"
    IDFW_PROJECT = "idfw_project"
    FORCE_TOOL = "force_tool"
    FORCE_PATTERN = "force_pattern"
    FORCE_CONSTRAINT = "force_constraint"
    FORCE_GOVERNANCE = "force_governance"
    UNIFIED_COMMAND = "unified_command"
    UNIFIED_WORKFLOW = "unified_workflow"


class SchemaNamespace(str, Enum):
    """Schema namespace organization"""
    IDFW = "idfw"
    FORCE = "force"
    UNIFIED = "unified"


class SchemaMetadata(BaseModel):
    """Metadata for schema definitions"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    version: str
    format: SchemaFormat
    namespace: SchemaNamespace
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    deprecated: bool = False
    replacement: Optional[str] = None


class SchemaDefinition(BaseModel):
    """Complete schema definition"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    metadata: SchemaMetadata
    schema_def: Dict[str, Any] = Field(alias="schema")
    examples: List[Dict[str, Any]] = Field(default_factory=list)

    @field_validator('schema_def')
    @classmethod
    def validate_json_schema(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that schema is valid JSON Schema"""
        try:
            # Basic validation - check for required fields
            if '$schema' not in v:
                v['$schema'] = 'http://json-schema.org/draft-07/schema#'
            return v
        except Exception as e:
            raise ValueError(f"Invalid JSON Schema: {e}")


class ConversionRule(BaseModel):
    """Rule for converting between schema formats"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_format: SchemaFormat
    target_format: SchemaFormat
    field_mappings: Dict[str, str]  # source_field -> target_field
    transformations: Dict[str, str] = Field(default_factory=dict)  # field -> transformation_func
    defaults: Dict[str, Any] = Field(default_factory=dict)  # field -> default_value


class SchemaRegistry:
    """
    Registry for managing schema definitions and conversions
    """

    def __init__(self, schema_dir: Optional[Path] = None) -> None:
        """
        Initialize schema registry

        Args:
            schema_dir: Directory containing schema definitions
        """
        self.schema_dir = schema_dir
        self.schemas: Dict[str, SchemaDefinition] = {}
        self.conversion_rules: List[ConversionRule] = []

        if schema_dir and schema_dir.exists():
            self._load_schemas()

        logger.info(f"Initialized schema registry with {len(self.schemas)} schemas")

    def _load_schemas(self) -> None:
        """Load schemas from directory"""
        if not self.schema_dir:
            return

        for schema_file in self.schema_dir.rglob("*.yaml"):
            try:
                with open(schema_file, 'r') as f:
                    data = yaml.safe_load(f)
                    schema_def = SchemaDefinition(**data)
                    self.register_schema(schema_def)
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")

    def register_schema(self, schema: SchemaDefinition) -> None:
        """
        Register a schema definition

        Args:
            schema: Schema to register
        """
        # Convert enum to string value (SchemaNamespace is a str enum)
        namespace_value = schema.metadata.namespace.value if hasattr(schema.metadata.namespace, 'value') else schema.metadata.namespace
        key = f"{namespace_value}:{schema.metadata.name}"
        self.schemas[key] = schema
        logger.debug(f"Registered schema: {key}")

    def get_schema(self, namespace: str, name: str) -> Optional[SchemaDefinition]:
        """
        Get a schema by namespace and name

        Args:
            namespace: Schema namespace
            name: Schema name

        Returns:
            Schema definition or None if not found
        """
        key = f"{namespace}:{name}"
        return self.schemas.get(key)

    def list_schemas(
        self,
        namespace: Optional[SchemaNamespace] = None,
        format: Optional[SchemaFormat] = None,
    ) -> List[SchemaDefinition]:
        """
        List schemas with optional filtering

        Args:
            namespace: Optional namespace filter
            format: Optional format filter

        Returns:
            List of matching schemas
        """
        schemas = list(self.schemas.values())

        if namespace:
            schemas = [s for s in schemas if s.metadata.namespace == namespace]

        if format:
            schemas = [s for s in schemas if s.metadata.format == format]

        return schemas

    def register_conversion_rule(self, rule: ConversionRule) -> None:
        """
        Register a conversion rule

        Args:
            rule: Conversion rule to register
        """
        self.conversion_rules.append(rule)
        logger.debug(
            f"Registered conversion rule: {rule.source_format} -> {rule.target_format}"
        )

    def get_conversion_rule(
        self,
        source: SchemaFormat,
        target: SchemaFormat,
    ) -> Optional[ConversionRule]:
        """
        Get conversion rule for format pair

        Args:
            source: Source format
            target: Target format

        Returns:
            Conversion rule or None if not found
        """
        for rule in self.conversion_rules:
            if rule.source_format == source and rule.target_format == target:
                return rule
        return None


class SchemaUnifier:
    """
    Main class for schema bridging and unification
    """

    def __init__(self, registry: SchemaRegistry) -> None:
        """
        Initialize schema unifier

        Args:
            registry: Schema registry
        """
        self.registry = registry
        logger.info("Initialized schema unifier")

    def validate(
        self,
        data: Dict[str, Any],
        schema_namespace: str,
        schema_name: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate data against a schema

        Args:
            data: Data to validate
            schema_namespace: Schema namespace
            schema_name: Schema name

        Returns:
            Tuple of (is_valid, error_message)
        """
        schema_def = self.registry.get_schema(schema_namespace, schema_name)

        if not schema_def:
            return False, f"Schema not found: {schema_namespace}:{schema_name}"

        try:
            jsonschema.validate(instance=data, schema=schema_def.schema_def)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)

    def convert(
        self,
        data: Dict[str, Any],
        source_format: SchemaFormat,
        target_format: SchemaFormat,
    ) -> Dict[str, Any]:
        """
        Convert data from one schema format to another

        Args:
            data: Source data
            source_format: Source schema format
            target_format: Target schema format

        Returns:
            Converted data

        Raises:
            ValueError: If conversion rule not found or conversion fails
        """
        rule = self.registry.get_conversion_rule(source_format, target_format)

        if not rule:
            raise ValueError(
                f"No conversion rule found: {source_format} -> {target_format}"
            )

        result: Dict[str, Any] = {}

        # Apply field mappings
        for source_field, target_field in rule.field_mappings.items():
            if source_field in data:
                value = data[source_field]

                # Apply transformation if defined
                if target_field in rule.transformations:
                    transform_func = rule.transformations[target_field]
                    value = self._apply_transformation(value, transform_func)

                result[target_field] = value

        # Apply defaults for missing fields
        for field, default_value in rule.defaults.items():
            if field not in result:
                result[field] = default_value

        logger.debug(f"Converted data from {source_format} to {target_format}")
        return result

    def _apply_transformation(self, value: Any, transform_func: str) -> Any:
        """
        Apply a transformation function to a value

        Args:
            value: Value to transform
            transform_func: Name of transformation function

        Returns:
            Transformed value
        """
        # Built-in transformations
        transformations = {
            "uppercase": lambda v: v.upper() if isinstance(v, str) else v,
            "lowercase": lambda v: v.lower() if isinstance(v, str) else v,
            "to_list": lambda v: [v] if not isinstance(v, list) else v,
            "to_string": lambda v: str(v),
            "to_int": lambda v: int(v),
            "to_float": lambda v: float(v),
        }

        func = transformations.get(transform_func)
        if func:
            return func(value)

        logger.warning(f"Unknown transformation: {transform_func}")
        return value

    def merge_schemas(
        self,
        schemas: List[SchemaDefinition],
        merged_name: str,
    ) -> SchemaDefinition:
        """
        Merge multiple schemas into one

        Args:
            schemas: Schemas to merge
            merged_name: Name for merged schema

        Returns:
            Merged schema definition
        """
        if not schemas:
            raise ValueError("No schemas provided for merging")

        merged_schema: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "required": [],
        }

        merged_tags: Set[str] = set()

        for schema_def in schemas:
            schema = schema_def.schema_def

            # Merge properties
            if "properties" in schema:
                merged_schema["properties"].update(schema["properties"])

            # Merge required fields
            if "required" in schema:
                merged_schema["required"].extend(schema["required"])

            # Merge tags
            merged_tags.update(schema_def.metadata.tags)

        # Remove duplicates from required
        merged_schema["required"] = list(set(merged_schema["required"]))

        metadata = SchemaMetadata(
            name=merged_name,
            version="1.0.0",
            format=SchemaFormat.UNIFIED_WORKFLOW,
            namespace=SchemaNamespace.UNIFIED,
            description=f"Merged schema from {len(schemas)} sources",
            tags=list(merged_tags),
        )

        result = SchemaDefinition(
            metadata=metadata,
            schema=merged_schema,
        )

        logger.info(f"Merged {len(schemas)} schemas into {merged_name}")
        return result

    def discover_schemas(
        self,
        data: Dict[str, Any],
    ) -> List[tuple[SchemaDefinition, float]]:
        """
        Discover which schemas match the given data

        Args:
            data: Data to match against schemas

        Returns:
            List of (schema, confidence_score) tuples
        """
        matches: List[tuple[SchemaDefinition, float]] = []

        for schema_def in self.registry.schemas.values():
            score = self._calculate_match_score(data, schema_def)
            if score > 0:
                matches.append((schema_def, score))

        # Sort by confidence score descending
        matches.sort(key=lambda x: x[1], reverse=True)

        logger.debug(f"Discovered {len(matches)} matching schemas")
        return matches

    def _calculate_match_score(
        self,
        data: Dict[str, Any],
        schema_def: SchemaDefinition,
    ) -> float:
        """
        Calculate how well data matches a schema

        Args:
            data: Data to match
            schema_def: Schema definition

        Returns:
            Match score (0.0 to 1.0)
        """
        schema = schema_def.schema_def

        if "properties" not in schema:
            return 0.0

        properties = schema["properties"]
        required_fields = set(schema.get("required", []))

        # Count matching fields
        data_fields = set(data.keys())
        schema_fields = set(properties.keys())

        matching_fields = data_fields & schema_fields

        # Calculate scores
        field_coverage = len(matching_fields) / len(schema_fields) if schema_fields else 0
        required_coverage = (
            len(matching_fields & required_fields) / len(required_fields)
            if required_fields else 1.0
        )

        # Weighted score
        score = 0.6 * field_coverage + 0.4 * required_coverage

        return score


def create_default_conversion_rules() -> List[ConversionRule]:
    """
    Create default conversion rules for common schema pairs

    Returns:
        List of conversion rules
    """
    rules = [
        # IDFW Document -> Unified Workflow
        ConversionRule(
            source_format=SchemaFormat.IDFW_DOCUMENT,
            target_format=SchemaFormat.UNIFIED_WORKFLOW,
            field_mappings={
                "title": "name",
                "description": "description",
                "variables": "parameters",
            },
            defaults={
                "version": "1.0.0",
                "type": "document_workflow",
            },
        ),

        # FORCE Tool -> Unified Command
        ConversionRule(
            source_format=SchemaFormat.FORCE_TOOL,
            target_format=SchemaFormat.UNIFIED_COMMAND,
            field_mappings={
                "name": "command_name",
                "description": "description",
                "parameters": "arguments",
            },
            transformations={
                "command_name": "lowercase",
            },
            defaults={
                "prefix": "$",
            },
        ),

        # IDFW Project -> Unified Workflow
        ConversionRule(
            source_format=SchemaFormat.IDFW_PROJECT,
            target_format=SchemaFormat.UNIFIED_WORKFLOW,
            field_mappings={
                "name": "name",
                "description": "description",
                "tasks": "steps",
            },
            defaults={
                "version": "1.0.0",
                "type": "project_workflow",
            },
        ),
    ]

    return rules


def initialize_schema_bridge(schema_dir: Optional[Path] = None) -> SchemaUnifier:
    """
    Initialize schema bridge with default configuration

    Args:
        schema_dir: Optional directory containing schemas

    Returns:
        Configured SchemaUnifier instance
    """
    registry = SchemaRegistry(schema_dir)

    # Register default conversion rules
    for rule in create_default_conversion_rules():
        registry.register_conversion_rule(rule)

    unifier = SchemaUnifier(registry)

    logger.info("Schema bridge initialized")
    return unifier