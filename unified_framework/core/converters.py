"""
Schema Converters for IDFWU Unified Framework
Linear Issues: PEG-884 (SB-003), SB-004

This module provides bidirectional conversion between IDFW and FORCE schemas.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from .force_parser import (
    FORCETool,
    FORCECategory,
    FORCEParameter,
    FORCEReturn,
    FORCEDependency,
    FORCEToolParser
)

logger = logging.getLogger(__name__)


class IDFWToFORCEConverter:
    """
    Convert IDFW documents to FORCE tools
    Linear Issue: SB-003
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize IDFW to FORCE converter
        
        Args:
            strict_mode: If True, raise errors on conversion issues
        """
        self.strict_mode = strict_mode
        self.stats = {
            "documents_converted": 0,
            "parameters_created": 0,
            "dependencies_created": 0,
            "conversion_errors": 0
        }
        logger.info(f"Initialized IDFW to FORCE converter (strict={strict_mode})")
    
    def convert_document(self, idfw_doc: Dict[str, Any]) -> FORCETool:
        """
        Convert IDFW document to FORCE tool
        
        Args:
            idfw_doc: IDFW document data
            
        Returns:
            Converted FORCETool object
            
        Raises:
            ValueError: If conversion fails in strict mode
        """
        self.stats["documents_converted"] += 1
        
        try:
            # Validate required fields in strict mode
            if self.strict_mode:
                if not idfw_doc.get("title") or not idfw_doc.get("version"):
                    raise ValueError("Missing required fields: title and version")
            
            # Extract IDFW fields
            doc_id = idfw_doc.get("docId") or idfw_doc.get("diagId") or idfw_doc.get("title", "unknown")
            title = idfw_doc.get("title", "Untitled")
            description = idfw_doc.get("description", "")
            version = idfw_doc.get("version", "1.0.0")
            
            # Determine FORCE category from IDFW document type
            category = self._determine_category(idfw_doc)
            
            # Convert variables to parameters
            parameters = self._convert_variables_to_parameters(idfw_doc.get("variables", {}))
            
            # Extract tasks as dependencies
            dependencies = self._convert_tasks_to_dependencies(idfw_doc.get("tasks", []))
            
            # Create FORCE tool
            force_tool = FORCETool(
                tool_id=self._generate_tool_id(doc_id),
                name=title,
                category=category,
                version=version,
                description=description,
                command=self._generate_yung_command(title),
                parameters=parameters,
                returns=self._generate_return_spec(idfw_doc),
                dependencies=dependencies,
                variants=self._extract_variants(idfw_doc),
                protocols=self._extract_protocols(idfw_doc),
                metadata=self._convert_metadata(idfw_doc)
            )
            
            # Update stats
            self.stats["parameters_created"] += len(force_tool.parameters)
            self.stats["dependencies_created"] += len(force_tool.dependencies)
            logger.debug(f"Successfully converted IDFW document '{doc_id}' to FORCE tool")
            return force_tool
            
        except Exception as e:
            self.stats["conversion_errors"] += 1
            error_msg = f"Failed to convert IDFW document: {e}"
            
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                self.stats["conversion_errors"] += 1
                logger.warning(error_msg)
                
                # Return minimal tool in lenient/default mode
                return FORCETool(
                    tool_id=f"error_{self.stats['documents_converted']}",
                    name="Conversion Error",
                    category=FORCECategory.TOOL,
                    description=error_msg
                )
    
    def _determine_category(self, idfw_doc: Dict[str, Any]) -> FORCECategory:
        """Determine FORCE category from IDFW document type"""
        doc_id = idfw_doc.get("docId", "") or idfw_doc.get("diagId", "")
        
        # Check for specific document fields first
        if "diagramType" in idfw_doc or "diagId" in idfw_doc:
            return FORCECategory.PATTERN  # Diagrams map to patterns
        elif "projectName" in idfw_doc:
            return FORCECategory.WORKFLOW  # Projects map to workflows
        elif "promptText" in idfw_doc or "generatorLibId" in idfw_doc:
            return FORCECategory.TRANSFORMATION  # Generators map to transformations
        elif "apiKeys" in idfw_doc or "llmConfigs" in idfw_doc:
            return FORCECategory.CONSTRAINT  # Config maps to constraints
        elif ("variables" in idfw_doc and 
              isinstance(idfw_doc.get("variables"), dict) and
              ("immutable" in idfw_doc["variables"] or "mutable" in idfw_doc["variables"])):
            return FORCECategory.VALIDATION  # Variables map to validation
        
        # Check document ID prefix as fallback
        if doc_id.startswith("IDDG"):
            return FORCECategory.PATTERN
        elif doc_id.startswith("IDPJ"):
            return FORCECategory.WORKFLOW
        elif doc_id.startswith("IDPG"):
            return FORCECategory.TRANSFORMATION
        elif doc_id.startswith("IDPC"):
            return FORCECategory.CONSTRAINT
        elif doc_id.startswith("IDFV"):
            return FORCECategory.VALIDATION
        
        return FORCECategory.TOOL  # Default
    
    def _convert_variables_to_parameters(self, variables: Dict[str, Any]) -> List[FORCEParameter]:
        """Convert IDFW variables to FORCE parameters"""
        parameters = []
        
        # Handle both flat and categorized variables
        if "immutable" in variables or "mutable" in variables:
            # Categorized variables
            for var_name, var_value in variables.get("immutable", {}).items():
                parameters.append(FORCEParameter(
                    name=var_name,
                    type=self._infer_type(var_value),
                    required=True,
                    default=var_value,
                    description=f"Immutable variable: {var_name}"
                ))
            
            for var_name, var_value in variables.get("mutable", {}).items():
                parameters.append(FORCEParameter(
                    name=var_name,
                    type=self._infer_type(var_value),
                    required=False,
                    default=var_value,
                    description=f"Mutable variable: {var_name}"
                ))
        else:
            # Flat variables
            for var_name, var_value in variables.items():
                parameters.append(FORCEParameter(
                    name=var_name,
                    type=self._infer_type(var_value),
                    required=False,
                    default=var_value,
                    description=f"Variable: {var_name}"
                ))
        
        return parameters
    
    def _infer_type(self, value: Any) -> str:
        """Infer parameter type from value"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "any"
    
    def _convert_tasks_to_dependencies(self, tasks: List[Dict[str, Any]]) -> List[FORCEDependency]:
        """Convert IDFW tasks to FORCE dependencies"""
        dependencies = []
        
        for task in tasks:
            task_id = task.get("taskId", task.get("name", "unknown"))
            dependencies.append(FORCEDependency(
                tool_id=f"task_{task_id}",
                required=task.get("required", True)
            ))
        
        return dependencies
    
    def _generate_tool_id(self, doc_id: str) -> str:
        """Generate FORCE tool ID from IDFW document ID"""
        # Keep the original doc_id if it exists
        if doc_id:
            return doc_id
        # Generate new ID if needed
        return f"force_tool_{uuid.uuid4().hex[:8]}"
    
    def _generate_yung_command(self, title: str) -> str:
        """Generate YUNG command from title"""
        # Convert title to command format
        cmd = title.lower().replace(" ", "_").replace("-", "_")
        return f"${cmd}"
    
    def _generate_return_spec(self, idfw_doc: Dict[str, Any]) -> Optional[FORCEReturn]:
        """Generate return specification from IDFW document"""
        # Check if document produces output
        if "output" in idfw_doc or "returns" in idfw_doc:
            return FORCEReturn(
                type="object",
                description="Document output"
            )
        elif "diagrams" in idfw_doc:
            return FORCEReturn(
                type="string",
                description="Generated diagram"
            )
        
        return None
    
    def _extract_variants(self, idfw_doc: Dict[str, Any]) -> List[str]:
        """Extract variants from IDFW document"""
        variants = []
        
        # Check for explicit variants
        if "variants" in idfw_doc:
            variants.extend(idfw_doc["variants"])
        
        # Check for related documents
        if "references" in idfw_doc:
            for ref in idfw_doc["references"]:
                if isinstance(ref, str):
                    variants.append(ref)
        
        return variants
    
    def _extract_protocols(self, idfw_doc: Dict[str, Any]) -> List[str]:
        """Extract protocols from IDFW document"""
        protocols = []
        
        # Map IDFW types to protocols
        doc_id = idfw_doc.get("docId", "")
        if doc_id.startswith("IDDG"):
            protocols.append("visualization")
        elif doc_id.startswith("IDPJ"):
            protocols.append("project_management")
        elif doc_id.startswith("IDPG"):
            protocols.append("generation")
        
        # Check for explicit protocols
        if "protocols" in idfw_doc:
            protocols.extend(idfw_doc["protocols"])
        
        return protocols
    
    def _convert_metadata(self, idfw_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert IDFW metadata to FORCE metadata"""
        metadata = {}
        
        # Copy standard metadata fields
        if "metadata" in idfw_doc:
            idfw_meta = idfw_doc["metadata"]
            metadata.update({
                "created_at": idfw_meta.get("created_at"),
                "updated_at": idfw_meta.get("updated_at"),
                "author": idfw_meta.get("author"),
                "status": idfw_meta.get("status"),
                "source": "idfw"
            })
        
        # Add document-specific metadata
        metadata["original_doc_id"] = idfw_doc.get("docId")
        metadata["original_version"] = idfw_doc.get("version")
        metadata["original_revision"] = idfw_doc.get("revision")
        
        return metadata
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        return self.stats.copy()
    
    def _detect_parameter_type(self, value: Any) -> str:
        """Detect parameter type from value for testing"""
        if isinstance(value, str) and value.isdigit():
            return "integer"
        return self._infer_type(value)
    
    def _map_idfw_to_force_category(self, doc_type: str) -> FORCECategory:
        """Map IDFW document type to FORCE category"""
        mapping = {
            "documentation": FORCECategory.TOOL,
            "diagram": FORCECategory.PATTERN,
            "project": FORCECategory.WORKFLOW,
            "generator": FORCECategory.TRANSFORMATION,
            "config": FORCECategory.CONSTRAINT,
            "variable": FORCECategory.VALIDATION
        }
        return mapping.get(doc_type, FORCECategory.TOOL)


class FORCEToIDFWConverter:
    """
    Convert FORCE tools to IDFW documents
    Linear Issue: SB-004
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize FORCE to IDFW converter
        
        Args:
            strict_mode: If True, raise errors on conversion issues
        """
        self.strict_mode = strict_mode
        self.stats = {
            "tools_converted": 0,
            "variables_created": 0,
            "references_created": 0,
            "conversion_errors": 0
        }
        logger.info(f"Initialized FORCE to IDFW converter (strict={strict_mode})")
    
    def convert_tool(self, force_tool: Union[FORCETool, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert FORCE tool to IDFW document
        
        Args:
            force_tool: FORCE tool (object or dict)
            
        Returns:
            IDFW document dictionary
            
        Raises:
            ValueError: If conversion fails in strict mode
        """
        self.stats["tools_converted"] += 1
        
        try:
            # Convert to dict if needed
            if isinstance(force_tool, FORCETool):
                tool_data = {
                    "tool_id": force_tool.tool_id,
                    "name": force_tool.name,
                    "category": force_tool.category,
                    "version": force_tool.version,
                    "description": force_tool.description,
                    "command": force_tool.command,
                    "parameters": force_tool.parameters,
                    "returns": force_tool.returns,
                    "dependencies": force_tool.dependencies,
                    "variants": force_tool.variants,
                    "protocols": force_tool.protocols,
                    "metadata": force_tool.metadata
                }
            else:
                tool_data = force_tool
            
            # Validate required fields in strict mode
            if self.strict_mode:
                if not tool_data.get("tool_id"):
                    raise ValueError("Invalid FORCE tool: missing tool_id")
            
            # Create IDFW document
            idfw_doc = {
                "docId": tool_data.get("tool_id", f"force_{uuid.uuid4().hex[:8]}"),
                "title": tool_data.get("name", "Untitled"),
                "version": tool_data.get("version", "1.0.0"),
                "revision": "_a1",
                "description": tool_data.get("description", ""),
                "variables": self._convert_parameters_to_variables(tool_data.get("parameters", [])),
                "metadata": self._convert_metadata(tool_data),
                "references": self._convert_dependencies_to_references(tool_data.get("dependencies", [])),
                "tasks": self._generate_tasks(tool_data)
            }
            
            # Add type-specific fields
            self._add_type_specific_fields(idfw_doc, tool_data)
            
            # Update stats
            params = tool_data.get("parameters", [])
            deps = tool_data.get("dependencies", [])
            self.stats["variables_created"] += len(params)
            self.stats["references_created"] += len(deps)
            logger.debug(f"Successfully converted FORCE tool '{tool_data.get('tool_id')}' to IDFW document")
            return idfw_doc
            
        except Exception as e:
            self.stats["conversion_errors"] += 1
            error_msg = f"Failed to convert FORCE tool: {e}"
            
            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                self.stats["conversion_errors"] += 1
                logger.warning(error_msg)
                
                # Return minimal document in lenient/default mode
                return {
                    "docId": f"ERROR-{self.stats['tools_converted']}",
                    "title": "Conversion Error",
                    "version": "1.0.0",
                    "description": error_msg
                }
    
    def _generate_doc_id(self, tool_data: Dict[str, Any]) -> str:
        """Generate IDFW document ID from FORCE tool"""
        tool_id = tool_data.get("tool_id", "unknown")
        category = tool_data.get("category", FORCECategory.TOOL)
        
        # Map category to IDFW prefix
        prefix_map = {
            FORCECategory.WORKFLOW: "IDDG",
            FORCECategory.INTEGRATION: "IDPJ",
            FORCECategory.TRANSFORMATION: "IDPG",
            FORCECategory.GOVERNANCE: "IDPC",
            FORCECategory.VALIDATION: "IDFV",
            FORCECategory.CONSTRAINT: "IDDA",
            FORCECategory.PATTERN: "IDDA",
            FORCECategory.PROTOCOL: "IDDA",
            FORCECategory.TOOL: "IDDA",
            FORCECategory.VARIANT: "IDDA"
        }
        
        # Get category value
        if hasattr(category, "value"):
            category_val = category
        else:
            try:
                category_val = FORCECategory(category)
            except:
                category_val = FORCECategory.TOOL
        
        prefix = prefix_map.get(category_val, "IDDA")
        
        # Extract numeric part from tool_id if present
        import re
        match = re.search(r'\d+', tool_id)
        num = match.group() if match else "001"
        
        return f"{prefix}-{num}"
    
    def _convert_parameters_to_variables(self, parameters: List[Any]) -> Dict[str, Any]:
        """Convert FORCE parameters to IDFW variables"""
        variables = {
            "immutable": {},
            "mutable": {}
        }
        
        for param in parameters:
            # Handle both dict and object parameters
            if hasattr(param, "name"):
                name = param.name
                required = param.required
                default = param.default
            else:
                name = param.get("name", "unknown")
                required = param.get("required", False)
                default = param.get("default")
            
            # Place in appropriate category
            if required:
                variables["immutable"][name] = default if default is not None else ""
            else:
                variables["mutable"][name] = default if default is not None else ""
        
        # Clean up empty categories
        if not variables["immutable"]:
            del variables["immutable"]
        if not variables["mutable"]:
            del variables["mutable"]
        
        return variables
    
    def _convert_metadata(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert FORCE metadata to IDFW metadata"""
        metadata = {}
        
        # Get FORCE metadata
        force_meta = tool_data.get("metadata", {})
        
        # Map standard fields
        metadata["created_at"] = force_meta.get("created_at", datetime.now().isoformat())
        metadata["updated_at"] = force_meta.get("updated_at", datetime.now().isoformat())
        metadata["author"] = force_meta.get("author", "unknown")
        metadata["status"] = force_meta.get("status", "draft")
        
        # Add conversion metadata
        metadata["source"] = "force"
        metadata["original_tool_id"] = tool_data.get("tool_id")
        metadata["original_category"] = str(tool_data.get("category", ""))
        
        return metadata
    
    def _convert_dependencies_to_references(self, dependencies: List[Any]) -> List[str]:
        """Convert FORCE dependencies to IDFW references"""
        references = []
        
        for dep in dependencies:
            # Handle both dict and object dependencies
            if hasattr(dep, "tool_id"):
                references.append(dep.tool_id)
            else:
                references.append(dep.get("tool_id", "unknown"))
        
        return references
    
    def _generate_tasks(self, tool_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate IDFW tasks from FORCE tool"""
        tasks = []
        
        # Create task from command if present
        command = tool_data.get("command")
        if command:
            tasks.append({
                "taskId": "cmd-001",
                "name": f"Execute {command}",
                "params": {
                    "command": command,
                    "tool_id": tool_data.get("tool_id")
                }
            })
        
        # Add tasks for variants
        for i, variant in enumerate(tool_data.get("variants", [])):
            tasks.append({
                "taskId": f"variant-{i+1:03d}",
                "name": f"Process variant {variant}",
                "params": {"variant": variant}
            })
        
        return tasks
    
    def _add_type_specific_fields(self, idfw_doc: Dict[str, Any], tool_data: Dict[str, Any]) -> None:
        """Add type-specific fields based on FORCE category"""
        category = tool_data.get("category", FORCECategory.TOOL)
        
        # Get category value
        if hasattr(category, "value"):
            category_val = category
        else:
            try:
                category_val = FORCECategory(category)
            except:
                category_val = FORCECategory.TOOL
        
        # Add category-specific fields
        if category_val == FORCECategory.WORKFLOW:
            idfw_doc["diagramType"] = "workflow"
            idfw_doc["typeTool"] = "force"
        elif category_val == FORCECategory.TRANSFORMATION:
            idfw_doc["promptText"] = f"Transform using {tool_data.get('name', 'tool')}"
            idfw_doc["generationActions"] = ["transform"]
        elif category_val == FORCECategory.GOVERNANCE:
            idfw_doc["apiKeys"] = {}
            idfw_doc["llmConfigs"] = {}
        elif category_val == FORCECategory.INTEGRATION:
            idfw_doc["projectName"] = tool_data.get("name", "Integration Project")
        elif category_val == FORCECategory.VALIDATION:
            idfw_doc["variables"]["validation_rules"] = tool_data.get("protocols", [])
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        return self.stats.copy()
    
    def _generate_idfw_doc_id(self, tool_id: Optional[str], doc_type: str) -> str:
        """Generate IDFW document ID"""
        if tool_id:
            return tool_id
        
        # Generate ID based on document type
        prefixes = {
            "documentation": "IDDA",
            "diagram": "IDDG",
            "variable": "IDFV",
            "project": "IDPJ",
            "generator": "IDPG",
            "config": "IDPC"
        }
        prefix = prefixes.get(doc_type, "IDDA")
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
    
    def _map_force_to_idfw_type(self, category: FORCECategory) -> str:
        """Map FORCE category to IDFW document type"""
        mapping = {
            FORCECategory.TOOL: "documentation",
            FORCECategory.PATTERN: "diagram",
            FORCECategory.WORKFLOW: "project",
            FORCECategory.TRANSFORMATION: "generator",
            FORCECategory.CONSTRAINT: "config",
            FORCECategory.VALIDATION: "variable",
            FORCECategory.INTEGRATION: "project",
            FORCECategory.GOVERNANCE: "config",
            FORCECategory.PROTOCOL: "documentation",
            FORCECategory.VARIANT: "documentation"
        }
        return mapping.get(category, "documentation")


class BidirectionalConverter:
    """
    Provides bidirectional conversion with round-trip validation
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize bidirectional converter
        
        Args:
            strict_mode: If True, raise errors on conversion issues
        """
        self.idfw_to_force = IDFWToFORCEConverter(strict_mode)
        self.force_to_idfw = FORCEToIDFWConverter(strict_mode)
        self.round_trip_stats = {
            "successful": 0,
            "failed": 0
        }
        logger.info("Initialized bidirectional converter")
    
    def convert(self, data: Union[Dict[str, Any], FORCETool], 
                source_format: str, 
                target_format: str) -> Union[Dict[str, Any], FORCETool]:
        """
        Convert between IDFW and FORCE formats
        
        Args:
            data: Source data
            source_format: Source schema format
            target_format: Target schema format
            
        Returns:
            Converted data
            
        Raises:
            ValueError: If conversion is not supported
        """
        if source_format == target_format:
            return data
        
        if source_format == "idfw" and target_format == "force":
            return self.idfw_to_force.convert_document(data)
        elif source_format == "force" and target_format == "idfw":
            return self.force_to_idfw.convert_tool(data)
        else:
            raise ValueError(f"Invalid source format: {source_format} or target format: {target_format}")
    
    def validate_round_trip(self, data: Union[Dict[str, Any], FORCETool], 
                           source_format: str) -> tuple[bool, Optional[str]]:
        """
        Validate that data can be converted and converted back without loss
        
        Args:
            data: Source data
            source_format: Source format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Determine target format
            if source_format == "idfw":
                target_format = "force"
            else:
                target_format = "idfw"
            
            # Convert to target
            converted = self.convert(data, source_format, target_format)
            
            # Convert back to source
            round_trip = self.convert(converted, target_format, source_format)
            
            # Compare key fields
            if source_format == "idfw":
                # Check IDFW fields
                original = data
                if (original.get("title") == round_trip.get("title") and
                    original.get("version") == round_trip.get("version") and
                    original.get("description") == round_trip.get("description")):
                    return True, None
                else:
                    return False, "Round-trip conversion lost data"
            else:
                # Check FORCE fields
                if isinstance(data, FORCETool):
                    original = data
                    if (original.name == round_trip.name and
                        original.version == round_trip.version and
                        original.description == round_trip.description):
                        self.round_trip_stats["successful"] += 1
                        return True, None
                    else:
                        self.round_trip_stats["failed"] += 1
                        return False, "Round-trip conversion lost data"
                else:
                    self.round_trip_stats["successful"] += 1
                    return True, None
            
        except Exception as e:
            return False, f"Round-trip validation failed: {e}"
    
    def convert_batch(self, documents: List[Union[Dict[str, Any], FORCETool]], 
                      source_format: str, target_format: str) -> List[Union[Dict[str, Any], FORCETool]]:
        """Convert multiple documents"""
        return [self.convert(doc, source_format, target_format) for doc in documents]
    
    def get_conversion_report(self) -> str:
        """Get conversion statistics report"""
        report = ["\n=== Conversion Statistics ==="]
        report.append("\nIDFW to FORCE Statistics:")
        for key, value in self.idfw_to_force.stats.items():
            report.append(f"  {key}: {value}")
        report.append("\nFORCE to IDFW Statistics:")
        for key, value in self.force_to_idfw.stats.items():
            report.append(f"  {key}: {value}")
        report.append("\nRound-Trip Validation:")
        report.append(f"  Successful: {self.round_trip_stats['successful']}")
        report.append(f"  Failed: {self.round_trip_stats['failed']}")
        return "\n".join(report)


def create_default_converters(strict_mode: bool = True) -> BidirectionalConverter:
    """
    Create default converter instances
    
    Args:
        strict_mode: If True, raise errors on conversion issues
        
    Returns:
        Configured BidirectionalConverter
    """
    return BidirectionalConverter(strict_mode)