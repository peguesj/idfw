"""
Schema Bridge for IDFWU Unified Framework
Linear Project: 4d649a6501f7

This module provides schema bridging functionality between IDFW and FORCE schemas.
Includes conversion functions, validation, and schema registry.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

import jsonschema
import yaml
from pydantic import BaseModel, Field, ConfigDict, field_validator

# Configure logging
logger = logging.getLogger(__name__)

# Import converters if available (after logger is defined)
try:
    from .converters import (
        IDFWToFORCEConverter,
        FORCEToIDFWConverter,
        BidirectionalConverter
    )
    CONVERTERS_AVAILABLE = True
except ImportError:
    CONVERTERS_AVAILABLE = False
    logger.warning("Converters module not available")


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
            namespace: Schema namespace (string or enum)
            name: Schema name

        Returns:
            Schema definition or None if not found
        """
        namespace_value = namespace.value if hasattr(namespace, 'value') else namespace
        key = f"{namespace_value}:{name}"
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
        
        # Initialize converters if available
        self.bidirectional_converter = None
        if CONVERTERS_AVAILABLE:
            self.bidirectional_converter = BidirectionalConverter()
            logger.info("Initialized schema unifier with converters")
        else:
            logger.info("Initialized schema unifier without converters")

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
    
    def convert_idfw_to_force(self, idfw_data: Dict[str, Any]) -> Optional[Any]:
        """
        Convert IDFW document to FORCE tool using bidirectional converter
        
        Args:
            idfw_data: IDFW document data
            
        Returns:
            FORCETool object or None if converters not available
        """
        if not self.bidirectional_converter:
            logger.warning("Bidirectional converter not available")
            return None
        
        try:
            return self.bidirectional_converter.convert(idfw_data, "idfw", "force")
        except Exception as e:
            logger.error(f"Error converting IDFW to FORCE: {e}")
            return None
    
    def convert_force_to_idfw(self, force_data: Union[Dict[str, Any], Any]) -> Optional[Dict[str, Any]]:
        """
        Convert FORCE tool to IDFW document using bidirectional converter
        
        Args:
            force_data: FORCE tool data or FORCETool object
            
        Returns:
            IDFW document dict or None if converters not available
        """
        if not self.bidirectional_converter:
            logger.warning("Bidirectional converter not available")
            return None
        
        try:
            return self.bidirectional_converter.convert(force_data, "force", "idfw")
        except Exception as e:
            logger.error(f"Error converting FORCE to IDFW: {e}")
            return None
    
    def validate_conversion_round_trip(
        self, 
        data: Union[Dict[str, Any], Any],
        source_format: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that data can be converted and converted back without loss
        
        Args:
            data: Source data
            source_format: Source format ("idfw" or "force")
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.bidirectional_converter:
            return False, "Bidirectional converter not available"
        
        try:
            return self.bidirectional_converter.validate_round_trip(data, source_format)
        except Exception as e:
            return False, f"Round-trip validation failed: {e}"
    
    def get_converter_stats(self) -> Optional[str]:
        """
        Get converter statistics report
        
        Returns:
            Statistics report string or None if converters not available
        """
        if not self.bidirectional_converter:
            return None
        
        return self.bidirectional_converter.get_conversion_report()


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


class IDFWDocumentParser:
    """
    Parser for IDFW document schemas
    Handles all IDFW document types (documentation, diagrams, variables, projects)
    """

    # IDFW Schema draft version
    IDFW_SCHEMA_VERSION = "http://json-schema.org/draft/2020-12/schema"
    
    # IDFW document types
    DOCUMENT_TYPES = {
        "documentation": "IDDA",
        "diagram": "IDDG", 
        "variable": "IDFV",
        "project": "IDPJ",
        "generator": "IDPG",
        "config": "IDPC"
    }

    def __init__(self, registry: Optional[SchemaRegistry] = None):
        """
        Initialize IDFW Document Parser
        
        Args:
            registry: Optional schema registry for storing parsed schemas
        """
        self.registry = registry or SchemaRegistry()
        self._init_idfw_schemas()
        logger.info("Initialized IDFW Document Parser")

    def _init_idfw_schemas(self) -> None:
        """Initialize built-in IDFW schema definitions"""
        # Base IDFW document schema
        base_schema = {
            "$schema": self.IDFW_SCHEMA_VERSION,
            "$id": "https://idfw.unified/schemas/document.json",
            "type": "object",
            "properties": {
                "docId": {"type": "string"},
                "title": {"type": "string"},
                "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                "revision": {"type": "string"},
                "description": {"type": "string"},
                "variables": {
                    "type": "object",
                    "properties": {
                        "immutable": {"type": "object"},
                        "mutable": {"type": "object"}
                    }
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                        "author": {"type": "string"},
                        "status": {"type": "string", "enum": ["draft", "review", "approved", "published"]}
                    }
                },
                "references": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "taskId": {"type": "string"},
                            "name": {"type": "string"},
                            "params": {"type": "object"}
                        },
                        "required": ["taskId", "name"]
                    }
                }
            },
            "required": ["title", "version"]
        }
        
        # Register base schema
        metadata = SchemaMetadata(
            name="idfw_document_base",
            version="2.1.1",
            format=SchemaFormat.IDFW_DOCUMENT,
            namespace=SchemaNamespace.IDFW,
            description="Base IDFW document schema",
            tags=["idfw", "document", "base"]
        )
        
        schema_def = SchemaDefinition(
            metadata=metadata,
            schema=base_schema
        )
        
        self.registry.register_schema(schema_def)

    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse an IDFW document from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed document data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
            
        logger.debug(f"Parsed IDFW document from {file_path}")
        return data

    def validate(self, data: Dict[str, Any], document_type: str = "base") -> tuple[bool, Optional[str]]:
        """
        Validate IDFW document against schema
        
        Args:
            data: Document data to validate
            document_type: Type of IDFW document (base, documentation, diagram, etc.)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        schema_name = f"idfw_document_{document_type}"
        schema_def = self.registry.get_schema("idfw", schema_name)
        
        if not schema_def:
            # Try base schema if specific type not found
            schema_def = self.registry.get_schema("idfw", "idfw_document_base")
            
        if not schema_def:
            return False, f"Schema not found for document type: {document_type}"
            
        try:
            jsonschema.validate(instance=data, schema=schema_def.schema_def)
            return True, None
        except jsonschema.ValidationError as e:
            return False, self._format_validation_error(e)

    def _format_validation_error(self, error: jsonschema.ValidationError) -> str:
        """
        Format validation error with helpful message
        
        Args:
            error: JSONSchema validation error
            
        Returns:
            Formatted error message
        """
        path = '.'.join(str(p) for p in error.path) if error.path else 'root'
        return f"Validation error at '{path}': {error.message}"

    def detect_document_type(self, data: Dict[str, Any]) -> str:
        """
        Detect IDFW document type from data
        
        Args:
            data: Document data
            
        Returns:
            Detected document type
        """
        # Check for explicit type field
        if "docId" in data:
            doc_id = data["docId"]
            for doc_type, prefix in self.DOCUMENT_TYPES.items():
                if doc_id.startswith(prefix):
                    return doc_type
                    
        # Check for type-specific fields
        if "diagramType" in data or "typeTool" in data:
            return "diagram"
        elif "promptText" in data or "generationActions" in data:
            return "generator"
        elif "apiKeys" in data or "llmConfigs" in data:
            return "config"
        elif "projectName" in data or "tasks" in data:
            return "project"
        elif "variables" in data and isinstance(data.get("variables"), dict):
            if "immutable" in data["variables"] or "mutable" in data["variables"]:
                return "variable"
                
        return "documentation"  # Default type

    def extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from IDFW document
        
        Args:
            data: Document data
            
        Returns:
            Extracted metadata
        """
        metadata = data.get("metadata", {})
        
        # Add document-level metadata
        metadata.update({
            "title": data.get("title", "Untitled"),
            "version": data.get("version", "1.0.0"),
            "revision": data.get("revision", "_a1"),
            "document_type": self.detect_document_type(data),
            "has_variables": "variables" in data,
            "has_tasks": "tasks" in data,
            "has_references": "references" in data
        })
        
        return metadata

    def extract_variables(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and categorize variables from IDFW document
        
        Args:
            data: Document data
            
        Returns:
            Categorized variables (immutable and mutable)
        """
        variables = data.get("variables", {})
        
        # Return empty dict if no variables
        if not variables:
            return {}
        
        # Handle both flat and categorized variable structures
        if "immutable" in variables or "mutable" in variables:
            return variables
        else:
            # Auto-categorize flat variables
            categorized = {
                "immutable": {},
                "mutable": {}
            }
            
            # Common immutable variable patterns
            immutable_patterns = ["version", "id", "created", "author", "type"]
            
            for key, value in variables.items():
                if any(pattern in key.lower() for pattern in immutable_patterns):
                    categorized["immutable"][key] = value
                else:
                    categorized["mutable"][key] = value
                    
            return categorized

    def parse_nested_references(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse nested document references
        
        Args:
            data: Document data
            
        Returns:
            List of parsed references
        """
        references = data.get("references", [])
        parsed_refs = []
        
        for ref in references:
            if isinstance(ref, str):
                # Simple string reference
                parsed_refs.append({
                    "type": "document",
                    "id": ref,
                    "resolved": False
                })
            elif isinstance(ref, dict):
                # Complex reference object
                parsed_refs.append({
                    "type": ref.get("type", "document"),
                    "id": ref.get("id", ref.get("docId", "unknown")),
                    "version": ref.get("version"),
                    "resolved": ref.get("resolved", False)
                })
                
        return parsed_refs

    def parse_with_validation(self, file_path: Union[str, Path]) -> tuple[Dict[str, Any], bool, Optional[str]]:
        """
        Parse and validate IDFW document in one operation
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Tuple of (parsed_data, is_valid, error_message)
        """
        try:
            data = self.parse(file_path)
            doc_type = self.detect_document_type(data)
            is_valid, error = self.validate(data, doc_type)
            
            if is_valid:
                logger.info(f"Successfully parsed and validated IDFW {doc_type} document")
            else:
                logger.warning(f"IDFW document validation failed: {error}")
                
            return data, is_valid, error
        except Exception as e:
            logger.error(f"Failed to parse IDFW document: {e}")
            return {}, False, str(e)


def initialize_schema_bridge(schema_dir: Optional[Path] = None) -> SchemaUnifier:
    """
    Initialize schema bridge with default configuration

    Args:
        schema_dir: Optional directory containing schemas

    Returns:
        Configured SchemaUnifier instance
    """
    registry = SchemaRegistry(schema_dir)

    # Initialize IDFW parser and register its schemas
    idfw_parser = IDFWDocumentParser(registry)
    
    # Register default conversion rules
    for rule in create_default_conversion_rules():
        registry.register_conversion_rule(rule)

    unifier = SchemaUnifier(registry)

    logger.info("Schema bridge initialized with IDFW parser")
    return unifier