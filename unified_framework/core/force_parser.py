"""
FORCE Tool Parser for IDFWU Unified Framework
Linear Issue: PEG-883 (SB-002)

This module provides parsing functionality for FORCE tool definitions.
Handles all 171 FORCE components including tools, patterns, constraints,
governance, variants, and protocols.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from .schema_bridge import (
    SchemaRegistry,
    SchemaFormat,
    SchemaNamespace,
    SchemaDefinition,
    SchemaMetadata
)


logger = logging.getLogger(__name__)


class FORCECategory(str, Enum):
    """FORCE component categories"""
    TOOL = "tool"
    PATTERN = "pattern"
    CONSTRAINT = "constraint"
    GOVERNANCE = "governance"
    VARIANT = "variant"
    PROTOCOL = "protocol"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"


class FORCEParameter(BaseModel):
    """FORCE tool parameter definition"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    type: str
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)
    

class FORCEReturn(BaseModel):
    """FORCE tool return value definition"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    type: str
    description: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None


class FORCEDependency(BaseModel):
    """FORCE tool dependency definition"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    tool_id: str
    version: Optional[str] = None
    required: bool = True
    

class FORCETool(BaseModel):
    """Complete FORCE tool definition"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    tool_id: str
    name: str
    category: FORCECategory
    version: str = "1.0.0"
    description: Optional[str] = None
    command: Optional[str] = None  # YUNG command ($prefix)
    parameters: List[FORCEParameter] = Field(default_factory=list)
    returns: Optional[FORCEReturn] = None
    dependencies: List[FORCEDependency] = Field(default_factory=list)
    variants: List[str] = Field(default_factory=list)
    protocols: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FORCEToolParser:
    """
    Parser for FORCE tool definitions
    Handles all 171 FORCE components with validation and metadata extraction
    """
    
    # YUNG command prefix
    YUNG_PREFIX = "$"
    
    # FORCE component counts (as per specification)
    COMPONENT_COUNTS = {
        "tools": 50,
        "patterns": 25,
        "constraints": 20,
        "governance": 15,
        "variants": 25,
        "protocols": 20,
        "transformations": 10,
        "validations": 6
    }
    
    def __init__(self, registry: Optional[SchemaRegistry] = None):
        """
        Initialize FORCE Tool Parser
        
        Args:
            registry: Optional schema registry for storing parsed tools
        """
        self.registry = registry or SchemaRegistry()
        self.tools: Dict[str, FORCETool] = {}
        self._init_force_schemas()
        logger.info(f"Initialized FORCE Tool Parser with {sum(self.COMPONENT_COUNTS.values())} component capacity")
    
    def _init_force_schemas(self) -> None:
        """Initialize built-in FORCE tool schemas"""
        # Base FORCE tool schema
        base_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://force.unified/schemas/tool.json",
            "type": "object",
            "properties": {
                "tool_id": {"type": "string"},
                "name": {"type": "string"},
                "category": {
                    "type": "string",
                    "enum": [c.value for c in FORCECategory]
                },
                "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                "description": {"type": "string"},
                "command": {"type": "string"},
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "required": {"type": "boolean"},
                            "default": {},
                            "description": {"type": "string"},
                            "constraints": {"type": "object"}
                        },
                        "required": ["name", "type"]
                    }
                },
                "returns": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "schema": {"type": "object"}
                    },
                    "required": ["type"]
                },
                "dependencies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tool_id": {"type": "string"},
                            "version": {"type": "string"},
                            "required": {"type": "boolean"}
                        },
                        "required": ["tool_id"]
                    }
                },
                "variants": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "protocols": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "metadata": {"type": "object"}
            },
            "required": ["tool_id", "name", "category"]
        }
        
        # Register base schema
        metadata = SchemaMetadata(
            name="force_tool_base",
            version="1.0.0",
            format=SchemaFormat.FORCE_TOOL,
            namespace=SchemaNamespace.FORCE,
            description="Base FORCE tool schema",
            tags=["force", "tool", "base"]
        )
        
        schema_def = SchemaDefinition(
            metadata=metadata,
            schema=base_schema
        )
        
        self.registry.register_schema(schema_def)
    
    def parse(self, file_path: Union[str, Path]) -> FORCETool:
        """
        Parse a FORCE tool definition from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed FORCETool object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or tool structure is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
        
        return self.parse_tool(data)
    
    def parse_tool(self, data: Dict[str, Any]) -> FORCETool:
        """
        Parse FORCE tool from dictionary data
        
        Args:
            data: Tool definition data
            
        Returns:
            Parsed FORCETool object
            
        Raises:
            ValueError: If tool structure is invalid
        """
        try:
            # Handle category as string or enum
            if "category" in data and isinstance(data["category"], str):
                try:
                    data["category"] = FORCECategory(data["category"])
                except ValueError:
                    # Default to TOOL if category is unknown
                    data["category"] = FORCECategory.TOOL
            
            # Parse parameters
            if "parameters" in data:
                params = []
                for param_data in data["parameters"]:
                    params.append(FORCEParameter(**param_data))
                data["parameters"] = params
            
            # Parse return value
            if "returns" in data and data["returns"]:
                data["returns"] = FORCEReturn(**data["returns"])
            
            # Parse dependencies
            if "dependencies" in data:
                deps = []
                for dep_data in data["dependencies"]:
                    deps.append(FORCEDependency(**dep_data))
                data["dependencies"] = deps
            
            tool = FORCETool(**data)
            
            # Store in registry
            self.tools[tool.tool_id] = tool
            
            logger.debug(f"Parsed FORCE tool: {tool.tool_id}")
            return tool
            
        except Exception as e:
            raise ValueError(f"Invalid FORCE tool structure: {e}")
    
    def validate(self, tool: Union[FORCETool, Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Validate FORCE tool against schema
        
        Args:
            tool: Tool to validate (FORCETool object or dict)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if isinstance(tool, FORCETool):
            tool_data = tool.model_dump()
            # Convert category enum to string for validation
            if "category" in tool_data:
                tool_data["category"] = tool_data["category"].value if hasattr(tool_data["category"], "value") else str(tool_data["category"])
            # Convert nested objects to dicts
            if "parameters" in tool_data:
                tool_data["parameters"] = [p if isinstance(p, dict) else p.model_dump() if hasattr(p, "model_dump") else dict(p) for p in tool_data["parameters"]]
            if "returns" in tool_data:
                if tool_data["returns"] is None:
                    # Remove None returns for validation
                    del tool_data["returns"]
                else:
                    if hasattr(tool_data["returns"], "model_dump"):
                        returns_dict = tool_data["returns"].model_dump()
                    elif isinstance(tool_data["returns"], dict):
                        returns_dict = tool_data["returns"]
                    else:
                        returns_dict = dict(tool_data["returns"])
                    # Remove None schema field if present
                    if "schema" in returns_dict and returns_dict["schema"] is None:
                        del returns_dict["schema"]
                    tool_data["returns"] = returns_dict
            if "dependencies" in tool_data:
                tool_data["dependencies"] = [d if isinstance(d, dict) else d.model_dump() if hasattr(d, "model_dump") else dict(d) for d in tool_data["dependencies"]]
        else:
            tool_data = tool
        
        # Get schema
        schema_def = self.registry.get_schema("force", "force_tool_base")
        
        if not schema_def:
            return False, "FORCE tool schema not found"
        
        # Validate against schema
        import jsonschema
        try:
            jsonschema.validate(instance=tool_data, schema=schema_def.schema_def)
            return True, None
        except jsonschema.ValidationError as e:
            return False, f"Validation error: {e.message}"
    
    def detect_category(self, data: Dict[str, Any]) -> FORCECategory:
        """
        Detect FORCE category from tool data
        
        Args:
            data: Tool data
            
        Returns:
            Detected FORCECategory
        """
        # Check explicit category field
        if "category" in data:
            try:
                return FORCECategory(data["category"])
            except ValueError:
                pass
        
        # Detect by field patterns
        if "constraints" in data and isinstance(data["constraints"], list):
            return FORCECategory.CONSTRAINT
        elif "governance_rules" in data or "compliance" in data:
            return FORCECategory.GOVERNANCE
        elif "pattern_type" in data or "template" in data:
            return FORCECategory.PATTERN
        elif "variant_of" in data:
            return FORCECategory.VARIANT
        elif "protocol_type" in data:
            return FORCECategory.PROTOCOL
        elif "transform" in data or "transformation" in data:
            return FORCECategory.TRANSFORMATION
        elif "validation_rules" in data:
            return FORCECategory.VALIDATION
        elif "workflow_steps" in data:
            return FORCECategory.WORKFLOW
        elif "integration_type" in data:
            return FORCECategory.INTEGRATION
        
        return FORCECategory.TOOL  # Default
    
    def extract_yung_command(self, tool: FORCETool) -> Optional[str]:
        """
        Extract YUNG command from tool definition
        
        Args:
            tool: FORCE tool
            
        Returns:
            YUNG command string or None
        """
        if tool.command and tool.command.startswith(self.YUNG_PREFIX):
            return tool.command
        
        # Check metadata for command
        if "yung_command" in tool.metadata:
            cmd = tool.metadata["yung_command"]
            if not cmd.startswith(self.YUNG_PREFIX):
                cmd = self.YUNG_PREFIX + cmd
            return cmd
        
        # Generate from tool name
        if tool.name:
            cmd_name = tool.name.lower().replace(" ", "_")
            return f"{self.YUNG_PREFIX}{cmd_name}"
        
        return None
    
    def extract_parameters(self, tool: FORCETool) -> Dict[str, Any]:
        """
        Extract parameter definitions from tool
        
        Args:
            tool: FORCE tool
            
        Returns:
            Dictionary of parameter definitions
        """
        params = {}
        for param in tool.parameters:
            params[param.name] = {
                "type": param.type,
                "required": param.required,
                "default": param.default,
                "description": param.description,
                "constraints": param.constraints
            }
        return params
    
    def extract_dependencies(self, tool: FORCETool) -> List[str]:
        """
        Extract tool dependencies
        
        Args:
            tool: FORCE tool
            
        Returns:
            List of dependency tool IDs
        """
        return [dep.tool_id for dep in tool.dependencies]
    
    def resolve_dependency_chain(self, tool_id: str, visited: Optional[Set[str]] = None) -> List[str]:
        """
        Resolve full dependency chain for a tool
        
        Args:
            tool_id: Tool ID to resolve
            visited: Set of already visited tools (for cycle detection)
            
        Returns:
            Ordered list of dependency tool IDs
            
        Raises:
            ValueError: If circular dependency detected
        """
        if visited is None:
            visited = set()
        
        if tool_id in visited:
            raise ValueError(f"Circular dependency detected: {tool_id}")
        
        visited.add(tool_id)
        
        if tool_id not in self.tools:
            return []
        
        tool = self.tools[tool_id]
        chain = []
        
        for dep in tool.dependencies:
            # Recursively resolve dependencies
            dep_chain = self.resolve_dependency_chain(dep.tool_id, visited.copy())
            for dep_id in dep_chain:
                if dep_id not in chain:
                    chain.append(dep_id)
            
            if dep.tool_id not in chain:
                chain.append(dep.tool_id)
        
        return chain
    
    def get_tools_by_category(self, category: FORCECategory) -> List[FORCETool]:
        """
        Get all tools of a specific category
        
        Args:
            category: Category to filter by
            
        Returns:
            List of tools in that category
        """
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def get_tool_variants(self, tool_id: str) -> List[FORCETool]:
        """
        Get all variants of a tool
        
        Args:
            tool_id: Base tool ID
            
        Returns:
            List of variant tools
        """
        variants = []
        for tool in self.tools.values():
            if tool_id in tool.variants or tool.metadata.get("variant_of") == tool_id:
                variants.append(tool)
        return variants
    
    def parse_batch(self, directory: Union[str, Path], pattern: str = "*.json") -> Dict[str, FORCETool]:
        """
        Parse multiple FORCE tool files from directory
        
        Args:
            directory: Directory containing tool files
            pattern: File pattern to match
            
        Returns:
            Dictionary of tool_id -> FORCETool
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        parsed_tools = {}
        
        for file_path in directory.glob(pattern):
            try:
                tool = self.parse(file_path)
                parsed_tools[tool.tool_id] = tool
                logger.info(f"Parsed tool: {tool.tool_id} from {file_path}")
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")
        
        return parsed_tools
    
    def export_to_schema_registry(self) -> None:
        """Export all parsed tools to the schema registry"""
        for tool in self.tools.values():
            # Create schema definition for each tool
            tool_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "$id": f"https://force.unified/tools/{tool.tool_id}.json",
                "type": "object",
                "title": tool.name,
                "description": tool.description,
                "properties": {}
            }
            
            # Add parameter schemas
            for param in tool.parameters:
                tool_schema["properties"][param.name] = {
                    "type": param.type,
                    "description": param.description
                }
                if param.default is not None:
                    tool_schema["properties"][param.name]["default"] = param.default
            
            # Create metadata
            metadata = SchemaMetadata(
                name=tool.tool_id,
                version=tool.version,
                format=SchemaFormat.FORCE_TOOL,
                namespace=SchemaNamespace.FORCE,
                description=tool.description or f"FORCE tool: {tool.name}",
                tags=["force", tool.category.value, "tool"]
            )
            
            # Register schema
            schema_def = SchemaDefinition(
                metadata=metadata,
                schema=tool_schema
            )
            
            self.registry.register_schema(schema_def)
            
        logger.info(f"Exported {len(self.tools)} tools to schema registry")